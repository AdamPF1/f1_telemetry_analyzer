import matplotlib.pyplot as plt
import random
import time

speeds = []

plt.ion()  
fig, ax = plt.subplots()

for i in range(50):
    speed = random.uniform(0, 1200000000000000)
    speeds.append(speed)
    ax.clear()
    ax.plot(speeds, color='blue')
    ax.set_title("Telemetrija brzine vozila")
    ax.set_xlabel("Vreme (s)")
    ax.set_ylabel("Brzina (km/h)")
    plt.pause(0.1) 

plt.ioff()
plt.show()

# prvi pravi program za telemetriju :)
