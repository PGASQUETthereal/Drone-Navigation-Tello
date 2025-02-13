from djitellopy import TelloSwarm

# Définition des IP des drones
swarm = TelloSwarm.fromIps([
    "192.168.137.24",  # Drone 1
    "192.168.137.147"  # Drone 2
])

swarm.connect()
swarm.takeoff()

# Faire un carré dans un sens pour Drone 1 et dans l'autre pour Drone 2
def square_movement(i, tello):
    for _ in range(4):  # 4 côtés du carré
        tello.move_forward(50)
        if i == 0:  # Drone 1 tourne à droite
            tello.rotate_clockwise(90)
        else:  # Drone 2 tourne à gauche
            tello.rotate_counter_clockwise(90)

swarm.parallel(square_movement)

swarm.tellos[0].flip_forward()
swarm.tellos[1].flip_back()

swarm.land()

# Affichage du niveau de batterie
for i, tello in enumerate(swarm.tellos):
    print(f"Drone {i+1} Battery: {tello.get_battery()}%")

swarm.end()
