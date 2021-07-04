from termcolor import colored  #pour faciliter la lecture sinon c'est trop dur de lire 
import matplotlib.pyplot as plt 
import matplotlib 

class Drone :
    def __init__(self,state,action_time):
        self.state = state              #état du drone, booléen True => en fonctionnement False en recharge 
        self.action_time = action_time  #indique depuis combien de temps le drone fait une action 
        #(recharge si state = False ou travail si state = True)
    
    #inverse l'état du drone
    def toggle_state(self):
        self.state = not self.state
       
    #réinitialise action_time
    def reset_time(self):
        self.action_time = 0


#def calcul l'average_amp qui dépend du poids du drone
def find_avg_amp():
    return True

#calcul l'autonomie du drone
#formule utilisé : (Battery Capacity * Battery Discharge /Average Amp Draw)*60
def drone_auto(bat_capacity,bat_discharge):
    avg_amp = find_avg_amp()
    return (bat_capacity*bat_discharge)/avg_amp

#calcul le temps de vol entre le béton et la construction
# d en mètre et vit_drone en m/s le résultat sera en m/min 
def time_construc(d,vit_drone):
    return (d/vit_drone)/60

#crée la config pour un nombre de drone multiple de 3 
def config_multiple(nb_drone,charge_time):
    list_drone = [Drone(True,0) for k in range(nb_drone)]
    for drone in list_drone[int(nb_drone/3):]:
        drone.state = not drone.state
        drone.action_time = charge_time 
    return list_drone

#crée la config pour un nombre de drone paire
def config_paire(nb_drone,charge_time):
    list_drone = [Drone(True,0) for k in range(nb_drone)]
    for drone in list_drone[int(nb_drone/2):]:
        drone.state = not drone.state
        drone.action_time = charge_time
    return list_drone

#retourne directement un nombre paire ou un multiple 
def get_paire_or_mult(nb,config):
    if config == "config_1": # cas on envoie la moitié et inversement
        if nb%2 == 0 :
            return nb
        else :  # cas il est impaire 
            return nb-1 
    else : # cas on coupe les drones en 2-3 groupes selon la valeur du nb de drone
        if nb%3 == 0 :
            return nb
        else : 
            #si nb_drone est impaire on le transforme en un nombre paire
            if nb%2 !=0 : # cas nb impaire
                return nb-1
            else : # cas nb paire 
                return nb 
    return nb
#retourne une liste de configuration optimale de drone
#soit nb_drone est un multiple de 3 soit un nombre paire (si impair on le transforme en nb pair)
def config_drone(nb_drone,charge_time,config):
    list_drone = []
    #cas de figure où me nb de drone est un multiple de 3
    if config == "config_0":
        list_drone = [Drone(True,0) for k in range(nb_drone)]
    elif config == "config_4":
        list_drone = [Drone(False,charge_time) for k in range(nb_drone)]
        list_drone[0].state = True
        list_drone[0].reset_time() 
    else : 
        if nb_drone%3 == 0 :
            list_drone = config_multiple(nb_drone,charge_time)
        else : 
            #si nb_drone est impaire on le transforme en un nombre paire
            if nb_drone%2 !=0 :
                nb_drone-=1
                if nb_drone%3 == 0 :
                    list_drone=config_multiple(nb_drone,charge_time)
                else : 
                    list_drone = config_paire(nb_drone,charge_time)
            else :
                list_drone = config_paire(nb_drone,charge_time)
    return list_drone, nb_drone

