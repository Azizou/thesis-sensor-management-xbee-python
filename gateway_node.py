import requests
import logging
from datetime import datetime
import sys, time, os
from apscheduler.schedulers.background import BackgroundScheduler

import coordinator


base_url = 'http://localhost/~azizou/gateway_node'
def post_sensor_data():
	time = datetime.now()
	if time.hour < 6 or time.hour > 20:
		return
	url = base_url + '/SensorMeasurementsPostService.php'
	response = requests.get(url)
	logging.info("Response code: "+ str(response.content))
	# print response.content

def init_gateway(user_id, serial_id):
	url = base_url + '/RegisterGatewayNode.php'
	response = requests.get(url,params={'user_id': user_id, 'serial_id': serial_id})
	if response.status_code == 200:
		if response.content == '1':
			logging.info("Gateway registration successful. Response: 1")
			# Register sensor nodes
			url = base_url + '/RegisterAllSensorNodes.php'
			response = requests.get(url)
			if response.status_code == 200:
				if response.content == '1':
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
	logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(funcName)s:%(message)s',filename="sensor.log",level=logging.INFO)
	logging.info("Logging for gateway node started")
	delay = 20
	if len(sys.argv) < 2:
		print "Must provide the user_id and serial id of this gateway node"
		exit(-1)
	init_gateway(sys.argv[0],sys.argv[1])
	
	# Init Sensor Network
	status,coord = coordinator.network_setup(sys.argv)

	print "Initilisation of gateway node and sensor network complete"
    # Setup jobs for posting data to cloud
	scheduler = BackgroundScheduler()
	if status:
		scheduler = BackgroundScheduler()
		# scheduler.add_job(post_sensor_data, 'interval', hours=6, id='post_job')
		scheduler.add_job(coord.collect_data, 'interval', minutes=delay, id='data_collection_job')
		# scheduler.start()
	scheduler.add_job(post_sensor_data, 'interval', hours=6, id='post_job')
	# scheduler.add_job(post_sensor_data, 'interval', seconds=1, id='post_job')
	scheduler.start()

	print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

	try:
		# This is here to simulate application activity (which keeps the main thread alive).
		while True:
			time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
		# Not strictly necessary if daemonic mode is enabled but should be done if possible
		scheduler.shutdown()

main()