import requests
import logging
from datetime import datetime
import sys, time, os
from apscheduler.schedulers.background import BackgroundScheduler

import coordinator


base_url = 'http://localhost/~azizou/gateway_node'
def post_sensor_data():
	time = datetime.now()
	# print "Time :",time
	if time.hour < 6 or time.hour > 20:
		return
	url = base_url + '/SensorMeasurementsPostService.php'
	response = requests.get(url)
	logging.info("Response code: "+ str(response.content))
	print "Time :",time,"Measurement Post Response:",response.content

def init_gateway(user_id, serial_id):
	url = base_url + '/RegisterGatewayNode.php'
	response = requests.get(url,params={'user_id': user_id, 'serial_id': serial_id})
	if response.status_code == 200:
		if response.content == '1':
			logging.info("Gateway registration successful. Response: 1")
			url = base_url + '/RegisterAllSensorNodes.php'
			response = requests.get(url)
			if response.status_code == 200:
				if response.content == '1':
					print "Registration successfull"
					logging.info("All Sensor nodes have been registered successfully")
				else:
					logging.warning("Some sensor nodes could not be registered")
			else:
				logging.critical("HTTP response is not OK. Response status code: {}".format(response.status_code))

		elif response.content == '0':
			logging.warning("Gateway registration failed. Response: 0")
	else:
		logging.critical("HTTP response is not OK. Response status code: {}".format(response.status_code))




def main():
	logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(funcName)s:%(message)s',filename="sensor.log")
	logging.info("Logging for gateway node started")
	delay = 15
	if len(sys.argv) < 2:
		print "Must provide the user_id and serial id of this gateway node"
		exit(-1)
	init_gateway(sys.argv[0],sys.argv[1])
	
	# Init Sensor Network
	status,coord = coordinator.network_setup(sys.argv)

	print "Initializations of gateway node and sensor network complete"
    # Setup jobs for posting data to cloud
	scheduler = BackgroundScheduler()
	scheduler.add_job(post_sensor_data, 'interval', seconds=5, id='post_job')
	time.sleep(delay)
	scheduler.start()

	print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

	try:
		while True:
			coord.collect_data()
			time.sleep(delay)

	except (KeyboardInterrupt, SystemExit):
		scheduler.shutdown()

main()



























# import serial,xbee
# import sys
# import binascii
# ser = serial.Serial('/dev/ttyUSB1',9600)
# xbee = xbee.XBee(ser,escaped=True)#API 2

# xbee.remote_at(dest_addr_long=binascii.unhexlify('0013A20040E4E730'), frame_id='A', command='NI', parameter='SLA')
# resp = xbee.wait_read_frame()
# print resp

# xbee.tx_long_addr(dest_addr=binascii.unhexlify('0013A20040E4E730'), frame_id='B', data=b'\x44')
# resp = xbee.wait_read_frame()
# print resp