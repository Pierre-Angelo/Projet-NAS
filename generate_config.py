import json
#import sys
"""
if len(sys.argv) < 2 :
    print("usage : python3 generate_config.py [intent file name]")
    exit()"""

intent_file_name = ".\\intent_file_net_policies.json" #sys.argv[1]

with open(intent_file_name,'r',encoding='utf-8') as f:
 data = list(json.load(f).values())

def get_sr(routeurs):
    routeur_serveur=[]
    for i,router in enumerate(routeurs):
        if router["AS"]==1:
            routeur_serveur.append(router["hostname"])
    return(routeur_serveur)

def icon(routeurs,routeur_serveur):
    connexion_list=[]
    for i,router in enumerate(routeurs):
        hostname=router["hostname"]
        for interface,value in router["interfaces"].items():
             if (value in routeur_serveur) and (([value,hostname]) not in connexion_list):
                  connexion_list.append([hostname,value])
    return(connexion_list)

def i_autoip(routeurs,connexion_list):
    for i,router in enumerate(routeurs):
        hostname=router["hostname"]
        for interface,value in router["interfaces"].items():
            if [hostname,value] in connexion_list:
                index = connexion_list.index([hostname, value])
                ip=(f"192.168.{index+128}.1/30")
                routeurs[i]["interfaces"][interface]=ip
            elif [value,hostname] in connexion_list:
                index = connexion_list.index([value,hostname])
                ip=(f"192.168.{index+128}.2/30")
                routeurs[i]["interfaces"][interface]=ip

def mask(i) :
    if (i == 32) :
        return "255.255.255.255"
    elif (i == 30) :
        return "255.255.255.252"
    else :
        return "nop"

global nl ,t,AS
nl = "!\n"
AS ={}
t = [
    nl*9+"\n"+nl+"! Last configuration change at 11:19:13 UTC Fri Dec 22 2023\n"+nl+"version 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n"+nl ,
    nl+"boot-start-marker\nboot-end-marker\n"+3*nl+
    "no aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n"+
    6*nl+"no ip domain lookup\nno ipv6 cef\n"+
    2*nl+"mpls label protocol ldp\nmultilink bundle-name authenticated\n"+nl*9+
    "ip tcp synwait-time 5\n"+12*nl,
    4*nl+"control-plane\n"+2*nl+
    "line con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\n",
    "line aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline vty 0 4\n login\n"+2*nl+"end"
]

