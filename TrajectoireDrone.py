import pygame
from djitellopy import Tello
import time
import math
import cv2
import threading

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
GRAY = (200, 200, 200)

# Variables
trajectory = []  # Liste des points de la trajectoire
running = True

drone = None  # Initialisation du drone (sera configuré plus tard)
drone_connected = False

# Dimensions de l'air (en mètres)
area_length = 5  # Valeur par défaut
area_width = 5  # Valeur par défaut

# Tentative de connexion au drone
try:
    drone = Tello()
    drone.connect()
    print(f"Battery Level: {drone.get_battery()}%")
    drone.streamon()
    drone_connected = True
except Exception as e:
    print("Drone non connecté :", e)


import math

def send_commands_to_drone(trajectory):
    """
    Envoie les commandes de vol au drone pour suivre la trajectoire ou affiche les commandes si le drone n'est pas connecté.
    """
    if drone_connected:
        drone.takeoff()
    angle = 0  # Angle initial (en degrés)

    for i in range(len(trajectory) - 1):
        x1, y1 = trajectory[i]
        x2, y2 = trajectory[i + 1]

        # Conversion des points en distances (en cm)
        dx = int((x2 - x1) * area_width / WIDTH * 100)  # Longueur en cm
        dy = int((y1 - y2) * area_length / HEIGHT * 100)  # Hauteur en cm
        print(f"dx={dx}, dy={dy}")

        # Calcul de la distance et de l'angle
        distance = math.sqrt(dx**2 + dy**2)  # Distance entre les points
        alpha = math.degrees(math.atan2(dx, dy))  # Angle cible en degrés
        print(f"distance = {distance}, alpha (angle cible) = {alpha}")

        # Calcul de l'angle de rotation nécessaire
        rotation_angle =  angle - alpha
        if rotation_angle > 180:
            rotation_angle -= 360
        elif rotation_angle < -180:
            rotation_angle += 360

        print(f"Rotation nécessaire = {rotation_angle}")

        if drone_connected:
            try:
                # Tourner dans la direction optimale
                if rotation_angle > 0:
                    drone.rotate_counter_clockwise(int(rotation_angle))
                elif rotation_angle < 0:
                    drone.rotate_clockwise(int(-rotation_angle))

                # Mettre à jour l'angle actuel
                angle = alpha

                # Avancer sur la distance calculée
                drone.move_forward(int(distance))  # Convertir en cm
                #time.sleep(1)  # Pause pour stabilisation
            except Exception as e:
                print("Erreur lors de l'envoi des commandes au drone :", e)
        else:
            # Affichage des commandes simulées
            print(f"Commande simulée: rotation={rotation_angle}, avancer={distance}")

    if drone_connected:
        try:
            drone.land()
        except Exception as e:
            print("Erreur lors de l'atterrissage :", e)
    drone.land()

# Création de polices et des champs de saisie
font = pygame.font.Font(None, 36)
input_length = pygame.Rect(10, HEIGHT - 50, 100, 30)
input_width = pygame.Rect(200, HEIGHT - 50, 100, 30)
button_send = pygame.Rect(WIDTH - 150, HEIGHT - 50, 140, 40)

# Zone de dessin pour la trajectoire
DRAW_ZONE = pygame.Rect(0, 0, WIDTH, HEIGHT - 100)

input_active_length = False
input_active_width = False
text_length = str(area_length)
text_width = str(area_width)

# Boucle principale
while running:
    win.fill(WHITE)  # Efface l'écran

    # Dessine la zone de dessin
    pygame.draw.rect(win, GRAY, DRAW_ZONE, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Gestion des clics sur les champs de saisie
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_length.collidepoint(event.pos):
                input_active_length = True
                input_active_width = False
            elif input_width.collidepoint(event.pos):
                input_active_length = False
                input_active_width = True
            elif button_send.collidepoint(event.pos):
                # Lancer la fonction dans un thread séparé
                threading.Thread(target=send_commands_to_drone, args=(trajectory,), daemon=True).start()
            elif DRAW_ZONE.collidepoint(event.pos):
                # Ajoute des points à la trajectoire quand la souris est cliquée
                if event.button == 1:  # Clic gauche
                    x, y = pygame.mouse.get_pos()
                    print("(x,y) =", x , y)  
                    trajectory.append((x, y))
            else:
                input_active_length = False
                input_active_width = False


        # Gestion de la saisie clavier pour les champs actifs
        if event.type == pygame.KEYDOWN:
            if input_active_length:
                if event.key == pygame.K_BACKSPACE:
                    text_length = text_length[:-1]
                elif event.unicode.isdigit():
                    text_length += event.unicode
                if text_length != "" :
                    area_length = int(text_length)
            if input_active_width:
                if event.key == pygame.K_BACKSPACE:
                    text_width = text_width[:-1]
                elif event.unicode.isdigit():
                    text_width += event.unicode
                if text_width != "" :
                    area_width = int(text_width)

    # Dessine la trajectoire
    if len(trajectory) > 1:
        pygame.draw.lines(win, RED, False, trajectory, 2)

    # Dessine les champs de saisie et le bouton
    pygame.draw.rect(win, GRAY, input_length, 2)
    pygame.draw.rect(win, GRAY, input_width, 2)
    pygame.draw.rect(win, GRAY, button_send)

    text_surface_length = font.render(text_length, True, BLACK)
    text_surface_width = font.render(text_width, True, BLACK)
    button_text = font.render("Envoyer", True, BLACK)

    win.blit(text_surface_length, (input_length.x + 5, input_length.y + 5))
    win.blit(text_surface_width, (input_width.x + 5, input_width.y + 5))
    win.blit(button_text, (button_send.x + 20, button_send.y + 5))

    label_length = font.render("Longueur (m):", True, BLACK)
    label_width = font.render("Largeur (m):", True, BLACK)

    win.blit(label_length, (10, HEIGHT - 80))
    win.blit(label_width, (200, HEIGHT - 80))

    pygame.display.update()

    # Récupérer le flux vidéo sous forme d'image
    frame = drone.get_frame_read().frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Afficher l'image avec OpenCV
    cv2.imshow("Flux vidéo du drone", frame)

        # Quitter avec 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Atterrissage et arrêt du drone si connecté
if drone_connected:
    try:
        drone.land()
        drone.streamoff()
        drone.end()
    except Exception as e:
        print("Erreur lors de l'arrêt du drone :", e)

# Quitte Pygame et fenètre stream
pygame.quit()
cv2.destroyAllWindows()