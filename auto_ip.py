import json
import os

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

intent_file_name = ".\\intent_file_net_policies.json" #sys.argv[1]

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
config_path = os.path.join(dir_path, "intent_file_net_policies.json") 
with open(config_path, 'r') as file:
    data = list(json.load(file).values())

routeurs= data[0]
routeur_serveur=get_sr(routeurs)
connexion_list=icon(routeurs,routeur_serveur)
i_autoip(routeurs,connexion_list)

print(routeurs)