import json
with open('intent_file.json','r',encoding='utf-8') as f:
 data = list(json.load(f).values())[0]

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
    def __init__(self, AS,protocole, border,hostname,interfaces):
        self.AS = str(AS)
        self.protocole = protocole
        self.border = border
        self.hostname = hostname
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
        
        return res
    
    def bgp(self) :
        listRAS = AS[self.AS]
        res = "router bgp " +self.AS+"\n bgp router-id "+((self.hostname[1:]+".")*4)[:-1]+"\n bgp log-neighbor-changes\n no bgp default ipv4-unicast\n"
        for nei in listRAS :
            if nei != self.hostname :
                res+= " neighbor "+nei[1]+"::"+ nei[2]+" remote-as "+ self.AS+"\n"
                res+= " neighbor "+nei[1]+"::"+ nei[2]+" update-source Loopback0\n"

        if self.border != "NULL" :
            remAS = "1" if self.AS == "2" else "2"
            nei = self.interfaces[self.border][ self.interfaces[self.border].index(remAS):self.interfaces[self.border].index(remAS)+2]
            add = remAS*3+":"+self.interfaces[self.border][4:9]+"::"+nei
            res += " neighbor "+ add + " remote-as "+ remAS+"\n"+nl
        res += " address-family ipv4\n exit-address-family\n"+nl+ " address-family ipv6\n"
        
        if self.border != "NULL" :
            res += "  network 111:1112::11/64\n" if self.AS == "1" else "  network 222:2122::21/64\n"
        for nei in listRAS :
            if nei != self.hostname :
                res +=   "  neighbor "+nei[1]+"::"+ nei[2]+ " activate\n"
        if self.border != "NULL" :
            remAS = "1" if self.AS == "2" else "2"
            nei = self.interfaces[self.border][ self.interfaces[self.border].index(remAS):self.interfaces[self.border].index(remAS)+2]
            add = remAS*3+":"+self.interfaces[self.border][4:9]+"::"+nei
            res += "  neighbor "+ add + " activate\n"+nl 
        res += " exit-address-family\n"+nl
               
        return res
    
    def conn(self):
        res = ""
        if self.protocole == "OSPF":
            res += "ipv6 router ospf 2\n router-id "+((self.hostname[1:]+".")*4)[:-1]+"\n"
            if self.border != "NULL" :
                res += " passive-interface  GigabitEthernet"+self.border[1:]
        else :
            res += "ipv6 router rip p"+self.AS+"\n redistribute connected\n"
        return res


list_router = []

for r in data :
    list_router.append(router(r["AS"],r["protocole"],r["border"],r["hostname"],r["interfaces"]))
    AS[list_router[-1].AS]=[]

for r in list_router :
    AS[r.AS].append(r.hostname)

fichiers = {"R11" :["434a0746-8448-42ff-b176-11b5d13142d8","1"],
            "R12" :["11b9fa6d-214c-4845-b6a4-b1db370b87a5","2"],
            "R13" :["49a7a5f5-a58e-4855-b9f7-3aaa58e3a712","3"],
            "R14" :["6e7529f7-28cd-42d2-ae28-235ea466b4fa","4"],
            "R15" :["804e7a1b-92c3-4acb-9b3c-79bc9faabc8b","5"],
            "R16" :["1b884c37-dbe9-4297-9752-a13c4ff04155","7"],
            "R17" :["cd7d4c92-9bd7-471b-bf7e-1d0e6ad20034","11"],
            "R21" :["3f5961df-37d9-4064-8968-f411b50c4b0f","10"],
            "R22" :["96095d7c-3131-487a-acf4-882bc827c809","8"],
            "R23" :["80b312b2-9921-41b0-b614-952ce6b3b26f","6"],
            "R24" :["eb00c665-cc69-4d6f-9da3-0b9430aa9e03","9"],
            "R25" :["f09bf038-5f96-4513-812d-f87a2fb6d07f","13"],
            "R26" :["f356ec56-d010-4d5a-99c0-20aeff93d418","12"],
            "R27" :["2547e6ce-55b0-4f21-a354-4d7c2d06a3ce","14"]}

for r in list_router:
    config = t[0]+r.hn+t[1]+ r.genInterface()+r.bgp()+t[2]+r.conn()+t[3]+t[4]

    with open("deuxieme-reseau-pas-trop-simple\project-files\dynamips\\"+fichiers[r.hostname][0]+"\configs\i"+fichiers[r.hostname][1]+"_startup-config.cfg",'w',encoding='utf-8') as f :
        f.write(config)
         
