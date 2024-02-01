# Network Automation Project

The 3 main files are `generate_config.py`, `intent_file_net_policies.json` and `reseau_politique_auto\reseau_politique.gns3`.<br>
If you are an **evaluator**, we recommend only reading sections **Quick config and lauch**, **Features (summary)** and **Behaviour and main gns3 file structure** (specially solution 1).

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
Next, open your gns3 file and start all routers. They will automatically load their configuration. Wait for BGP to establish all connections (2.5 minutes). <br>
If you see 888::/16 on blue clients' routing tables or 444::/16 and 555::/16 on red client's routing table, you are good to go!
   
## Features (Summary)
The following features are supported by this project (intent file + script + gns3 folder).

1. Interface configurations.
2. RIP protocol support.
3. OSPF protocol support, including optional OSPF metrics configuration.
4. Comprehensive BGP configuration:<br>
&nbsp; - Establishment of neighbor relationships (internal and external).<br>
&nbsp; - Community tagging.<br>
&nbsp; - Route advertisement.<br>
&nbsp; - Route filtering.<br>

#### Future Development
- Integration of Telnet for remote management (or not).

## Main gns3 file's behaviour and structure 

The 2 principal ASes, Blue and Red act as peers. Both have a common provider. Blue uses RIP and has 2 Clients, Red uses OSPF and has 1 client.

All routers outside Blue and Red represent each a single AS.

Red has set it's OSPF metrics to avoid the R71-R72 link connection, so every message passes through R73.

Red and Blue do not share their inter-As networks. This measure prevents Providers from using and knowing about our network topology.
However, clients that wish to do networking mapping or troubleshooting have 3 options if they need to bypass this:

1) Advertising their shared network with principal AS (recommended).
This will facilitate the usage of other tools such as traceroute and will simplify the handling of commands.
(You can copy and paste using the corresponding client).<br>

&nbsp;&nbsp;Client 41:<br>
&nbsp;&nbsp;&nbsp;&nbsp;conf t<br>
&nbsp;&nbsp;&nbsp;&nbsp;router bgp 4<br>
&nbsp;&nbsp;&nbsp;&nbsp;address-family ipv6 unicast<br>
&nbsp;&nbsp;&nbsp;&nbsp;network 140:1141::/64<br>

&nbsp;&nbsp;Client 51:<br>
&nbsp;&nbsp;&nbsp;&nbsp;conf t<br>
&nbsp;&nbsp;&nbsp;&nbsp;router bgp 5<br>
&nbsp;&nbsp;&nbsp;&nbsp;address-family ipv6 unicast<br>
&nbsp;&nbsp;&nbsp;&nbsp;network 150:1251::/64<br>

&nbsp;&nbsp;Client 81:<br>
&nbsp;&nbsp;&nbsp;&nbsp;conf t<br>
&nbsp;&nbsp;&nbsp;&nbsp;router bgp 8<br>
&nbsp;&nbsp;&nbsp;&nbsp;address-family ipv6 unicast<br>
&nbsp;&nbsp;&nbsp;&nbsp;network 780:7381::/64<br>

(This way the route is tagged as client route, which matches the filter).

2) Ping using an internal AS router. This requieres to install and configure an additional router inside the client's Autonomous system.

3) Ping using the source option.

Examples (only 1 needed):
R41 # ping <IPprefix> source g2/0
R51 # ping <IPprefix> source g2/0
R81 # ping <IPprefix> source g1/0

This service is not available to peers and providers.

## Intent File Configuration

Customize the `intent_file_net_policies.json` to alter the network setup. Ensure your modifications match the structure of our intent file.

For each router:
- Assign a hostname in the format: RXY, where XY represents the router number.
- Define interfaces and their corresponding addresses. 

Interfaces connected to routers inside the same AS must have interfaces with the next format: 
- nnn:xxxx:xxxx:xxxx::xxxx/64 where n MUST be the AS number and x can be set to anything

Interfaces connected to other AS, must have one of the following formats dependig on the as number (n), remote-as number(m), own hostname number(ab), remote hostname number (cd):

- nm0:abcd::ab/64 If configuring router Rab and n<m
- nm0:abcd::cd/64 If configuring router Rcd and n<m
- mn0:cdab::cd/64 If configuring router Rab and n>m
- mn0:cdab::ab/64 If configuring router Rcd and n>m

Explanaition: first digit is the lowest AS number, second digit is the remaining as, third is always 0. After semicolon, the lowest hostname is taken first, followed by the bigger. Lastly, the remaining last 2 digits will always correspond to the self Router.
If you have a better way to explain this, please submit to the git your proposal.

We higly recommend you to analyse the following example, it might clarify it better.   

Example:
```java
{
   {  
      "AS": 1,
      "hostname" : "R12", //Rab
      "interfaces" : {
         "G1/0" : "111:1213::12/64",
         "G2/0" : "111::5/64",       
         "G3/0" : "170:1276::12/64" // Link to remote AS
         // Additional interfaces can be added or removed
      },
      "AS": 7,
      "hostname" : "R76", //Rcd
      "interfaces" : {
         "G1/0" : "777:66::AA/64", 
         "G3/0" : "170:1276::76/64" // Link to remote AS
      }      
   }   
}
```
A default loopback0 interface will be assigned an address based on the router's hostname numbers (e.g., 1::2/128 for R12, 7::6/128).



### Interior Gateway Protocol (IGP)
Specify either OSPF or RIP as the IGP. For OSPF, you can set OSPF costs to modify link weights, affecting OSPF metrics.

Example:
```java
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
```java
   {
      //...
      "border" : "NULL"
      //...
   }
```
This will create an iBGP Neighbor session with all adjacent routers.


In the case of a Border router, you must indicate in this field wich interfaces connect to exrernal ASes:
```java
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

A configured router with all the option might look like this example:
```json
{
   "AS" : 6,
   "protocole" : "OSPF",
   "border" : [["G1/0","PEER"],["G2/0","CLIENT"]],
   "hostname" : "R61",
   "OSPF_cost": {"G3/0" : 10},
   "interfaces" : 
      {
         "G1/0" : "160:1361::61/64",
         "G2/0" : "670:6171::61/64",
         "G3/0" : "666::1/64"
      }
}
```
## Usage

1. Prepare a JSON file with your network's configuration intent. The JSON structure should include details for each router, such as AS number, routing protocol, border router information, hostname, OSPF costs, and interfaces just as explained in the intent file configuration.

2. Run the script with the path to your JSON file as an argument:

```bash
   python generate_config.py path_to/intent_file.json
```
(apply the same reasoning for linux by using pyhton3 instad).

3. The script will generate configuration files for each router defined in the JSON file and save them to the associated directory within the project structure.

## JSON File Structure

- `routers`: An array of objects, each representing a router's configuration.
- `config_files`: Specifies the directory and filename for each router's configuration file.
- `network_name`: The name of your network, used in the directory path for saving configurations.

## TO DO
Clean main branch and implement the gitignore
