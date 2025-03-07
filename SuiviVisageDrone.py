from djitellopy import Tello
import cv2
import threading
import numpy as np

from numpy import hanning

# Dimensions de l'image
FRAME_WIDTH = 960
FRAME_HEIGHT = 720
CENTER_X = FRAME_WIDTH // 2
CENTER_Y = FRAME_HEIGHT // 2



# Tentative de connexion au drone
try:
    drone = Tello()
    drone.connect()
    print(f"Battery Level: {drone.get_battery()}%")
    drone.streamon()
    drone_connected = True
except Exception as e:
    print("Drone non connecté :", e)


def send_commands_to_drone(X, Y, endX, endY, nb_detection):
    """
    Envoie des commandes au drone pour suivre le visage détecté.
    """
    if not drone_connected:
        print("Drone non connecté")
        return

    # Calcul de la position du centre du visage
    face_center_x = X + (endX - X)/2
    face_center_y = Y + (endY - Y)/2

    # Calcul des écarts entre le centre du visage et le centre de l'image
    delta_x = face_center_x - CENTER_X
    delta_y = face_center_y - CENTER_Y
 
    left_right_velocity = 0
    forward_backward_velocity = 0
    up_down_velocity = 0
    yaw_velocity = 0

    
    if nb_detection !=0 :
        yaw_velocity = int(delta_x*0.2)

        up_down_velocity = int(-delta_y*0.2)

        face_width = endX - X

        forward_backward_velocity = int(-(face_width-100) * 0.5)


    print("Vitesse : yaw = ", yaw_velocity, "up_down = ", up_down_velocity, "for_back = ", forward_backward_velocity)
    
    #Envoie de la commande au drone
    drone.send_rc_control(left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity)


def takeoff():
    try:
        battery = drone.get_battery()
        print(f"Batterie : {battery}%")
        
        if battery < 20:
            print("Batterie trop faible pour décoller.")
            return
        
        height = drone.get_height()
        print(f"Hauteur actuelle : {height} cm")
        
        if height == 0:
            drone.takeoff()
    except Exception as e:
        print("Erreur lors du décollage :", e)


face_net = cv2.dnn.readNetFromCaffe(
    "C:/Users/tiger/Documents/Cours/3A/ProjetDrone/deploy.prototxt",
    "C:/Users/tiger/Documents/Cours/3A/ProjetDrone/res10_300x300_ssd_iter_140000.caffemodel"
)


has_taken_off = False

while True:
        # Capture d'une image du drone
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convertir l'image en niveaux de gris pour la détection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Pour détecter des visages
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        face_net.setInput(blob)
        detections = face_net.forward()

        # Initialisation de la variable pour suivre le plus grand visage
        largest_face = None
        max_area = 0
        nb_faces = 0

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]  # Confiance du modèle
            if confidence > 0.6:  # Seulement les visages fiables
                box = detections[0, 0, i, 3:7] * np.array([FRAME_WIDTH, FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT])
                (startX, startY, endX, endY) = box.astype("int")
                nb_faces += 1
                # Calcul de la surface du visage
                area = (endX - startX) * (endY - startY)
                
                # Vérifie si c'est le plus grand visage détecté
                if area > max_area & nb_faces<1:
                    max_area = area
                    largest_face = (startX, startY, endX, endY)

        print("nb_faces : ",nb_faces)
        # Si un visage a été détecté, dessine-le et envoie les commandes
        if largest_face:
            (startX, startY, endX, endY) = largest_face
            cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)
            threading.Thread(target=send_commands_to_drone, args=(startX, startY, endX, endY, nb_faces), daemon=True).start()
        else :
            threading.Thread(target=send_commands_to_drone, args=(0,0,0,0, nb_faces), daemon=True).start()
        cv2.imshow('Détection de Visage', frame)
                
         # Vérifie si le drone n'a pas encore décollé
        if not has_taken_off:
            takeoff()             # Décollage après l'ouverture de la fenêtre
            has_taken_off = True  # Marque le drapeau pour éviter de redécoller

        

        #threading.Thread(target = takeoff, args=(), daemon=True).start()
        # Quitter le programme si 'q' est pressé
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# Atterrissage et arrêt du drone si connecté
if drone_connected:
    try:
        drone.land()
        drone.streamoff()
        drone.end()  # Ferme correctement la connexion
        drone_connected = False

        # Reconnexion propre
        drone = Tello()
        drone.connect()
        drone.streamon()
        drone_connected = True
    except Exception as e:
        print("Erreur lors de l'arrêt du drone :", e)

# Quitte Pygame et fenètre stream
cv2.destroyAllWindows()