import coordinator
import sys, time
from apscheduler.schedulers.background import BackgroundScheduler

"""
Setup wsn network_setup
Collect sensor data every period of time
Call a service to update the cloud server with helth status twice a day
"""

delay = 20

if __name__ == '__main__':
	status,coord = coordinator.network_setup(sys.argv)
	if status:
		scheduler = BackgroundScheduler()
		# scheduler.add_job(post_sensor_data, 'interval', hours=6, id='post_job')
		scheduler.add_job(coord.collect_data, 'interval', seconds=2, id='data_collection_job')
		scheduler.start()

			while 1:#Now - last collection >= 10 minutes
				coord.collect_data()
				time.sleep(delay)
