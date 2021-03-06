/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: fishlinghu@gmail.com
 *
 * This program conducts a simple experiment: It builds up a topology based on
 * either Inet or Orbis trace files. A random node is then chosen, and all the
 * other nodes will send a packet to it. The TTL is measured and reported as an histogram.
 *
 */

#include <ctime>
#include <sstream>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/ipv4-nix-vector-helper.h"
#include "ns3/topology-read-module.h"
#include "ns3/packet-sink.h"
#include <list>
#include <fstream>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("Topology Read and Throughput Testing");

static std::list < unsigned int > data;

// ----------------------------------------------------------------------
// -- main
// ----------------------------------------------
int main(int argc, char * argv[]) {

    std::string format("Orbis");
    std::string input("src/topology-read/examples/Orbis_toposample.txt");

    // Set up command line parameters used to control the experiment.
    CommandLine cmd;
    cmd.AddValue("format", "Format to use for data input [Orbis|Inet|Rocketfuel].",
        format);
    cmd.AddValue("input", "Name of the input file.",
        input);
    cmd.Parse(argc, argv);

    // ------------------------------------------------------------
    // -- Read topology data.
    // --------------------------------------------

    // Pick a topology reader based in the requested format.
    TopologyReaderHelper topoHelp;
    topoHelp.SetFileName(input);
    topoHelp.SetFileType(format);
    Ptr<TopologyReader> inFile = topoHelp.GetTopologyReader();

    NodeContainer nodes;

    if (inFile != 0) {
        nodes = inFile->Read();
    }

    if (inFile->LinksSize() == 0) {
        NS_LOG_ERROR("Problems reading the topology file. Failing.");
        return -1;
    }

    // ------------------------------------------------------------
    // -- Create nodes and network stacks
    // --------------------------------------------
    NS_LOG_INFO ("creating internet stack");
    InternetStackHelper stack;

    // Setup NixVector Routing
    Ipv4NixVectorHelper nixRouting;
    stack.SetRoutingHelper (nixRouting);  // has effect on the next Install ()
    stack.Install (nodes);

    NS_LOG_INFO ("creating ip4 addresses");
    Ipv4AddressHelper address;
    address.SetBase ("10.0.0.0", "255.255.255.252");

    int totlinks = inFile->LinksSize ();

    NS_LOG_INFO ("creating node containers");
    NodeContainer* nc = new NodeContainer[totlinks];
    TopologyReader::ConstLinksIterator iter;
    int i = 0;
    for ( iter = inFile->LinksBegin (); iter != inFile->LinksEnd (); iter++, i++ ){
        nc[i] = NodeContainer (iter->GetFromNode (), iter->GetToNode ());
    }

    NS_LOG_INFO ("creating net device containers");
    NetDeviceContainer* ndc = new NetDeviceContainer[totlinks];
    PointToPointHelper p2p;
    for (int i = 0; i < totlinks; i++){
        // p2p.SetChannelAttribute ("Delay", TimeValue(MilliSeconds(weight[i])));
        p2p.SetChannelAttribute ("Delay", StringValue ("2ms"));
        p2p.SetDeviceAttribute ("DataRate", StringValue ("0.5Mbps"));
        ndc[i] = p2p.Install (nc[i]);
    }

    // it crates little subnets, one for each couple of nodes.
    NS_LOG_INFO ("creating ipv4 interfaces");
    Ipv4InterfaceContainer* ipic = new Ipv4InterfaceContainer[totlinks];
    for (int i = 0; i < totlinks; i++){
        ipic[i] = address.Assign (ndc[i]);
        address.NewNetwork ();
    }

    // select an random number
    uint32_t totalNodes = nodes.GetN ();
    Ptr<UniformRandomVariable> unifRandom = CreateObject<UniformRandomVariable> ();
    unifRandom->SetAttribute ("Min", DoubleValue (0));
    unifRandom->SetAttribute ("Max", DoubleValue (totalNodes - 1));
    unsigned int randomServerNumber = unifRandom->GetInteger (0, totalNodes - 1);

    // select the server with index = random number
    Ptr<Node> randomServerNode = nodes.Get (randomServerNumber);
    Ptr<Ipv4> ipv4Server = randomServerNode->GetObject<Ipv4> ();
    Ipv4InterfaceAddress iaddrServer = ipv4Server->GetAddress (1,0);
    Ipv4Address ipv4AddrServer = iaddrServer.GetLocal ();

    // ------------------------------------------------------------
    // -- Send around packets to check the ttl
    // --------------------------------------------
    Config::SetDefault ("ns3::Ipv4RawSocketImpl::Protocol", StringValue ("2"));

    uint16_t port = 9;  // well-known echo port number
    BulkSendHelper source ("ns3::TcpSocketFactory",
                           InetSocketAddress (ipv4AddrServer, port));
    // Set the amount of data to send in bytes.  Zero is unlimited.
    uint32_t maxBytes = 0;
    source.SetAttribute ("MaxBytes", UintegerValue (maxBytes));

    // except the random selected server node, all other nodes are clients
    NodeContainer clientNodes;
    for ( unsigned int i = 0; i < nodes.GetN (); i++ ){
        if (i != randomServerNumber ){
            Ptr<Node> clientNode = nodes.Get (i);
            clientNodes.Add (clientNode);
        }
    }

    const double duration = 3.0;

    ApplicationContainer apps = source.Install (clientNodes);
    apps.Start (Seconds (0.0));
    apps.Stop (Seconds (duration));

    PacketSinkHelper sink = PacketSinkHelper ("ns3::TcpSocketFactory",
        InetSocketAddress (Ipv4Address::GetAny (), port)
    );
    ApplicationContainer sinkApps = sink.Install (randomServerNode);
    sinkApps.Start (Seconds (0.0));
    sinkApps.Stop (Seconds (duration));

    // 8. Install FlowMonitor on all nodes
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll ();

    // ------------------------------------------------------------
    // -- Run the simulation
    // --------------------------------------------
    NS_LOG_INFO ("Run Simulation.");
    Simulator::Stop (Seconds (3.0));
    Simulator::Run ();
    Simulator::Destroy ();
    NS_LOG_INFO ("Done.");

    // 10. Print per flow statistics
    monitor->CheckForLostPackets ();
    Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier> (flowmon.GetClassifier ());
    FlowMonitor::FlowStatsContainer stats = monitor->GetFlowStats ();
    for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin (); i != stats.end (); ++i){
        // first 2 FlowIds are for ECHO apps, we don't want to display them
        //
        // Duration for throughput measurement is 9.0 seconds, since
        //   StartTime of the OnOffApplication is at about "second 1"
        // and
        //   Simulator::Stops at "second 10".
        if (i->first > 2) {
            Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow (i->first);
            std::cout << "Flow " << i->first - 2 << " (" << t.sourceAddress << " -> " << t.destinationAddress << ")\n";
            std::cout << "  Tx Packets: " << i->second.txPackets << "\n";
            std::cout << "  Tx Bytes:   " << i->second.txBytes << "\n";
            std::cout << "  TxOffered:  " << i->second.txBytes * 8.0 / duration / 1000 / 1000  << " Mbps\n";
            std::cout << "  Rx Packets: " << i->second.rxPackets << "\n";
            std::cout << "  Rx Bytes:   " << i->second.rxBytes << "\n";
            std::cout << "  Throughput: " << i->second.rxBytes * 8.0 / duration / 1000 / 1000  << " Mbps\n";
        }
    }

    Ptr<PacketSink> sink1 = DynamicCast<PacketSink> (sinkApps.Get (0));
    std::cout << "Total Bytes Received: " << sink1->GetTotalRx () << std::endl;

    delete[] ipic;
    delete[] ndc;
    delete[] nc;

    NS_LOG_INFO ("Done.");

    return 0;

    // end main
}
