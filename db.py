import MySQLdb as db
from binascii import hexlify
import logging
import ConfigParser

class Db:
	def __init__(self):
		logging.info("Initializing the database")
		cfg = ConfigParser.ConfigParser()
		cfg.read('config.ini')
		self.connection = db.connect(cfg.get('database','host'),cfg.get('database','username'),cfg.get('database','password'),cfg.get('database','dbname'))
		if not self.connection:
			logging.error("Unable to connect to the database")
			exit(0)
		logging.info("Database connection successful.")


	def get_active_sensors(self):
	    sql = "SELECT id, serial_id, source FROM Sensors WHERE active=1"
	    cur = self.connection.cursor(db.cursors.DictCursor)
	    cur.execute(sql)
	    return  cur.fetchall()

	def save_data(self, response):
		addr = response['source_addr']
		current, voltage, temperature = self.process_rf_data(response['rf_data'],response['sensor_id'])
		sql = "INSERT INTO `SensorMeasurements` (`id`, `sensor_id`, `created_at`, `temperature`, `voltage`, `current`)\
		 VALUES (NULL, '{0}', CURRENT_TIMESTAMP, '{1}', '{2}', '{3}')".format(response['sensor_id'],
		  temperature, voltage, current)

		with self.connection:
			cur = self.connection.cursor()
			cur.execute(sql)
			logging.info("Response saved")



	def process_rf_data(self,rf_data, sensor_id):
		"""
		1st 2 bytes for the current
		2nd 2 bytes for the voltage
		3rd 2 bytes for the temperature
		For the temp, scale factor is 10mV/degree C

		return a float value for each of those bytes
		"""
		if(len(rf_data) != 6):
			raise DataFormatError("Expected 4 byte of rf data")
		sensor_info = self.get_sensor_info(sensor_id)
		current_bytes = int(hexlify(rf_data[0:2]),16)
		voltage_bytes = int(hexlify(rf_data[2:4]),16)
		temperature_bytes = int(hexlify(rf_data[4:6]),16)	
		adc_resolution = sensor_info['adc_resolution']
		current = (1000.0 * 5 * current_bytes)/((1<<adc_resolution)-1)/(sensor_info['current_resistor'] * sensor_info['voltage_resistor'])
		voltage = (5.0 * voltage_bytes) / ((1<<adc_resolution)-1) * (sensor_info['R1'] + sensor_info['R2'])/sensor_info['R1']
		temperature = (500.0 * temperature_bytes )/ ((1<<adc_resolution)-1)
		return current, voltage, temperature

	def get_sensor_info(self,sensor_id):
		sql = "SELECT minimum_temperature, maximum_temperature, adc_resolution, current_resistor, voltage_resistor, R1, R2 FROM Sensors WHERE active=1 AND id='{0}'".format(sensor_id)
		# print sql
		cur = self.connection.cursor(db.cursors.DictCursor)
		cur.execute(sql)
		res =  cur.fetchone()
		return res


class DataFormatError(Exception):
	pass