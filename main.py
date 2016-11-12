import requests
import logging
from datetime import datetime
import sys, time, os
from apscheduler.schedulers.background import BackgroundScheduler
import coordinator
import ConfigParser

cfg = ConfigParser.ConfigParser()
cfg.read('config.ini')
base_url = cfg.get('gateway','base_url')
user_id = cfg.get('gateway','user_id')
serial_id = cfg.get('gateway','serial_id')
baude_rate = int(cfg.get('gateway','baude_rate'))
port = cfg.get('gateway','port')
collect_interval = int(cfg.get('gateway','collect_interval'))
post_interval = int(cfg.get('gateway','post_interval'))

def post_sensor_data():
	time = datetime.now()
	if time.hour < 6 or time.hour > 23:
		return
	url = base_url + '/SensorMeasurementsPostService.php'
	response = requests.get(url)
	logging.info("Time : {} Measurement Post Response: {}".format(time,response.content))


def init_gateway():
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
	logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(funcName)s:%(message)s',filename="sensor.log",level=logging.DEBUG)
	logging.info("Logging for gateway node started")
	logging.getLogger("requests").setLevel(logging.WARNING)
	logging.getLogger("apscheduler").setLevel(logging.WARNING)
	logging.getLogger("urllib3").setLevel(logging.WARNING)
	

	init_gateway()
	global port
	if(len(sys.argv)==2):
		port = sys.argv[1]
	# Init Sensor Network
	status,coord = coordinator.network_setup(['',port,baude_rate])

	print "Initialization of gateway node and sensor network complete"
    # Setup jobs for posting data to cloud
	scheduler = BackgroundScheduler()
	scheduler.add_job(post_sensor_data, 'interval', seconds=post_interval, id='post_job')
	time.sleep(collect_interval)
	scheduler.start()

	print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

	try:
		while True:
			coord.collect_data()
			time.sleep(collect_interval)

	except (KeyboardInterrupt, SystemExit):
		scheduler.shutdown()

main()