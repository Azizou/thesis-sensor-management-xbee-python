import MySQLdb as db

class Db:
	#use system variable to store those for security purposes
	HOST = 'localhost'
	USERNAME = 'dev'
	PASSWORD = 'dev'
	DB_NAME = 'phss_healthm'

	def __init__(self):
		self.con = db.connect(self.HOST,self.USERNAME,self.PASSWORD,self.DB_NAME)
		print "Db: DB connection successful."

	def get_active_sensors(self):
	    sql = "SELECT id, serial_id, source FROM Sensors WHERE active=1"
	    cur = self.con.cursor(db.cursors.DictCursor)
	    cur.execute(sql)
	    return  cur.fetchall()

	def save_data(self, response):
		addr = response['source_addr']
		current, voltage, temperature = self.process_rf_data(response['rf_data'])
		sql = "INSERT INTO `SensorMeasurements` (`id`, `sensor_id`, `created_at`, `source`, `temperature`, `voltage`, `current`)\
		 VALUES (NULL, '{0}', CURRENT_TIMESTAMP, '{1}', '{2}', '{3}', '{4}')".format(response['sensor_id'], response['source'],
		  temperature, voltage, current)
		print sql
		with self.con:
			cur = self.con.cursor()
			cur.execute(sql)



	def process_rf_data(rf_data):
		"""
		1st 2 bytes for the current
		2nd 2 bytes for the voltage
		3rd 2 bytes for the temperature
		"""
		if(len(rf_data) != 3):
			raise DataFormatError("Expected 4 byte of rf data")
		return byteToInt(rf_data[0:2]),byteToInt(rf_data[2:4]),byteToInt(rf_data[4:6])

	def byteToInt(byte):
		if hasattr(byte, 'bit_length'):
			return byte
		return ord(byte) if hasattr(byte, 'encode') else byte[0]


class DataFormatError(Exception):
	pass