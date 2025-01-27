from djitellopy import Tello
import cv2

drone = Tello()
drone.connect()
print(f"Batterie : {drone.get_battery()}%")

drone.streamon()
try:
    while True:
        frame = drone.get_frame_read().frame
        cv2.imshow("Flux vidéo", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print(f"Erreur : {e}")
finally:
    drone.streamoff()
    cv2.destroyAllWindows()
