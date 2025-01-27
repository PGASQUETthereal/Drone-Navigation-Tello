import pygame
from djitellopy import Tello
import cv2
import numpy as np
import time
import math

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
tracking_mode = False  # Mode suivi d'objet par couleur

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

# Paramètres pour la détection de couleur (Rouge par défaut)
LOWER_BOUND = np.array([0, 120, 70])  # Limite basse pour la couleur (HSV)
UPPER_BOUND = np.array([10, 255, 255])  # Limite haute pour la couleur (HSV)
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
TOLERANCE = 50  # Tolérance pour le suivi

def track_color():
    """
    Fonction pour le suivi d'objet basé sur la couleur avec affichage en temps réel du retour caméra
    """
    if not drone_connected:
        print("Drone non connecté, impossible de démarrer le suivi.")
        return

    try:
        while tracking_mode:
            # Capture une image du flux vidéo
            frame = drone.get_frame_read().frame
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)

            # Conversion de BGR en HSV
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            # Masquage pour la couleur cible
            mask = cv2.inRange(hsv, LOWER_BOUND, UPPER_BOUND)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # Trouver les contours
            contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            center = None

            if len(contours) > 0:
                # Trouver le plus grand contour
                c = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # Contrôle du drone
                error_x = center[0] - CENTER_X
                error_y = CENTER_Y - center[1]  # Inversé car l'origine est en haut à gauche

                # Déplacement horizontal
                if abs(error_x) > TOLERANCE:
                    if error_x > 0:
                        drone.move_right(20)
                    else:
                        drone.move_left(20)

                # Déplacement vertical
                if abs(error_y) > TOLERANCE:
                    if error_y > 0:
                        drone.move_up(20)
                    else:
                        drone.move_down(20)

            # Affichage de l'image et du masque
            mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # Convertir le masque en BGR pour affichage
            combined = np.hstack((frame, mask_bgr))  # Combiner l'image et le masque côte à côte
            cv2.imshow("Tello Tracking", combined)

            # Quitter le mode suivi si 'q' est pressé
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print("Erreur dans le suivi de couleur :", e)

    finally:
        cv2.destroyAllWindows()

# Création de polices et des champs de saisie
font = pygame.font.Font(None, 36)
input_length = pygame.Rect(10, HEIGHT - 50, 100, 30)
input_width = pygame.Rect(120, HEIGHT - 50, 100, 30)
button_send = pygame.Rect(WIDTH - 150, HEIGHT - 50, 140, 40)
button_track = pygame.Rect(WIDTH - 300, HEIGHT - 50, 140, 40)  # Nouveau bouton pour le tracking

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
                send_commands_to_drone(trajectory)
            elif button_track.collidepoint(event.pos):
                tracking_mode = not tracking_mode
                if tracking_mode:
                    print("Mode suivi activé")
                    track_color()
                else:
                    print("Mode suivi désactivé")
            elif DRAW_ZONE.collidepoint(event.pos):
                # Ajoute des points à la trajectoire quand la souris est cliquée
                if event.button == 1:  # Clic gauche
                    x, y = pygame.mouse.get_pos()
                    print("(x,y) =", x, y)
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

    # Dessine les champs de saisie et les boutons
    pygame.draw.rect(win, GRAY, input_length, 2)
    pygame.draw.rect(win, GRAY, input_width, 2)
    pygame.draw.rect(win, GRAY, button_send)
    pygame.draw.rect(win, GRAY, button_track)

    text_surface_length = font.render(text_length, True, BLACK)
    text_surface_width = font.render(text_width, True, BLACK)
    button_text_send = font.render("Envoyer", True, BLACK)
    button_text_track = font.render("Suivi", True, BLACK)

    win.blit(text_surface_length, (input_length.x + 5, input_length.y + 5))
    win.blit(text_surface_width, (input_width.x + 5, input_width.y + 5))
    win.blit(button_text_send, (button_send.x + 20, button_send.y + 5))
    win.blit(button_text_track, (button_track.x + 20, button_track.y + 5))

    label_length = font.render("Longueur (m):", True, BLACK)
    label_width = font.render("Largeur (m):", True, BLACK)

    win.blit(label_length, (10, HEIGHT - 80))
    win.blit(label_width, (120, HEIGHT - 80))

    pygame.display.update()

# Atterrissage et arrêt du drone si connecté
if drone_connected:
    try:
        drone.land()
        drone.streamoff()
        drone.end()
    except Exception as e:
        print("Erreur lors de l'arrêt du drone :", e)

# Quitte Pygame
pygame.quit()