#fonction principale qui va nous retourner le temps de construction du mur 
#cf le fichier notion pour connaître la signification des variables
def main(payload,p_parachute,p_sys,poids_contruction,nb_drone,dist,vit_drone,charge_time,autonomie,config,print_info = False):
    #initiatilisation des variables
    temps,poids = 0,0                                                                     # initialisation du temps et du volume du béton 
    travel_time = time_construc(dist,vit_drone)                                            # temps de parcourt entre le béton et le mur (ou l'inverse, juste un aller)
    autonomie = autonomie    #drone_auto(bat_capacity,bat_discharge,avg_amp)                             # autonomie du drone 
    p_beton =  payload - (p_sys+p_parachute)#p_max_drone-(p_drone+p_parachute+p_sys)                                      # le poids en béton que le drone peut soulever
    
    if config == "config_1" :
        nb_drone = get_paire_or_mult(nb_drone,config)                                      #si on est dans le cas config 1 on essayer d'avoir un truc paire
        list_drone = config_paire(nb_drone,charge_time)
    elif config=="config_4":
        current_drone = 0 
        list_drone = config_drone(nb_drone,charge_time,'config_4')[0]
    else : 
        list_drone,nb_drone = config_drone(nb_drone,charge_time,config)                                   # nous donne une liste avec les drones comme ça on pourra direct appeler le drone
    # nous donnes les informations capitales qui vont nous permettre de faire notre calcul

    if print_info : 
        print(f"Les différentes informations sont :\nLe temps séparant le mur au béton {travel_time}\nle poids de béton {poids_contruction}\nune autonomie de {autonomie}\n")

    # logique principale
    while poids <= poids_contruction:
        #après l'aller-retour on check voir si le drone peut en refaire un autre pour déposer du ciment
        if config == "config_0": #on envoie tous les drone d'un coup
            if list_drone[0].state :
                if list_drone[0].action_time >= autonomie:
                    for drone in list_drone: #on met les drones en pause et on réinitialise action time
                        drone.toggle_state()   
                        drone.reset_time()
            else : 
                if list_drone[0].action_time >= charge_time:
                    for drone in list_drone: #on met les drones en activité et on réinitialise action time
                        drone.toggle_state()   
                        drone.reset_time()

        elif config == "config_4": # on envoie les drone 1 par 1 
            if list_drone[current_drone].state:
                if list_drone[current_drone].action_time >= autonomie:
                    list_drone[current_drone].toggle_state()
                    list_drone[current_drone].reset_time()
                    if (current_drone+1) == len(list_drone)-1:
                        current_drone = 0
                    else : 
                        current_drone+=1

                    if list_drone[current_drone].action_time >= charge_time : 
                        list_drone[current_drone].toggle_state()
                        list_drone[current_drone].reset_time()
               
        elif nb_drone%3 == 0 and config == "config_2": # cas le nombre de drone est un multiple de 3 + on est dans la config 2 
            if list_drone[0].state :  # cas premier tiers en fonctionnement
                if list_drone[0].action_time >= autonomie/2 and not list_drone[int(nb_drone/3)].state : # le groupe 1 ne peut qu'activer le groupe 2 
                    for drone in list_drone[int(nb_drone/3):int((2*nb_drone)/3)] : 
                        drone.toggle_state()
                        drone.reset_time() 
                if list_drone[0].action_time >= autonomie: # si on a dépassé l'autonomie du drone on l'envoie se recharger
                    for k in range(len(list_drone)) :
                        if k < int(nb_drone/3) or k>=int((2*nb_drone)/3):  # on éteint les drone du premier tier et on active ceux du dernier
                            list_drone[k].toggle_state()
                            list_drone[k].reset_time() 
            elif list_drone[-1].state:
                if list_drone[-1].action_time >= autonomie/2 and list_drone[int(nb_drone/3)].state : # le groupe 3 ne peut que désactiver le groupe 2 
                    for drone in list_drone[int(nb_drone/3):int((2*nb_drone)/3)] : #
                        drone.toggle_state()
                        drone.reset_time()  
                if list_drone[-1].action_time >= autonomie :
                    for k in range(len(list_drone)):
                        if k>= int((2*nb_drone)/3):  # on allume les drone du premier tier et on éteint ceux du dernier
                            list_drone[k].toggle_state()
                            list_drone[k].reset_time() 
            
            elif not list_drone[0].state : # cas on attend que le groupe 1 se recharge les autres font suivre car il y a tjs le même écart entre chaque groupe 
                if list_drone[0].action_time >= charge_time :
                    for drone  in list_drone[0:int(len(list_drone)/3)] :
                        drone.toggle_state()
                        drone.reset_time()

        else :  #config 1 on divise le nombre de drone par 2 pour envoyer ce dernier               
            if list_drone[0].state :                                                             # si c'est le groupe 1 qui est actif  
                if print_info :     
                    print(f"On est dans le cas où le groupe 1 est actif et action time vaut "+colored(list_drone[0].action_time,"red"))
                if  list_drone[0].action_time >= autonomie :#list_drone[0].not_reachable(autonomie,travel_time) : #list_drone[0].action_time >= 2*travel_time
                    for i in range(len(list_drone)) :
                        #si les drones sont rechargé alors seulement on les envoie construire le mur
                        if i >= int(len(list_drone)/2) :                                   
                            if  list_drone[i].action_time >= charge_time:                  # si le drone est chargé on peut l'envoyer en mission
                                list_drone[i].toggle_state()
                                list_drone[i].reset_time()
                        else : 
                            list_drone[i].toggle_state()
                            list_drone[i].reset_time()  
                            
            elif list_drone[-1].state:                                                           # si c'est le groupe 2 qui est actif 
                if print_info :
                    print(f"On est dans le cas où le groupe 2 est actif et action time vaut "+colored(list_drone[-1].action_time,"red"))

                if list_drone[-1].action_time >= autonomie : #list_drone[-1].not_reachable(autonomie,travel_time) : 
                    for i in range(len(list_drone)) :
                        
                        #si les drones sont rechargé alors seulement on les envoie construire le mur
                        if i <= int(len(list_drone)/2)-1 :                                   # faire des tests pour voir si c'est une inégalité stricte ou pas
                            if  list_drone[i].action_time >= charge_time:                  # si le drone est chargé on peut l'envoyer en mission
                                list_drone[i].toggle_state()
                                list_drone[i].reset_time()
                        else : 
                            list_drone[i].toggle_state()
                            list_drone[i].reset_time() 

            elif not list_drone[0].state and not list_drone[-1].state:                                 # cas où on a les 2 en attentes 
                if  list_drone[-1].action_time >= charge_time:                             # si les drones du groupe 2 sont rechargés on les envoie
                    for drone in list_drone[int(len(list_drone)/2):]:
                        drone.toggle_state()
                        drone.reset_time()
                elif list_drone[0].action_time >= charge_time :                            # si les drones du groupe 1 sont rechargés on les envoie
                    for drone in list_drone[0:int(len(list_drone)/2)] :
                        drone.toggle_state()
                        drone.reset_time()

        #le drone a réussi à faire son aller-retour
        temps+= 2*travel_time                                                              # on utilise l'aller-retour pour simplifier les calculs
        temps = round(temps,2)
        active_drone = 0
        for drone in list_drone:                                                           # on détermine le nombre de drone actif 
            if drone.state :
                active_drone+=1 
        poids += active_drone*p_beton                                                     # on ajoute le poids de béton nécessaire 
    

        #mise à jour du temps pour tous le monde peu importe l'état du drone
        for drone in list_drone :
            drone.action_time += 2*travel_time
            drone.action_time = round(drone.action_time,2) 

        if active_drone != 0 : 
            if print_info :
                print("La valeur du temps "+colored(temps,"green") +" et celle du béton est "+colored(poids,"green") +" le nombre de drone actif est "+colored(active_drone,"green")) 
            test = ""
            for k in range(len(list_drone)) :
                test += str(k)+" " +str(list_drone[k].state)+ " "
            if print_info:
                print("l'état des drones est ",test)
                print("\n\n")
    return temps 

