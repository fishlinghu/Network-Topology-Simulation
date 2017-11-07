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

// node ID starting from a number to the end represents a server
int getStartingServerID(std::string input) {
    std::map<int, int> degree_counter;
    std::ifstream fs;
    int node_a, node_b;
    // read in two nodes id line by line
    // count the degree of each node
    fs.open(input, std::ifstream::in);
    while (fs >> node_a >> node_b) {
        if (degree_counter.count(node_a) == 0) {
            degree_counter[node_a] = 1;
        } else {
            ++degree_counter[node_a];
        }

        if (degree_counter.count(node_b) == 0) {
            degree_counter[node_b] = 1;
        } else {
            ++degree_counter[node_b];
        }
    }
    fs.close();

    // iterate through the map, nodes with degree = 1 are servers
    int min_index = -1;
    for (std::map<int,int>::iterator it=degree_counter.begin(); it!=degree_counter.end(); ++it) {
        if (it->second == 1) {
            if (min_index == -1 || min_index > it->first) {
                min_index = it->first;
            }
        }
    }
    return min_index;
}

// ----------------------------------------------------------------------
// -- main
// ----------------------------------------------
int main(int argc, char * argv[]) {

    std::string format("Orbis");
    std::string input("src/topology-read/examples/Orbis_toposample.txt");
    double duration = 3.0;
    std::string data_rate("0.5Mbps");

    // Set up command line parameters used to control the experiment.
    CommandLine cmd;
    cmd.AddValue("format", "Format to use for data input [Orbis|Inet|Rocketfuel].",
        format);
    cmd.AddValue("input", "Name of the input file.",
        input);
    cmd.AddValue("duration", "Duration of the test in second (double)",
        duration);
    cmd.AddValue("dataRate", "Data rate of links", data_rate),
    cmd.Parse(argc, argv);

    // ------------------------------------------------------------
    // -- Read topology data.
    // --------------------------------------------
    // std::cout << "Server starts from idx=" << getStartingServerID(input) << "\n";
    const int starting_server_id = getStartingServerID(input);
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

    for (i = 0; i < totlinks; ++i){
        // p2p.SetChannelAttribute ("Delay", TimeValue(MilliSeconds(weight[i])));
        p2p.SetChannelAttribute ("Delay", StringValue ("2ms"));
        p2p.SetDeviceAttribute ("DataRate", StringValue (data_rate));
        ndc[i] = p2p.Install (nc[i]);
    }

    // it crates little subnets, one for each couple of nodes.
    NS_LOG_INFO ("creating ipv4 interfaces");
    Ipv4InterfaceContainer* ipic = new Ipv4InterfaceContainer[totlinks];
    for (i = 0; i < totlinks; ++i){
        ipic[i] = address.Assign (ndc[i]);
        address.NewNetwork ();
    }

    // ------------------------------------------------------------
    // -- Measure bisection bandwidth
    // --------------------------------------------
    Config::SetDefault ("ns3::Ipv4RawSocketImpl::Protocol", StringValue ("2"));

    uint16_t port = 9;  // well-known echo port number
    // Set the amount of data to send in bytes.  Zero is unlimited.
    uint32_t maxBytes = 0;
    int total_node_num = nodes.GetN();
    int half_server_num = (total_node_num - starting_server_id) / 2;

    /*
    std::cout << "Node id <--> Addr Mapping\n";
    for (i = 0; i < total_node_num; ++i) {
        Ptr<Ipv4> ipv4Server = nodes.Get(i)->GetObject<Ipv4> ();
        std::cout << i << ": " << ipv4Server->GetAddress(1,0).GetLocal() << "\n";
    }
    */

    //std::cout << "Sender: ";
    // first half are client nodes
    for ( i = starting_server_id; i < starting_server_id + half_server_num; ++i ){
        //std::cout << "," << i;
        Ptr<Node> client_node = nodes.Get(i);
        Ptr<Node> server_node = nodes.Get(i + half_server_num);
        Ptr<Ipv4> ipv4Server = server_node->GetObject<Ipv4> ();
        Ipv4InterfaceAddress iaddrServer = ipv4Server->GetAddress(1,0);
        Ipv4Address ipv4AddrServer = iaddrServer.GetLocal();
        BulkSendHelper source (
            "ns3::TcpSocketFactory",
            InetSocketAddress (ipv4AddrServer, port)
        );
        source.SetAttribute ("MaxBytes", UintegerValue (maxBytes));
        ApplicationContainer apps = source.Install (client_node);
        apps.Start (Seconds (0.0));
        apps.Stop (Seconds (duration));
    }
    //std::cout << "\nReceiver: ";
    // second half are server nodes
    NodeContainer serverNodes;
    for ( ; i < total_node_num; ++i) {
        //std::cout << "," << i;
        serverNodes.Add (nodes.Get(i));
    }
    //std::cout << "\n";

    PacketSinkHelper sink = PacketSinkHelper ("ns3::TcpSocketFactory",
        InetSocketAddress (Ipv4Address::GetAny (), port)
    );
    ApplicationContainer sinkApps = sink.Install (serverNodes);
    sinkApps.Start (Seconds (0.0));
    sinkApps.Stop (Seconds (duration));

    // 8. Install FlowMonitor on all nodes
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll ();
    // monitor->SetAttribute("DelayBinWidth", DoubleValue(0.001));
    // monitor->SetAttribute("JitterBinWidth", DoubleValue(0.001));
    // monitor->SetAttribute("PacketSizeBinWidth", DoubleValue(20));

    // ------------------------------------------------------------
    // -- Run the simulation
    // --------------------------------------------
    NS_LOG_INFO ("Run Simulation.");
    Simulator::Stop (Seconds (duration));
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
        //if (i->first > 2) {
            Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow (i->first);
            std::cout << "Flow " << i->first - 2 << " (" << t.sourceAddress << " -> " << t.destinationAddress << ")\n";
            std::cout << "  Tx Packets: " << i->second.txPackets << "\n";
            std::cout << "  Tx Bytes:   " << i->second.txBytes << "\n";
            std::cout << "  TxOffered:  " << i->second.txBytes * 8.0 / duration / 1000 / 1000  << " Mbps\n";
            std::cout << "  Rx Packets: " << i->second.rxPackets << "\n";
            std::cout << "  Rx Bytes:   " << i->second.rxBytes << "\n";
            //std::cout << "  Lost Packets: " << flow->second.lostPackets << endl;
            //std::cout << "  Pkt Lost Ratio: "
            //          << ((double)flow->second.txPackets-(double)flow->second.rxPackets)/(double)flow->second.txPackets
            //          << endl;
            std::cout << "  Throughput: " << i->second.rxBytes * 8.0 / duration / 1000 / 1000  << " Mbps\n";
            //std::cout << "  Mean{Delay}: " << (flow->second.delaySum.GetSeconds()/flow->second.rxPackets) << endl;
            //std::cout << "  Mean{Jitter}: " << (flow->second.jitterSum.GetSeconds()/(flow->second.rxPackets)) << endl;
        //}
    }

    long int sum = 0;
    ApplicationContainer::Iterator it;
    for (it = sinkApps.Begin (); it != sinkApps.End (); ++it) {
        Ptr<PacketSink> sink1 = DynamicCast<PacketSink>((*it));
        sum += sink1->GetTotalRx();
    }
    std::cout << "Total Bytes Received: " << sum << std::endl;
    std::cout << "Bandwidth: " << sum / duration << "byte/s" << std::endl;

    delete[] ipic;
    delete[] ndc;
    delete[] nc;

    NS_LOG_INFO ("Done.");

    return 0;

    // end main
}
