import json
with open('intent_file_net_policies.json','r',encoding='utf-8') as f:
 data = list(json.load(f).values())


global nl ,t,AS
nl = "!\n"
AS ={}
t = [
    nl*9+"\n"+nl+"! Last configuration change at 11:19:13 UTC Fri Dec 22 2023\n"+nl+"version 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n"+nl ,
    nl+"boot-start-marker\nboot-end-marker\n"+3*nl+
    "no aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n"+
    6*nl+"no ip domain lookup\nipv6 unicast-routing\nipv6 cef\n"+
    2*nl+"multilink bundle-name authenticated\n"+nl*9+
    "ip tcp synwait-time 5\n"+12*nl,
    "ip forward-protocol nd\n"+nl*2+"no ip http server\nno ip http secure-server\n"+nl,
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
        l0 = self.hostname[1]+"::"+ self.hostname[2]+"/128\n"
        G = "interface GigabitEthernet"
        nip =" no ip address\n"
        nego = " negotiation auto\n"
        address = " ipv6 address "
        en = " ipv6 enable\n"
        endProt = " "+self.AS+" area 0\n" if self.protocole == "OSPF" else " p"+self.AS+" enable\n"
        prot = " ipv6 " + self.protocole.lower() +endProt
        fast = "interface FastEthernet0/0\n no ip address\n shutdown\n duplex full"
        res = "interface Loopback0\n" + nip+address+l0+en+prot+nl+fast+"\n"+nl

        for it, add in self.interfaces.items():
            res += G+it[1:]+"\n"+nip+nego+address+add+"\n"+en+prot+nl
            if self.ospf_cost.get(it) is not None :
                res += " ipv6 ospf cost " + str(self.ospf_cost[it]) +"\n"+nl
        
        return res
    
    def bgp(self) :
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
                res
        res += nl+" address-family ipv4\n exit-address-family\n"+nl+ " address-family ipv6\n"
        

        for nei in listRAS :
            if nei != self.hostname :
                res +=   "  neighbor "+nei[1]+"::"+ nei[2]+ " activate\n"
        if self.border != "NULL" :
            for inter in self.border :
                remRouter = self.interfaces[inter[0]][6:8] if self.interfaces[inter[0]][4:6] == self.hostname[1:] else self.interfaces[inter[0]][4:6] 
                add = self.interfaces[inter[0]][:10] + remRouter
                res += "  neighbor "+ add + " activate\n"
                if inter[1] != "NULL":
                    res += "  neighbor "+ add + " route-map " + inter[1] +"_PREF in\n"
            res += "  network " + self.AS*3 + "::/16\n" 
        res += " exit-address-family\n"+nl

        return res
    
    def conn(self):
        res = ""
        if self.border != "NULL" :
            res += "ipv6 route " + self.AS*3 + "::/16 null0\n"
        if self.protocole == "OSPF":
            res += "ipv6 router ospf "+self.AS+"\n router-id "+((self.hostname[1:]+".")*4)[:-1]+"\n"
            if self.border != "NULL" :
                for inter in self.border :
                    res += " passive-interface  GigabitEthernet"+inter[0][1:]+ "\n"
        else :
            res += "ipv6 router rip p"+self.AS+"\n redistribute connected\n"
        
        if self.border != "NULL" :
            type_nei = []
            for inter in self.border :
                
                if inter[1] != "NULL" and inter[1] not in type_nei:
                    loc_pref = 100
                    if inter[1] == "CLIENT":
                        loc_pref = 400
                    elif inter[1] == "PEER":
                        loc_pref = 300
                    elif inter[1] == "PROVIDER":
                        loc_pref = 200  
                    res += nl*2 + "route-map " + inter[1] + "_PREF permit 10\n"
                    res += " set local-preference " + str(loc_pref) + "\n"
                    type_nei.append(inter[1])
            return res


list_router = []

for r in data[0] :
    list_router.append(router(r["AS"],r["protocole"],r["border"],r["hostname"],r["OSPF_cost"],r["interfaces"]))
    AS[list_router[-1].AS]=[]

for r in list_router :
    AS[r.AS].append(r.hostname)

fichiers = data[1]["config_files"]

for r in list_router:
    config = t[0]+r.hn+t[1]+ r.genInterface()+r.bgp()+t[2]+r.conn()+t[3]+t[4]

    with open(data[1]["network_name"]+"\project-files\dynamips\\"+fichiers[r.hostname][0]+"\configs\i"+fichiers[r.hostname][1]+"_startup-config.cfg",'w',encoding='utf-8') as f :
        f.write(config)
        
