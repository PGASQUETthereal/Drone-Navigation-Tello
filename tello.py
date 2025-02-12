from djitellopy import TelloSwarm

# Define the IP addresses of the drones
swarm = TelloSwarm.fromIps([
    "192.168.137.215",  # Replace with actual IP of drone 1
    "192.168.137.216"   # Replace with actual IP of drone 2
])

swarm.connect()

swarm.takeoff()
swarm.land()

#swarm.parallel(lambda tello: tello.move_forward(50))  # Move all drones forward
# Get battery levels of all drones
for i, tello in enumerate(swarm.tellos):
    print(f"Drone {i+1} Battery: {tello.get_battery()}%")

swarm.end()

