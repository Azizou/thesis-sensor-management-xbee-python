"""
	@author: Azizou Ogbone
	@file: end_device.py
	@description: represent an end device in the wireless sensor network.
"""
import logging
class EndDevice:
	def __init__(self, coord, xbee, dest_addr=None):
		self.xbee = xbee
		self.dest_addr = dest_addr
		self.sl = None
		self.sh = None
		self.coord = coord

	
	def configure(self):
		response_status = []
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='AP', parameter=b'\x02')
		response = self.xbee.wait_read_frame()
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='CE', parameter=b'\x00')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='A1', parameter=b'\x07')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='DL', parameter=self.sl)
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='DH', parameter=self.sh)
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='MY', parameter=b'\xFF\xFF')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='EE', parameter=b'\x00')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='NI', parameter=self.coord.next_end_node_identifier())
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])
		self.xbee.remote_at(dest_addr_long=self.dest_addr, frame_id=self.coord.next_frame_id(), command='WR')
		response = self.xbee.wait_read_frame()
		response_status.append(response['status'])

		for st in response_status:
			if st != b'\x00':
				logging.warning("An error occured while configuring the end_device xbee node")
				return False
		else:
			logging.info("End Node configuration completed successfully")
		return True

	def set_destination_addr(self,dest_addr):
		self.dest_addr = dest_addr

	def request_data(self):
		self.xbee.tx_long_addr(dest_addr=self.dest_addr, frame_id=self.coord.next_frame_id(), data=b'\x44')
		tx_long_addr = self.xbee.wait_read_frame()
		if tx_long_addr['id'] == 'tx_status' and tx_long_addr['status']==b'\x00':
			packet = self.xbee.wait_read_frame()
			if packet['id'] == 'rx_long_addr':
				return packet
			else:
				logging.error("Unexpected packet received", packet['id'])
		else:
			logging.warning("Transmission failed with status response: ",tx_long_addr['status'])
		return False

def main():
	print "Sorry, currently configuration is only done remotely"


if __name__ == '__main__':
	main()