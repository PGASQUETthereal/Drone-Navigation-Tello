import pygame
from djitellopy import Tello
import time

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trajectoire Drone")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Variables
trajectory = []  # Liste des points de la trajectoire
running = True

# Initialisation du drone Tello
drone = Tello()
drone.connect()
print(f"Battery Level: {drone.get_battery()}%")

def send_commands_to_drone(trajectory):
    """
    Envoie les commandes de vol au drone pour suivre la trajectoire.
    """
    for i in range(len(trajectory) - 1):
        x1, y1 = trajectory[i]
        x2, y2 = trajectory[i + 1]
        dx = x2 - x1
        dy = y2 - y1

        if dx > 0:
            drone.move_right(abs(dx))  # Déplacement à droite
        elif dx < 0:
            drone.move_left(abs(dx))  # Déplacement à gauche
        
        if dy > 0:
            drone.move_forward(abs(dy))  # Avancer
        elif dy < 0:
            drone.move_back(abs(dy))  # Reculer
        
        time.sleep(1)  # Pause pour stabilisation

# Boucle principale
while running:
    win.fill(WHITE)  # Efface l'écran
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Ajoute des points à la trajectoire quand la souris est cliquée
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            trajectory.append((x, y))

        # Lance le drone pour suivre la trajectoire (clic droit pour l'exemple)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            send_commands_to_drone(trajectory)

    # Dessine la trajectoire
    if len(trajectory) > 1:
        pygame.draw.lines(win, RED, False, trajectory, 2)
    
    pygame.display.update()

# Atterrissage et arrêt du drone
drone.land()
drone.end()

# Quitte Pygame
pygame.quit()
