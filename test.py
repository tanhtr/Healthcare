com = {'action': 'neutral', 'power': 0.0, 'time': 1668632709.9821}
met = {'met': [True, 1.0, True, 0.9, 0.0, True, 0.5, True, 0.599999, True, 0.699999, True, 0.8], 'time': 1668701328.9432}

'''
Engagement 10
Excitement 09
Focus 08
Interest 07
Relaxation 06
Stress True 05
'''

print("Mental command")
print(com['action'])


print("Performance metric")
if met['met'][1] == True:
    print("Focus")
if met['met'][7] == True:
    print("Relaxation")
if met['met'][5] == True:
    print("Stress")

from gpiozero import Buzzer
import time

buzzer = Buzzer(17)

while True:
    buzzer.on()
    print(1)
    time.sleep(3)

    buzzer.off()
    time.sleep(3)
    print(0)

import RPi.GPIO as GPIO
import time

LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

GPIO.output(LED_PIN, GPIO.HIGH)
time.sleep(1)

GPIO.output(LED_PIN, GPIO.LOW)
GPIO.cleanup()