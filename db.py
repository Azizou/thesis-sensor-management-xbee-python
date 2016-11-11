import MySQLdb as db
from binascii import hexlify

class Db:
	#use system variable to store those for security purposes
	HOST = 'localhost'
	USERNAME = 'dev'
	PASSWORD = 'dev'
	DB_NAME = 'phss_healthm'

	def __init__(self):
		self.connection = db.connect(self.HOST,self.USERNAME,self.PASSWORD,self.DB_NAME)
		# print "Db: DB connection successful."

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
		# print sql
		with self.connection:
			cur = self.connection.cursor()
			cur.execute(sql)



	def process_rf_data(self,rf_data, sensor_id):
		"""
		1st 2 bytes for the current
		2nd 2 bytes for the voltage
		3rd 2 bytes for the temperature
		return a float value for each of those bytes
		"""
		if(len(rf_data) != 6):
			raise DataFormatError("Expected 4 byte of rf data")
		sensor_info = self.get_sensor_info(sensor_id)
		current_bytes = int(hexlify(rf_data[0:2]),16)
		voltage_bytes = int(hexlify(rf_data[2:4]),16)
		temperature_bytes = int(hexlify(rf_data[4:6]),16)

		# print "Curreent: {0}, Volatge: {1}, Temperature: {2}".format(current_bytes, voltage_bytes, temperature_bytes)
		
		adc_resolution = sensor_info['adc_resolution']
		current = (1000.0 * 5 * current_bytes)/((1<<adc_resolution)-1)/(sensor_info['current_resistor'] * sensor_info['voltage_resistor'])
		voltage = (5.0 * voltage_bytes) / ((1<<adc_resolution)-1) * (sensor_info['R1'] + sensor_info['R2'])/sensor_info['R1']
		temperature = (500.0 * temperature_bytes )/ ((1<<adc_resolution)-1) #(sensor_info['maximum_temperature'] - sensor_info['minimum_temperature']) + sensor_info['minimum_temperature']
		# print "Curreent: {0:.4f}, Volatge: {1:.4f}, Temperature: {2:.3f}".format(current, voltage, temperature)
		return current, voltage, temperature
		#if Vo is already in the range 0 - 5V based on the value of Rl and Rs, compute Is directly
		#Is = 1000 x Vo / (Rs x Rl) where Vo = 5 * current_bytes/(1<<10 - 1)
		#Else Vo = 
		#current = Vs/Rs
		#Vs = Vo/Rl/1000


	def get_sensor_info(self,sensor_id):
		sql = "SELECT minimum_temperature, maximum_temperature, adc_resolution, current_resistor, voltage_resistor, R1, R2 FROM Sensors WHERE active=1 AND id='{0}'".format(sensor_id)
		print sql
		cur = self.connection.cursor(db.cursors.DictCursor)
		cur.execute(sql)
		res =  cur.fetchone()
		print res
		return res


class DataFormatError(Exception):
	pass