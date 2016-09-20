"""
	@file: end_device.py
	@description: represent an end device in the wireless sensor network.
"""

class EndDevice:
	def __init__(self, coord, xbee, dest_addr=None):
		self.xbee = xbee
		self.dest_addr = dest_addr
		self.sl = None
		self.sh = None
		self.coord = coord
		self.current_frame_id = 0
		self.getAddressOfCoordinator()
	#Assuming end devices are confured with 111 (reassign panid, reassign chanel id and auto associate on power up)
	#same pan id as coordinator
	#Use only 64 bit addressing
	#for each request wait for 10s for a response
	#use a 128 bit key after enabling the encryption key
	#set the  node indicator for each end device
	#All this either in the xctu-software or using a script (peferable) with command line arguments

	""" 
		set the coordinator addess on the end device
		disbale 16 bit communication
	"""
	def configure(self):
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='AP', parameter=b'\x02')
		response = self.xbee.wait_read_frame()
		print response

		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='CE', parameter=b'\x00')
		response = self.xbee.wait_read_frame()
		print response

		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='A1', parameter=b'\x07')
		response = self.xbee.wait_read_frame()
		print response

		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='DL', parameter=self.sl)
		response = self.xbee.wait_read_frame()
		print response

		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='DH', parameter=self.sh)
		response = self.xbee.wait_read_frame()
		print response

		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='MY', parameter=b'\xFF\xFF')
		response = self.xbee.wait_read_frame()
		print response

		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='EE', parameter=b'\x00')
		response = self.xbee.wait_read_frame()
		print response

		# self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='KY', parameter=b'\x07\x07\x07\x07\x07\x07\x07\x07\x08\x08\x08\x08\x08\x08\x08\x08')
		# response = self.xbee.wait_read_frame()
		# print response

		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='NI', parameter=self.coord.next_end_node_identifier())
		response = self.xbee.wait_read_frame()

		print response
		if response['status'] ==b'\x00':
			return True
		return False
		#TODO check if response is OK for all the above commands
	    

	#dest addr is 64-bit
	def set_destination_addr(self,dest_addr):
		self.dest_addr = dest_addr

	def request_data(self,next_frame_id):
		self.xbee.tx_long_addr(dest_addr=self.dest_addr, frame_id=next_frame_id())
		packet = self.xbee.wait_read_frame()
		if packet['id'] == 'rx_long_addr':
			return packet


	def getAddressOfCoordinator(self):
	    self.xbee.at(frame_id=self.coord.next_frame_id(), command='SL')
	    response = self.xbee.wait_read_frame()
	    print response
	    self.sl = response['parameter']

	    self.xbee.at(frame_id=self.coord.next_frame_id(), command='SH')
	    response = self.xbee.wait_read_frame()
	    self.sh = response['parameter']

	def next_frame_id(self):
		self.coord.next_frame_id()

	def next_frame_id(self):
	    if self.current_frame_id<255:
	        self.current_frame_id +=1
	    else:
	        self.current_frame_id = 1
	    return chr(self.current_frame_id)

def main():
	#set up connected coorinator
	port = '/dev/ttyUSB0'
	baude_rate = 9600
	node_identifier = 'END DEVICE 1'
	if len(sys.argv) == 2:
		port = sys.argv[1]
	elif len(sys.argv) == 3:
		port = sys.argv[1]
		baude_rate = sys.argv[2]
	elif len(sys.argv)== 4:
		port = sys.argv[1]
		baude_rate = sys.argv[2]
		node_identifier = sys.argv[3]

	coord = Coorinator(port,baude_rate,node_identifier)
	coord.setup_end_devices()
	print coord.configure()


if __name__ == '__main__':
	main()