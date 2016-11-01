import serial
import xbee
import sys #handle cmd_line args
from db import Db
import binascii
from end_device import EndDevice
# import db.py as db, end_device.py as end_device
class Coordinator:
	def __init__(self,port,baude_rate,node_identifier):
		try:
			ser = serial.Serial(port,baude_rate)
			self.xbee = xbee.XBee(ser,escaped=True)#API 2
			self.node_identifier = node_identifier
			self.current_frame_id = 0
			self.end_node_counter = 0
			self.base_end_node_identifier = "END DEVICE"
		except Exception as e:
			print "A critical error occured and the program will exit"
			print e
			exit(2)


	def configure(self):
		#ACCEPT end-device ASSOCIATION, CHANNEL AND PANID reassignment
		response_status = []
		print "A2"
		self.xbee.at(frame_id=self.next_frame_id(), command='A2', parameter=b'\x07')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		print "MY"
		self.xbee.at(frame_id=self.next_frame_id(), command='MY', parameter=b'\xFF\xFF')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		print "AP"
		self.xbee.at(frame_id=self.next_frame_id(), command='AP', parameter=b'\x02')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		print "EE"
		self.xbee.at(frame_id=self.next_frame_id(), command='EE', parameter=b'\x00')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])

		print "NI"
		self.xbee.at(frame_id=self.next_frame_id(), command='NI', parameter=self.node_identifier)
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		print "CE"
		self.xbee.at(frame_id=self.next_frame_id(), command='CE', parameter=b'\x01')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		print "WR"
		self.xbee.at(frame_id=self.next_frame_id(), command='WR')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])

		if response['status']==b'\x00':
			print response_status
			print " Coordinator configuration completed successfully"
			return True
		else:
			print response_status
			print "An erro occured during configuration : response = ",response
			return False

	def next_frame_id(self):
	    if self.current_frame_id<255:
	        self.current_frame_id +=1
	    else:
	        self.current_frame_id = 1
	    return chr(self.current_frame_id)
	
	def setup_end_devices(self,node_identifier):
		db = Db()
		succes = 0
		devices = db.get_active_sensors()
		end_device = EndDevice(self, self.xbee)
		for device in devices:
			print device
			end_device.set_destination_addr(binascii.unhexlify(device['serial_id']))
			status = end_device.configure()
			if status:
				print "End device with id",	device['serial_id'],'configured successfully'
				succes += 1
		if succes == len(devices):
			return True
		return False

	def next_end_node_identifier(self):
		self.end_node_counter += 1
		return self.base_end_node_identifier + " " + str(self.end_node_counter)

	def collect_data(self):
		print "Collecting sensor data"
		db = Db()
		devices = db.get_active_sensors()
		print devices
		end_device = EndDevice(self, self.xbee)
		for device in devices:
			print "Setting end device address"
			end_device.set_destination_addr(binascii.unhexlify(device['serial_id']))

			print "Requesting data from ",device['serial_id'], binascii.unhexlify(device['serial_id'])
			response = end_device.request_data()
			print response
			if response:
				print "Data received",response
				response['sensor_id'] = device['id']
				response['source'] = device['source']
				print "Saving the data"
				db.save_data(response)
			else:
				print "Device not responding"


def network_setup(argv):
	#set up connected coordinator
	port = '/dev/ttyUSB0'
	baude_rate = 9600
	node_identifier = 'MASTER'
	if len(argv) == 2:
		port = argv[1]
	elif len(argv) == 3:
		port = argv[1]
		baude_rate = argv[2]
	elif len(argv)== 4:
		port = argv[1]
		baude_rate = argv[2]
		node_identifier = argv[3]

	print "Initializing coordinator instance"
	coord = Coordinator(port,baude_rate,node_identifier)
	print "Configuring coordinator"
	status = coord.configure()
	print "configuration status",status
	if status:
		base_node_identifier = "END DEVICE"
		print "Configuring end devices"
		status = coord.setup_end_devices(base_node_identifier)
		if status:
			print "Network setup completed successfully!"
		return True,coord
	return False,None

if __name__ == '__main__':
	network_setup(sys.argv)