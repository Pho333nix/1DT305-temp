from machine import ADC
from machine import Pin
import pycom
import time
from network import WLAN
import urequests as requests
import machine
import struct
import keys
pycom.heartbeat(False)

#UBIDOS TOKEN

TOKEN=keys.TOKEN
DELAY=60 # delay for 1 minute

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.INT_ANT)

# Assign your Wi-Fi credentials
wlan.connect(keys.SSID, auth=(WLAN.WPA2, keys.password), timeout=5000)

#Wifi connection attempt
while not wlan.isconnected ():
    print("attempting to connect to wifi")
    pycom.rgbled(0xFF0000)  # Red
    time.sleep(1)
    pycom.rgbled(0xFF0000)  # Red
    machine.idle()
print("Connected to Wifi\n")
pycom.heartbeat(True)

# Builds the json to send the request
def build_json(variable1, value1, variable2, value2, variable3, value3):
    try:
        lat = 59.420  # latitude
        lng = 17.839  # longtitude

        # data array creation
        data = {variable1: {"value": value1},
                variable2: {"value": value2, "context": {"lat": lat, "lng": lng}}, # value - main information, context - additional
                variable3: {"value": value3}}
        return data
    except:
        return None

# Sends the request. Please reference the REST API reference https://ubidots.com/docs/api/
def post_var(device, value1, value2, value3):
    try:
        url = "https://industrial.api.ubidots.com/"
        url = url + "api/v1.6/devices/" + device
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        data = build_json("pulseData", value1, "position", value2, "rawData", value3)
        if data is not None:
            print(data)
            req = requests.post(url=url, headers=headers, json=data)
            return req.json()
        else:
            pass
    except:
        pass

PulseSensorPin= 'P16' # This pulse sensor is going to be connected to P16.

pulsePin = Pin(PulseSensorPin, mode=Pin.IN)  # set up pin mode to input
#
adc = ADC(bits=10)             # create an ADC object bits=10 means range 0-1024 the lower value the less light detected
apin = adc.channel(attn=ADC.ATTN_11DB, pin=PulseSensorPin)   # create an analog pin on P16;  attn=ADC.ATTN_11DB measures voltage from 0.1 to 3.3v

alpha = 0.75
reset=0.0
prvVal=0.0
sum = 0.0
pos = 0

while True:
    rawVal = apin()
    val =  alpha * prvVal + (1-alpha) * rawVal
    sum = sum + val
    pos +=1
    change = val - prvVal
    print("val", val, change)
    prvVal=val
    time.sleep(0.1)

    post_var("dev1", val, 1, rawVal)  # send data to UBIDOTS
    time.sleep(DELAY)
