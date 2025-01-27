import cv2

# Charger le modèle de détection de visages (Cascade Classifier)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialiser la capture vidéo (0 pour la webcam intégrée)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur : Impossible d'accéder à la webcam.")
    exit()

try:
    while True:
        # Capture d'une image de la webcam
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de lire l'image.")
            break

        # Convertir l'image en niveaux de gris pour la détection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Détection des visages
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Dessiner des rectangles autour des visages détectés
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Afficher l'image avec les rectangles
        cv2.imshow('Détection de Visage', frame)

        # Quitter le programme si 'q' est pressé
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Arrêt par l'utilisateur.")

finally:
    # Libérer les ressources
    cap.release()
    cv2.destroyAllWindows()
