#!/usr/bin/env python
#===============================================================================
# Copyright (C) 2018 Paul van Veen
#
# This file is part of ginlong-influxdb.
#
# R2_Control is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# R2_Control is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ginlong-influxdb.  If not, see <http://www.gnu.org/licenses/>.
#
# tested with firmware version  H4.01.51Y4.0.0W1.0.57(2017-12-211-D)
#===============================================================================

import paho.mqtt.publish as publish
import socket
import binascii
import time
import sys
import string
import ConfigParser
import io
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError

with open("config.ini") as f:
        sample_config = f.read()
config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(sample_config))

###########################
# Variables
listen_address = config.get('DEFAULT', 'listen_address') # What address to listen to (0.0.0.0 means it will listen on all addresses)
listen_port = int(config.get('DEFAULT', 'listen_port')) # Port to listen on
client_id = config.get('MQTT', 'client_id') # MQTT Client ID
mqtt_server = config.get('MQTT', 'mqtt_server') # MQTT Address
mqtt_port = int(config.get('MQTT', 'mqtt_port')) # MQTT Port
influx_server = config.get('INFLUX', 'influxdb_server') # Ifluxdb server adress
influx_port = int(config.get('INFLUX', 'influxdb_port') # Influxdb port
influx_db = config.get('INFLUX', 'influxdb_databasename') # influxdb name
influx_user = config.get('INFLUX', 'influxdb_user') # influxdb gebruikersnaam
influx_passwd = config.get('INFLUX', 'influxdb_password') # influxdb login


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((listen_address, listen_port))
sock.listen(1)


while True:
    # Wait for a connection
    if __debug__:
        print 'waiting for a connection'
    conn,addr = sock.accept()
    try:
        #print >>sys.stderr, 'connection from', addr
        # while True:
            rawdata = conn.recv(1000) # Read in a chunk of data
            hexdata = binascii.hexlify(rawdata) # Convert to hex for easier processing
	    timestamp = (time.strftime("%F %H:%M"))
	    if(len(hexdata) == 276):
                timestamp = (time.strftime("%F %H:%M")) # get date time
                msgs = []
                serial = binascii.unhexlify(str(hexdata[30:60])) # Serial number is used for MQTT path, allowing multiple inverters to connect to a single instance
                if __debug__:
                    print 'Hex data: %s' % hexdata
                    print "Serial %s" % serial
                    print "Length %s" % len(hexdata)
                mqtt_topic = ''.join([client_id, "/", serial, "/"]) # Create the topic base using the client_id and serial number
                if __debug__:
                    print >>sys.stderr, 'MQTT Topic: ', mqtt_topic

                ##### Vpv1
                vpv1 = float(int(hexdata[66:70],16))/10
                if __debug__:
                    print >>sys.stderr, 'vpv1: ', vpv1
                msgs.append((mqtt_topic + "Vpv1", vpv1, 0, False))

		##### Vpv2
                vpv2 = float(int(hexdata[70:74],16))/10
                if __debug__:
                    print >>sys.stderr, 'vpv2: ', vpv2
                msgs.append((mqtt_topic + "Vpv2", vpv2, 0, False))

                ##### Ipv1
                ipv1 = float(int(hexdata[78:82],16))/10
                if __debug__:
                    print >>sys.stderr, 'ipv1: ', ipv1
                msgs.append((mqtt_topic + "Ipv1", ipv1, 0, False))

                ##### Ipv2
                ipv2 = float(int(hexdata[82:86],16))/10
                if __debug__:
                    print >>sys.stderr, 'ipv2: ', ipv2
                msgs.append((mqtt_topic + "Ipv2", ipv2, 0, False))

                ##### Vac1
                vac1 = float(int(hexdata[102:106],16))/10
                if __debug__:
                    print >>sys.stderr, 'vac1: ', vac1
                msgs.append((mqtt_topic + "Vac1", vac1, 0, False))

                ##### Vac2
                #vac2 = float(int(hexdata[106:109],16))/10 if __debug__:
                #    print >>sys.stderr, 'vac2: ', vac2 
                #msgs.append((mqtt_topic + "Vac2", vac2, 0, False))

                ##### Vac3
                #vac3 = float(int(hexdata[110:113],16))/10 if __debug__:
                #    print >>sys.stderr, 'vac3: ', vac3 
                #msgs.append((mqtt_topic + "Vac3", vac3, 0, False))

		##### Iac1
                iac1 = float(int(hexdata[88:92],16))/10
                if __debug__:
                    print >>sys.stderr, 'iac1: ', iac1
                msgs.append((mqtt_topic + "Iac1", iac1, 0, False))

		##### Iac2
                #iac2 = float(int(hexdata[124:128],16))/10 if __debug__:
                #    print >>sys.stderr, 'iac2: ', iac2 
                #msgs.append((mqtt_topic + "Iac2", iac2, 0, False))

		##### Iac3
                #iac3 = float(int(hexdata[128:132],16))/10 if __debug__:
                #    print >>sys.stderr, 'iac3: ', iac3 
                #msgs.append((mqtt_topic + "Iac3", iac3, 0, False))

		##### Pac
                #pac = float(int(hexdata[136:140],16))/10
		pac = (vpv1*ipv1+vpv2*ipv2)*0.975
                if __debug__:
                    print >>sys.stderr, 'pac: ', pac
                msgs.append((mqtt_topic + "Pac", pac, 0, False))

		##### Fac
                fac = float(int(hexdata[114:118],16))/100
                if __debug__:
                    print >>sys.stderr, 'fac: ', fac
                msgs.append((mqtt_topic + "Fac", fac, 0, False))

		##### Temp
                temp = float(int(hexdata[62:66],16))/10
                if __debug__:
                    print >>sys.stderr, 'temp: ', temp
                msgs.append((mqtt_topic + "Temp", temp, 0, False))

		##### kWh today Not confirmed yet
                kwhtoday = float(int(hexdata[138:142],16))/100
                if __debug__:
                    print >>sys.stderr, 'kwhtoday: ', kwhtoday
                msgs.append((mqtt_topic + "kwhtoday", kwhtoday, 0,False))

		##### kWh total
                kwhtotal = float(int(hexdata[146:150],16))/10
                if __debug__:
                    print >>sys.stderr, 'kwhtotal: ', kwhtotal
                msgs.append((mqtt_topic + "kwhtotal", kwhtotal, 0,False))

		#### Json Format
		DataJson = [ {"measurement":"SolarPanel", "tags":{"Unit": serial},
				"fields": {
					"VoltagePv1":vpv1,
					"VoltagePv2":vpv2,
					"CurrentPv1":ipv1,
					"CurrentPv2":ipv2,
					"MainVoltage":vac1,
					"SolarPower":pac,
					"Frequency":fac,
					"Temperatuur":temp,
					"kwhtoday":kwhtoday,
					"kwhtotal":kwhtotal
					  }
			     }
			  ]
		#### Publish data
		client = InfluxDBClient(influx_server',influx_port, influx_user , influx_passwd , influx_db)
		# print DataJson
		client.create_database (influx_db)
                client.write_points (DataJson)

		publish.multiple(msgs, hostname=mqtt_server)

                # file = open("rawlog",'a')
                # file.write(timestamp + ' ' + hexdata + '\n')
                # file.close()

    finally:
        if __debug__:
            print "Finally"