"""
config_1 = on envoie dans la première moitié du groupe puis on envoie la seconde et on alterne
config_2 = on envoie le premier tiers au milieu de l'autonomie on envoie le groupe 2 puis le dernier tiers
p_drone,p_max_drone,p_parachute,p_sys,poids_contruction,nb_drone,dist,vit_drone,charge_time,autonomie,config
"""



#Nom du drone, payload,,vit_drone en m/s ,autonomie
drones = [
    ["Yuneec Tornado H920",1.6,21,24,4799],
    ["Airborne Vanguard",4.5,18,94,15990],
    ["Tarot T-18",8,15,20,706.08], #http://www.helipal.com/tarot-t18-octocopter-frame-set.html 
    ["Augmented Aerigon Drone",9,10,7,250000],
    ["Freefly Systems Alta 8",9.1,20,15,14363.71],
    ["DJI Agras T16",10,10,24,10500],
    ["DJI Spreading Wings S1000",11,13.41,15,3390], #https://www.droneshop.com/s1000-premium-dji-innovation
    ["Onyxstar Hydra-12",12,9.7,25,6513.3636], #https://www.dronevibes.com/forums/threads/superb-onyxstar-hydra-12-for-sale-dodeca-mikrokopter.35947/ 
    ["DJI Matrice 600 Pro",15.5,18,40,5699],
    ["Vulcan UAV Raven",24,10,20,13689]
]


