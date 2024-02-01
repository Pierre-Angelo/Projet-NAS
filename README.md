# Network Automation Project

Main files are `generate_config.py` and `intent_file_net_policies.json`.
If you are an evaluator, we recommend only reading sections: `Quick config and lauch`, `Features (summary)` and `Behaviour and main gns3 file structure` (specially solution 1)

The objective of this project is to simutlate complex networks using GNS3 to later develop a script to configure each router automatically. For this we will be using ipv6 connections on Cisco routers.

## Prerequisites

- Python 3.x
- A JSON file containing the network intent and configuration details.
- A GNS3 file containing the network corresponding to the JSON file structure details.

## Quick config and lauch:

#### Windows
Open a command prompt in the project directory and execute:

```bash
python .\generate_config.py .\intent_file_net_policies.json
```

#### Linux (Debian)
In the terminal, navigate to the project directory and run:
```bash
python3 generate_config.py intent_file_net_policies.json
```
This command generates the startup configuration for each router.   
Next, open your gns3 file and start all routers. They will automatically load their configuration. Wait for BGP to establish all connections and you are good to go! 
   
## Features (Summary)
The following features are supported by this project (intent file + script + gns3 folder)

1. Interface configurations.
2. RIP protocol support.
3. OSPF protocol support, including optional OSPF metrics configuration.
4. Comprehensive BGP configuration:
  - Establishment of neighbor relationships (internal and external).
  - Community tagging.
  - Route advertisement.
  - Route filtering.

#### Future Development
- Integration of Telnet for remote management (or not).

## Behaviour and main gns3 file structure

The 2 principal ASes, Blue and Red act as peers. Both have a common provider. Blue uses RIP and has 2 Clients, Red uses OSPF and has 1 client.

All routers outside Blue and Red represent each a single router AS.

Red has set it's OSPF metrics to avoid the R71-R72 connection, so every message passes through R73.

Red and Blue do not share their inter-As networks. This measure prevents Providers from using and knowing about our network topology.
However, clients that wish to do networking mapping or troubleshooting have 3 options:

1. Advertising their shared network with principal AS (recommended).
This will facilitate the usage of other tools such as traceroute and will simplify the handling of commands.
(You can copy and paste using the corresponding client)

Client 41:
conf t
router bgp 4
address-family ipv6 unicast
network 140:1141::/64

Client 51:
conf t
router bgp 5
address-family ipv6 unicast
network 150:1251::/64

Client 81:
conf t
router bgp 8
address-family ipv6 unicast
network 280:7381::/64

(This way the route is tagged as client route)

2. Ping using an internal AS router. This requieres to install and configure an additional router inside the client's Autonomous system.

3. Ping using the source option.

Examples (only 1 needed):
R41 # ping <IPprefix> source g2/0
R51 # ping <IPprefix> source g2/0
R81 # ping <IPprefix> source g1/0

This service is not provided to peers and providers.

## Intent File Configuration

Customize the `intent_file_net_policies.json` to alter the network setup. Ensure your modifications match the structure of our intent file.

For each router:
- Assign a hostname in the format: RXY, where XY represents the router number.
- Define interfaces and their corresponding addresses.

Example:
```json
{  
   "hostname" : "R12",
   "interfaces" : {
       "G1/0" : "200:1220::12/64",
       "G2/0" : "6780:1271::12/64",
       "G3/0" : "111::12/64"
       // Additional interfaces can be added or removed
   }
}
```
A default loopback0 interface will be assigned an address based on the router's hostname numbers (e.g., 1::2/64 for R12).



### Interior Gateway Protocol (IGP)
Specify either OSPF or RIP as the IGP. For OSPF, you can set OSPF costs to modify link weights, affecting OSPF metrics.

Example:
```json
{  
   "protocole" : "OSPF",
   "OSPF_cost": {
       "G3/0" : 10,
       "G5/0" : 100
   }
}
```
   
If you chose OSPF, you will have an OSPF_cost field where you can modify the weight of each link. This will modify the OSPF metrics. 
This is optional and you can leave empty brackets if you do not wish to set weighted links or if you use RIP instead.

### Border, Non-Border routers and BGP
If it is a non border router (not connected to any external AS), set the broder field as it follows:
```json
   {  
      //... 
      "border" : "NULL"
      //...
   }
```
This will create an iBGP Neighbor session with all adjacent routers.


In the case of a Border router, you must indicate in this field wich interfaces connect to exrernal ASes:
```json
   {
      //...
      "border" : [["G1/0","NULL"],["G2/0","NULL"]]
      //...
   }
```
This will create an eBGP Neighbor session with adjacent routers of the specified interfaces, and iBGP sessions with the rest.

Additionally, you can implement BGP policies and route filtering by changing the "NULL" part of the last line by "CLIENT", "PEER" or "PROVIDER"

This will apply BGP policies and route filtering as follows:
"CLIENT"  : Routes recieved are tagged as 1:1.
            Local preference is set to 400.
"PEER"    : Routes are only sent if they have the client tag (1:1). Any other route is blocked.
            Local preference is set to 300.
"PROVIDER": Routes are only sent if they have the client tag (1:1). Any other route is blocked.
            Local preference is set to 100.
## Usage

1. Prepare a JSON file with your network's configuration intent. The JSON structure should include details for each router, such as AS number, routing protocol, border router information, hostname, OSPF costs, and interfaces just as explained in the intent file configuration.

2. Run the script with the path to your JSON file as an argument:

```bash
   python generate_config.py path_to/intent_file.json
```
(apply the same reasoning for linux by using pyhton3 instad)

3. The script will generate configuration files for each router defined in the JSON file and save them to the associated directory within the project structure.

## JSON File Structure

- `routers`: An array of objects, each representing a router's configuration.
- `config_files`: Specifies the directory and filename for each router's configuration file.
- `network_name`: The name of your network, used in the directory path for saving configurations.