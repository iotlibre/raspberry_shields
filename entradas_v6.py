import subprocess
import time
import os
import paho.mqtt.publish as publish

import configparser

import logging
from logging.handlers import RotatingFileHandler


# Para obtener mas detalle: level=logging.DEBUG
# Para comprobar el funcionamiento: level=logging.INFO
logging.basicConfig(
        level=logging.INFO,
        handlers=[RotatingFileHandler('./logs/log_inputs.log', maxBytes=1000000, backupCount=10)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

# Parseo de variables del .ini
parser = configparser.ConfigParser()
parser.read('config_inputs.ini')

# Parseo de las variables de emonCMS
listener_name = parser.get('talker','name')
mqtt_ip = parser.get('talker','mqtt_ip')
a_sensors_ = parser.get('talker','analogic')
d_sensors_ = parser.get('talker','digital')
publish_time = parser.get('talker','publish_time')

a_sensors = a_sensors_.split(',')
d_sensors = d_sensors_.split(',')


logging.info(a_sensors)
logging.info(d_sensors)



if __name__ == "__main__":
    logging.info("Start entradas")
    while 1:
        for sensor in a_sensors:
            result ="ok"
            xout="no_response"
            try:
                x = subprocess.run(["/home/pi/test/analog/get-analog-input",sensor], stdout=subprocess.PIPE, text=True)
                xout = x.stdout

            except:
                result = "time_out"
                logging.info("time_out get-analog-input")
            
            if result == 'ok':
                logging.info(sensor)
                logging.info(xout)
                publish.single("a_sensor/" + sensor, xout, hostname=mqtt_ip)  
                
        for sensor in d_sensors:
            result ="ok"
            x="no_response"
            try:
                x = subprocess.run(["/home/pi/test/analog/get-digital-input",sensor], stdout=subprocess.PIPE, text=True)
                xout = x.stdout
                
            except:
                result = "time_out"
                logging.info("time_out get-digital-input")
                
            if result == 'ok':
                logging.info(sensor)
                logging.info(xout)
                publish.single("d_sensor/" + sensor, xout, hostname=mqtt_ip)  
                

        
        time.sleep(int(publish_time))
            





