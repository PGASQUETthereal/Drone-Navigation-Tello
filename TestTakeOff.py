#import module for tello:
from djitellopy import tello

import time

#Start Connection With Drone
Drone = tello.Tello()
Drone.connect()

#Get Battery Info
print("Batterie : " + str(Drone.get_battery()))

Drone.takeoff()
print("Baromètre : " + str(Drone.get_barometer()))
print("State : " + str(Drone.get_current_state()))





Drone.flip_back()

Drone.move_forward(500)

Drone.flip_forward()

Drone.land()