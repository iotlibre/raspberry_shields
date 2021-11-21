#!/usr/bin/python
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name


import time, serial

import os
import paho.mqtt.publish as publish

import configparser

import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
        level=logging.INFO,
        handlers=[RotatingFileHandler('./logs/log_serial.log', maxBytes=1000000, backupCount=10)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')


# Parseo de variables del .ini
parser = configparser.ConfigParser()
parser.read('config_serial.ini')

# Parseo de las variables de emonCMS
listener_name = parser.get('talker','name')
mqtt_ip = parser.get('talker','mqtt_ip')
publish_time = parser.get('talker','publish_time')

if __name__ == '__main__':
    with serial.Serial(None, 115200, timeout=1) as arduino:
        arduino.port = "/dev/serie_arduino"

        while 1:
            try:
                if arduino.isOpen():
                    if  arduino.inWaiting()>0: 
                        msg_in=str(arduino.readline())
                        logging.info(msg_in)
                        msg_in= msg_in.split("\'")[1]
                        ar_sensors = msg_in.rstrip("rn\\")
                        logging.info(ar_sensors)
                        sensors = ar_sensors.split(",")
                        logging.info(sensors)                       
                        for sensor in sensors:
                            sensor_name = str(sensor.split(":")[0])
                            sensor_value = str(sensor.split(":")[1])
                            logging.info(sensor_name + ": " + sensor_value)
                            publish.single("s_sensor/" + sensor_name, sensor_value, hostname= mqtt_ip)
                else:
                    logging.info("arduino.isOpen: false")
                    time.sleep(10) #wait for serial to open
                    arduino.open()
            except Exception as ex:
                logging.info("Excepcion: "+ str(ex))
                arduino.close()
                time.sleep(10)






