#!/usr/bin/env python


import time
import os
import paho.mqtt.client as mqtt

import configparser

import logging
from logging.handlers import RotatingFileHandler


import json



# Para obtener mas detalle: level=logging.DEBUG
# Para comprobar el funcionamiento: level=logging.INFO
logging.basicConfig(
        level=logging.INFO,
        handlers=[RotatingFileHandler('./logs/log_outputs.log', maxBytes=1000000, backupCount=10)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

# Parseo de variables del .ini
parser = configparser.ConfigParser()
parser.read('config_outputs.ini')

# Parseo de las variables de emonCMS
mqtt_topic = parser.get('listener','topic')
listener_name = parser.get('listener','name')
mqtt_ip = parser.get('listener','mqtt_ip')
mqtt_login = parser.get('listener','mqtt_login')
mqtt_password = parser.get('listener','mqtt_password')



def on_connect(client, obj, flags, rc):
    logging.debug("rc: " + str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    data_string = msg.payload
    
    name_1 = "C3.3"
    value_1 = "0"
    decoded_ok = 1
    
    logging.info("emoncms payload:")
    logging.info(data_string)

    decoded = json.loads(data_string)
    
    try:
        name_1=     str(decoded["name"])
        value_1 =   str(decoded["value"])

    except:
        logging.info("error in decoded")
        decoded_ok = 0
    
    if (name_1[0] == 'A') and (decoded_ok == 1):

        script_A = "sudo /home/pi/test/analog/set-analog-output {0} {1}"
        script_A =script_A.format(name_1,value_1)        
        os.system(script_A)
        logging.info(script_A)
        
    elif (name_1[0] == 'Q') and (decoded_ok == 1):

        script_Q = "sudo /home/pi/test/analog/set-digital-output {0} {1}"
        script_Q =script_Q.format(name_1,value_1)        
        os.system(script_Q)
        logging.info(script_Q)
        
    else:
        logging.info("Error in parameters")
    
    
def on_disconnect(client, userdata, rc):
    if rc != 0:
       result="Unexpected disconnection"
       logging.info("Unexpected disconnection")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_diconnect = on_disconnect


client.username_pw_set(mqtt_login,mqtt_password)
client.connect(mqtt_ip, 1883, 60)
client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=False)

