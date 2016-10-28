import logging

def main():
	logging.basicConfig(format='%(asctime)s: Function: %(funcName)s:%(name)s:%(levelname)s:%(pathname)s:%(lineno)d:%(message)s',filename="sensor.log",level=logging.DEBUG)
	logging.info("The Coordinator is runing")
	logging.warning("No response from end device %s after 15 seconds","E45")
	logging.error("Timeout")
	logging.critical("No internet access: server at %s is unreachable","www.phss_server.phss.com")
	logging.info("Network Status: %d",True)
	res = {'a':3,'Status': b'\x4CCF'}
	logging.info(res)
main()