Austin Dunn | adunn@gatech.edu | adunn39
Nichole Deeb | ndeeb3@gatech.edu | ndeeb3

Project 2 | Milestone 2 | 11/11/18

node.py - main thread, contains global variables and command line code
packets.py - contains objects used to store and transfer packets
packet_transmission.py - pops transmission queue and sends packets as needed
packet_retrieval.py - stores incoming packets into a queue
packet_ping.py - sends out RTT requests to known nodes on a set interval
packet_processing.py - processes received packets and updates data structures
sample-output.txt - shows a sample interaction of a node

Requirements:
 Our code requires Python v3+
 The most updated version of Python 3 is recommended

Instructions for running our code:
 To start a node, the following can be run in the command-line within the folder containing node.py:
    python node.py <name> <local-port> <PoC-address> <PoC-port> <max-nodes>
        Where name: the name of the node
        local-port: the port you would like to host the node on
        PoC-address: the address of the node's point of contact (0 for none)
        PoC-port: the port of the node's point of contact (0 for none)
        max-nodes: the maximum number of nodes in the network

    To find the address and port of your node, check the top message of the console output.
    This should be in the form of:
        Initialized node <name> on <address>:<port>, max nodes 5, POC: <PoC-address>:<PoC-port>.

 To interact with your node, you can use one of the following commands:
    send "<message>": sends the ASCII text within <message> to all nodes
    send <filename>: sends the filename (must be contained within the folder containing node.py) to all nodes
    show-status: prints the star-map of all known nodes, their RTT, and the current hub
    disconnect: disconnects the node and closes all threads
    show-log: shows a log of all events that have occurred in the node

 IMPORTANT NOTE:
    Please allow up to a minute for discovery to complete when adding nodes to a network
    Otherwise, hub selection may not be accurate.

Any known bugs or limitations:
 Rapid changing of a hub can cause messages to hang up for a while before finally being sent