class router() :
    def __init__(self, AS,protocole, border,hostname,ospf_cost,interfaces):
        self.AS = str(AS)
        self.protocole = protocole
        self.border = border
        self.hostname = hostname
        self.ospf_cost = ospf_cost
        self.interfaces = interfaces
        self.hn = "hostname " + self.hostname+"\n"
    
    def genInterface(self): 
        l0 = self.hostname[1]+"."+ self.hostname[2]+".0.1 " + mask(32) + "\n"
        G = "interface GigabitEthernet"
        nego = " negotiation auto\n"
        address = " ip address "
        endProt = " "+self.AS+" area 0\n" if self.protocole == "OSPF" else " p"+self.AS+" enable\n"
        prot = " ip " + self.protocole.lower() +endProt
        fast = "interface FastEthernet0/0\n no ip address\n shutdown\n duplex full"
        res = "interface Loopback0\n" + address+l0+prot+nl+fast+"\n"+nl

        for it, add in self.interfaces.items():
            mad = add.split("/")
            res += G+it[1:]+"\n"+nego+address+mad[0]+" "+mask(int(mad[1]))+"\n"+(prot + " mpls ip\n" if add.split(".")[0] == self.AS else "")+nl
            if self.ospf_cost.get(it) is not None :
                res += " ip ospf cost " + str(self.ospf_cost[it]) +"\n"+nl
        
        return res
    
    def bgp(self) : # bgp, duh
        listRAS = AS[self.AS]
        res = "router bgp " +self.AS+"\n bgp router-id "+((self.hostname[1:]+".")*4)[:-1]+"\n bgp log-neighbor-changes\n no bgp default ipv4-unicast\n"
        for nei in listRAS :
            if nei != self.hostname :
                res+= " neighbor "+nei[1]+"::"+ nei[2]+" remote-as "+ self.AS+"\n"
                res+= " neighbor "+nei[1]+"::"+ nei[2]+" update-source Loopback0\n"
        
        if self.border != "NULL" :
            for inter in self.border :
                remRouter = self.interfaces[inter[0]][6:8] if self.interfaces[inter[0]][4:6] == self.hostname[1:] else self.interfaces[inter[0]][4:6] 
                remAS = remRouter[0]
                add = self.interfaces[inter[0]][:10] + remRouter
                res += " neighbor "+ add + " remote-as "+ remAS+"\n"

        res += nl+" address-family ipv4\n exit-address-family\n"+nl+ " address-family ipv6\n"
        

        for nei in listRAS :
            if nei != self.hostname :
                res +=   "  neighbor "+nei[1]+"::"+ nei[2]+ " activate\n"
                res +=   "  neighbor "+nei[1]+"::"+ nei[2]+ " send-community\n"
                
        if self.border != "NULL" :
            for inter in self.border :
                remRouter = self.interfaces[inter[0]][6:8] if self.interfaces[inter[0]][4:6] == self.hostname[1:] else self.interfaces[inter[0]][4:6] 
                add = self.interfaces[inter[0]][:10] + remRouter
                res += "  neighbor "+ add + " activate\n"

                if inter[1] != "NULL": # inter[1]=="NULL" Routers are those of external ASes
                    res += "  neighbor "+ add + " route-map " + inter[1] +" in\n"
                    if inter[1] != "CLIENT":
                        res += "  neighbor "+ add + " route-map FILTER_TOWARDS_" + inter[1] +" out\n"

            res += "  network " + self.AS*3 + "::/16\n" 
        res += " exit-address-family\n"+nl
        return res
    
    def communities(self):
        res = ""
        if self.border != "NULL" and self.border[0][1] != "NULL" :
            res +="ip community-list standard ClientCommunity permit 1:1\n"
        return res
    
    def conn(self): # Internal protocol (ospf/rip)
        res = ""
        res += "ip forward-protocol nd\n"+nl
        # res += self.communities() + nl
        res += "no ip http server\nno ip http secure-server\n"+nl
        # if self.border != "NULL" :
            # res += "ipv6 route " + self.AS*3 + "::/16 null0\n"
        if self.protocole == "OSPF":
            res += "router ospf "+self.AS+"\n"
            # if self.border != "NULL" :
                # for inter in self.border :
                    # res += " passive-interface  GigabitEthernet"+inter[0][1:]+ "\n"
        else :
            res += "router rip p"+self.AS+"\n redistribute connected\n"
        return res
        
    def route_map(self):
        res = ""
        if self.border != "NULL" :
            type_nei = []
            for inter in self.border :
                
                if inter[1] != "NULL" and inter[1] not in type_nei:
                    loc_pref = 100
                    community_tag = None
                    if inter[1] == "CLIENT":
                        loc_pref = 400
                        community_tag = "1:1"
                    elif inter[1] == "PEER":
                        loc_pref = 300
                    elif inter[1] == "PROVIDER":
                        loc_pref = 200  
                    res += nl*2 + "route-map " + inter[1] + " permit 10\n"
                    res += " set local-preference " + str(loc_pref) + "\n"
                    if  community_tag is not None: 
                        res+= " set community "+community_tag+"\n"

                    
                    if inter[1] != "CLIENT":                     
                        res += nl +"route-map FILTER_TOWARDS_" + inter[1] +" permit 10 \n"
                        res += " match community " + "ClientCommunity\n"
                    
                    type_nei.append(inter[1])
        return res

# auto-ip de provider
routeurs=data[0]
routeur_serveur=get_sr(routeurs)
connexion_list=icon(routeurs,routeur_serveur)
i_autoip(routeurs,connexion_list)

list_router = []

for r in data[0] :
    list_router.append(router(r["AS"],r["protocole"],r["border"],r["hostname"],r["OSPF_cost"],r["interfaces"]))
    AS[list_router[-1].AS]=[]

for r in list_router :
    AS[r.AS].append(r.hostname)

fichiers = data[1]["config_files"]

for r in list_router:
    config = t[0]+r.hn+t[1]+ r.genInterface()+r.conn()+t[2]+t[3]

    with open(data[1]["network_name"]+"\\project-files\\dynamips\\"+fichiers[r.hostname][0]+"\\configs\\i"+fichiers[r.hostname][1]+"_startup-config.cfg",'w',encoding='utf-8') as f :
        f.write(config)
        