# but donner le temps de construction en fonction du nombre de dron
# "payload,p_parachute,p_sys,poids_contruction,nb_drone,dist,vit_drone,charge_time,autonomie,config"
# p_parachute = 0.500
# p_sys = 0.500
# poids_construction = int(input('Poids de la construction ? '))
# dist = 5
# charge_time = 60
# nb_drone = [k for k in range(2,100)]
# for drone in drones:
#     temps_config_1 = [main(drone[1],p_parachute,p_sys,poids_construction,num,dist,drone[2],charge_time,drone[3],'config_1') for num in nb_drone]
#     price = [drone[4]*num for num in nb_drone]
#     temps_config_2 = [main(drone[1],p_parachute,p_sys,poids_construction,num,dist,drone[2],charge_time,drone[3],'config_2') for num in nb_drone]
#     plt.figure(figsize=(10, 5))
#     plt.gcf().subplots_adjust(left = 0.1, bottom = 0.1,
#                         wspace = 0, hspace = 0.7)
#     plt.subplot(211)
#     plt.plot(nb_drone,temps_config_1)
#     plt.title(f"Temps de construction d'un mur de {poids_construction} Kg avec le drone {str(drone[0])} dans la configuration 1")
#     plt.grid()
#     plt.xlabel("Nombre de drone")
#     plt.ylabel("Temps en min")
#     plt.subplot(212)
#     plt.plot(nb_drone,price)
#     plt.title(f"Coût pour de la configuration n°1 pour le drone {drone[0]}")
#     plt.savefig("graphique/"+str(drone[0])+"_config_1.png")
#     plt.show()
#     plt.figure(figsize=(10, 5))
#     plt.plot(nb_drone,temps_config_2)
#     plt.title(f"Temps de construction d'un mur de {poids_construction} Kg avec le drone {str(drone[0])} dans la configuration 2")
#     plt.grid()
#     plt.xlabel("Nombre de drone")
#     plt.ylabel("Temps en min")
#     plt.savefig("graphique/"+str(drone[0])+"_config_2.png")
#     plt.show()


# for k in range (6,100):
#     print("La valeur de k est ",k)
#     print(main(0.500,0,0,2000,k,5,1.38889,30,7.92,"config_4"))

# #5 km/h = 1,38889m/s

nb_drone = [k for k in range(2,100)]
nb_drone_4 = [k for k in range(6,100)]

temps_config_0 = [main(0.500,0,0,2000,nb,5,1.38889,30,7.92,"config_0") for nb in nb_drone ]
temps_config_1 = [main(0.500,0,0,2000,nb,5,1.38889,30,7.92,"config_1") for nb in nb_drone ]
temps_config_2 = [main(0.500,0,0,2000,nb,5,1.38889,30,7.92,"config_2") for nb in nb_drone ]

temps_config_4 = [main(0.500,0,0,2000,nb,5,1.38889,30,7.92,"config_4") for nb in nb_drone_4 ]


fig = plt.figure()
ax = fig.add_subplot(111)

ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.set_title("Comparaison des différentes configuration")
ax.set_xlabel("Nombre de drone ")
ax.set_ylabel("Temps de construction (en min) ")

plt.grid()
plt.plot(nb_drone,temps_config_0,color = "r",label = "configuration 0")
plt.plot(nb_drone,temps_config_1,label = "configuration 1")
plt.plot(nb_drone,temps_config_2,label = "configuration 2")

plt.plot(nb_drone_4,temps_config_4,label = "configuration 3")
ax.legend()
plt.show()
fig.savefig("comparaison_config.png") 
