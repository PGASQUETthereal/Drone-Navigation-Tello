import pygame
from djitellopy import TelloSwarm
import threading
import math

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
WIDTH, HEIGHT = 600, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gestion de la flotte de drones")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Variables
trajectory = []  # Liste des points
running = True
area_length = 8  # Longueur de la zone
area_width = 8   # Largeur de la zone
x0 = WIDTH / 2
y0 = HEIGHT

drone_ips = [
    #"192.168.137.132",  # Drone 1
    "192.168.137.125", # Drone 2
    "192.168.137.67",
    #"192.168.137.174",
]

# Connexion aux drones
swarm = TelloSwarm.fromIps(drone_ips)
swarm.connect()
print(swarm.get_battery())

# Fonction pour envoyer les drones sur les points définis
def send_drones_to_points():
    global trajectory
    drones_states = {drone: (x0, y0, 0, False) for drone in swarm.tellos}  # Positions initiales avec état de vol
    
    def move_to_point(drone):
        global trajectory
        while trajectory:
            point = trajectory.pop(0)  # Récupérer un point valide
            x, y = point
            print("x : ",x, "y : ",y, 'x0 : ', x0, 'y0 : ', y0)
            dx = ((-x + drones_states[drone][0]) / WIDTH) * area_width * 100
            dy = ((-y + drones_states[drone][1]) / HEIGHT) * area_length * 100
            print("dx = ", dx, " dy = ", dy)
            angle = math.degrees(math.atan2(dx, dy))
            

            print('angle = ', angle)
            print('angle_old = ', drones_states[drone][2])
            angle_todo = angle - drones_states[drone][2]
            print('angle todo = ', angle_todo)

            if angle_todo > 180:
                angle_todo -= 360
            elif angle_todo < -180:
                angle_todo += 360

            if not drones_states[drone][3]:
                print(drone.get_battery())
                drone.takeoff()
                drone.move_up(100)

            
             # Tourner dans la direction optimale
            if angle_todo > 0:
                drone.rotate_counter_clockwise(int(angle_todo))
            elif angle_todo < 0:
                drone.rotate_clockwise(int(-angle_todo))
            distance = int(math.sqrt(dx**2 + dy**2))
            if distance < 500:
                drone.move_forward(int(math.sqrt(dx**2 + dy**2)))
            elif distance >= 500:
                drone.move_forward(int(distance/2))
                drone.move_forward(int(distance/2))
            
            drones_states[drone] = (x, y, angle, True)  # Mise à jour de la position, de l'angle et de l'état de vol

        # Retourner à la base
        home_x, home_y = x0, y0
        final_angle = 180 - drones_states[drone][2]     
        final_dx = - home_x/ WIDTH * area_width * 100 + drones_states[drone][0]
        final_dy = - home_y/HEIGHT * area_length * 100 + drones_states[drone][1]
        drone.rotate_counter_clockwise(int(final_angle))
        distance = int(math.sqrt(dx**2 + dy**2))
        if distance < 500:
            drone.move_forward(int(math.sqrt(dx**2 + dy**2)))
        elif distance < 1000:
            drone.move_forward(int(distance/2))
            drone.move_forward(int(distance/2))
        elif distance >=1000:
            drone.move_forward(int(distance/3))
            drone.move_forward(int(distance/3))
            drone.move_forward(int(distance/3))
        
        drone.flip_forward()
        
        drone.land()
        drones_states[drone] = (home_x, home_y, 0, False)  # Mise à jour après l'atterrissage

    threads = []
    for drone in swarm.tellos:
        t = threading.Thread(target=move_to_point, args=(drone,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

# Zone de dessin pour la trajectoire
DRAW_ZONE = pygame.Rect(0, 0, WIDTH, HEIGHT - 100)

# Boucle principale
while running:
    win.fill(WHITE)
    pygame.draw.rect(win, GRAY, DRAW_ZONE, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and DRAW_ZONE.collidepoint(event.pos):
            trajectory.append(event.pos)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            threading.Thread(target=send_drones_to_points, daemon=True).start()

    for point in trajectory:
        pygame.draw.circle(win, RED, point, 5)  # Affichage des points restants
        #print(point)

    pygame.display.update()

pygame.quit()
swarm.end()
