# Network Architecture and Service Project

The 3 main files are `generate_config.py`, `intent_file.json` and `reseau_demo\reseau_demo.gns3`.<br>
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
python .\generate_config.py 
```

#### Linux (Debian)
In the terminal, navigate to the project directory and run:
```bash
python3 generate_config.py 
```
This command generates the startup configuration for each router.   
Next, open your gns3 file and start all routers. They will automatically load their configuration. Wait for BGP to establish all connections (2.5 minutes). <br>
   
## Features (Summary)
The following features are supported and automated by this project (intent file + script + gns3 folder).

1. Interface configurations with automated address attribution for interfaces inside the network.
2. OSPF protocol support, including optional OSPF metrics configuration.
3. LDP protocol support, MPLS transport in the core, Penultimate Hop Popping behaviour
4. Comprehensive BGP configuration:<br>
&nbsp; - Establishment of neighbor relationships (internal and external).<br>
&nbsp; - Route advertisement.<br>
&nbsp; - VPNv4 where Red client and Blue cannot communicate with each other but they both can talk to the Green client. <br>
&nbsp; - Two route reflectors in the core.


#### Future Development
- Integration of Telnet for remote management .
- adding internet service on the network
- add RSVP
- Add Ingress TE services for multi-connected CE routers

## Intent File Configuration

Customize the `intent_file.json` to alter the network setup. Ensure your modifications match the structure of our intent file.

For each router:
- Assign a hostname in the format: RXY, where X is the ASN and Y represents the router number.
- Define interfaces and their corresponding addresses. If the interface is inside the network you can simply put the hostname of the conneted router and an address will be attributed automatically. 

Interfaces connected to other AS, must have one of the following formats dependig on the as number (n), remote-as number(m)

- nm.mn.0.1/30 If configuring router and n<m
- nm.mn.0.2/30 If configuring router and n>m

A default loopback0 interface will be assigned an address based on the router's hostname numbers.

### Interior Gateway Protocol (IGP)
You MUST specify OSPF as the IGP.You can set OSPF costs to modify link weights, affecting OSPF metrics.

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

You will have an OSPF_cost field where you can modify the weight of each link. This will modify the OSPF metrics. 
This is optional and you can leave empty brackets if you do not wish to set weighted links.

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


Additionally, you can implement BGP VPNv4 and route filtering by changing the "NULL" part of the last line by "VRF:[name of vpn client]:[number of vpn client]" (e.g : "border" : [["G1/0","VRF:Bleu:1"],["G3/0","VRF:Rouge:2"]])

This will create a VRF which exports the incoming client routes.
To manage what routes each VRF should import you have to modify the "importVRF" field which is at the end of the intent file.
```json
"importVRF" : {
        "Bleu" : ["Vert:3"],
        "Rouge" : ["Vert:3"],
        "Vert" : ["Rouge:2","Bleu:1"]
    }
```


A configured router with all the option might look like this example:
```json
{
            "AS" : 1,
            "protocole" : "OSPF",
            "border" : [["G1/0","VRF:Bleu:1"],["G3/0","VRF:Vert:3"],["G4/0","VRF:Rouge:2"]],
            "hostname" : "R11",
            "OSPF_cost": {},  
            "interfaces" : 
                {
                    "G1/0" : "14.41.0.1/30",
                    "G2/0" : "R14",
                    "G3/0" : "18.81.0.1/30",
                    "G4/0" : "16.61.0.1/30"
                }     
        }
```
## Usage

1. Prepare a JSON file with your network's configuration intent. The JSON structure should include details for each router, such as AS number, routing protocol, border router information, hostname, OSPF costs, and interfaces just as explained in the intent file configuration.

2. Run the script :

```bash
   python generate_config.py
```
(apply the same reasoning for linux by using pyhton3 instad).

3. The script will generate configuration files for each router defined in the JSON file and save them to the associated directory within the project structure.

## JSON File Structure

- `routers`: An array of objects, each representing a router's configuration.
- `config_files`: Specifies the directory and filename for each router's configuration file.
- `network_name`: The name of your network, used in the directory path for saving configurations.
- `importVRF` : specifies the iports of the different VRF
