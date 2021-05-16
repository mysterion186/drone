import matplotlib.pyplot as plt 



class Drone :
    def __init__(self,state,action_time):
        self.state = state              #état du drone, booléen True => en fonctionnement False en recharge 
        self.action_time = action_time  #indique depuis combien de temps le drone fait une action 
        #(recharge si state = False ou travail si state = True)
    
    #inverse l'état du drone
    def toggle_state(self):
        self.state = not self.state
    
    #renvoir True si on ne peut pas faire d'aller retour, False si on peut
    def not_reachable(self,drone_autonomie,travel_time,charge_time):
        return drone_autonomie <= self.action_time + 2*travel_time 
    
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
def time_construc(d,vit_drone):
    return d/vit_drone 

#crée la config pour un nombre de drone multiple de 3 
def config_multiple(nb_drone):
    list_drone = [Drone(True,0) for k in range(nb_drone)]
    for drone in list_drone[int(nb_drone/3):]:
        drone.state = not drone.state 
    return list_drone

#crée la config pour un nombre de drone paire
def config_paire(nb_drone):
    list_drone = [Drone(True,0) for k in range(nb_drone)]
    for drone in list_drone[int(nb_drone/2):]:
        drone.state = not drone.state
    return list_drone

#retourne une liste de configuration optimale de drone
#soit nb_drone est un multiple de 3 soit un nombre paire (si impair on le transforme en nb pair)
def config_drone(nb_drone):
    list_drone = []
    #cas de figure où me nb de drone est un multiple de 3
    if nb_drone%3 == 0 :
        list_drone = config_multiple(nb_drone)
    else : 
        #si nb_drone est impaire on le transforme en un nombre paire
        if nb_drone%2 !=0 :
            nb_drone-=1
            if nb_drone%3 == 0 :
                list_drone=config_multiple(nb_drone)
            else : 
                list_drone = config_paire(nb_drone)
        else :
            list_drone = config_paire(nb_drone)
    return list_drone 

#fonction principale qui va nous retourner le temps de construction du mur 
#cf le fichier notion pour connaître la signification des variables
def main(p_drone,p_max_drone,p_parachute,p_sys,volume_construction,nb_drone,dist,vit_drone,charge_time,rau_beton,bat_capacity,bat_discharge,avg_amp):
    #initiatilisation des variables
    temps,volume = 0,0                                                                     # initialisation du temps et du volume du béton 
    travel_time = time_construc(dist,vit_drone)                                            # temps de parcourt entre le béton et le mur (ou l'inverse, juste un aller)
    autonomie = drone_auto(bat_capacity,bat_discharge,avg_amp)                             # autonomie du drone 
    p_beton = p_max_drone-(p_drone+p_parachute+p_sys)                                      # le poids en béton que le drone peut soulever
    v_beton  = p_beton/rau_beton                                                           # volume de béton qu'un drone peut soulever
    list_drone = config_drone(nb_drone)                                                    # nous donne une liste avec les drones comme ça on pourra direct appeler le drone
    #nous donnes les informations capitales qui vont nous permettre de faire notre calcul
    print(f"Les différentes informations sont :\nLe temps séparant le mur au béton {travel_time}\nle volume de béton {v_beton}\nune autonomie de {autonomie}\n")

    #logique principale
    while volume <= volume_construction:
        #le drone a réussi à faire son aller-retour
        temps+= 2*travel_time                                                              # on utilise l'aller-retour pour simplifier les calculs
        active_drone = 0
        for drone in list_drone:                                                           # on détermine le nombre de drone actif 
            if drone.state :
                active_drone+=1 
        volume += active_drone*v_beton                                                     # on ajoute le volume de béton nécessaire 

        #mise à jour du temps pour tous le monde peu importe l'état du drone
        for drone in list_drone :
            drone.action_time += 2*travel_time              

        #choix de quelle "groupe" de drone on envoie construire le mur

        #après l'aller-retour on check voir si le drone peut en refaire un autre pour déposer du ciment
        if nb_drone%3 == 0 :                                                               # cas le nombre de drone est un multiple de 3 
            pass
        else :                                                                             # pas la peine d'être plus précis, car list_drone sera forcément paire
            if list_drone[0] :                                                             # si c'est le groupe 1 qui est actif 
                if list_drone[0].not_reachable(autonomie,travel_time,charge_time) :
                    for i in range(len(list_drone)) :
                        #si les drones sont rechargé alors seulement on les envoie construire le mur
                        if i >= int(len(list_drone)/2) :                                   # faire des tests pour voir si c'est une inégalité stricte ou pas
                            if  list_drone[i].action_time >= charge_time:                  # si le drone est chargé on peut l'envoyer en mission
                                list_drone[i].toggle_state()
                                list_drone[i].reset_time()
                        else : 
                            list_drone[i].toggle_state()
                            list_drone[i].reset_time()  
            elif list_drone[-1]:                                                           # si c'est le groupe 2 qui est actif 
                if list_drone[-1].not_reachable(autonomie,travel_time,charge_time) : 
                    for i in range(len(list_drone)) :
                        #si les drones sont rechargé alors seulement on les envoie construire le mur
                        if i <= int(len(list_drone)/2) :                                   # faire des tests pour voir si c'est une inégalité stricte ou pas
                            if  list_drone[i].action_time >= charge_time:                  # si le drone est chargé on peut l'envoyer en mission
                                list_drone[i].toggle_state()
                                list_drone[i].reset_time()
                        else : 
                            list_drone[i].toggle_state()
                            list_drone[i].reset_time() 
            else :                                                                         # cas où on a les 2 en attentes 
                if  list_drone[-1].action_time >= charge_time:                             # si les drones du groupe 2 sont rechargés on les envoie
                    for drone in list_drone[int(len(list_drone)/2):]:
                        drone.toggle_state()
                        drone.reset_time()
                elif list_drone[0].action_time >+ charge_time :                            # si les drones du groupe 1 sont rechargés on les envoie
                    for drone in list_drone[0:int(len(list_drone)/2)] :
                        drone.toggle_state()
                        drone.reset_time()          
    return temps 

"p_drone,p_max_drone,p_parachute,p_sys,volume_construction,nb_drone,dist,vit_drone,charge_time,rau_beton,bat_capacity,bat_discharge,avg_amp"
#toutes les unités sont selon le truc du système international
dist = 5 #m
rau_beton = 2400 #Kg/m^3 https://travauxbeton.fr/densite-ciment/ 
volume_contruction = 1 #m^3 

