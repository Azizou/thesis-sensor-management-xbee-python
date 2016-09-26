from coordinator import Coordinator, network_setup
import sys, time

"""
Setup wsn network_setup
Collect sensor data every period of time
Call a service to update the cloud server with helth status twice a day
"""

delay = 10
if __name__ == '__main__':
	status,coord = network_setup(sys.argv)
	if status:
		while 1:#Now - last collection >= 10 minutes
			coord.collect_data()
			time.sleep(delay)
