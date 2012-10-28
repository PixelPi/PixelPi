import sys, argparse, socket, pygame, math
import getopt
import textwrap
import sys
from ola.ClientWrapper import ClientWrapper

PIXEL_SIZE = 3

def new_dmx_data(dmx_data):
	data  = []
        if ola_dmx_receiver.verbose:
		print dmx_data
	for group in range(ola_dmx_receiver.num_leds / ola_dmx_receiver.group_size):
		for pixel in range(ola_dmx_receiver.group_size):
			data.append(dmx_data[(group*PIXEL_SIZE):(group*PIXEL_SIZE)+PIXEL_SIZE])
	ola_dmx_receiver.send(data)

class DMXReceiver:

    def __init__(self):
        self.UDP_IP = None
        self.UDP_PORT = 6803
        self.verbose = False
        self.cmd = None
        self.num_leds = 50


    # ==================================================================================================
    # ====================      Helpers                       ==========================================
    # ==================================================================================================

    def getBytes(self, data):
        result = bytearray(len(data)* PIXEL_SIZE)
        j = 0
        for i in range(len(data)):
            result[j] = data[i][0]
            result[j+1] = data[i][1]
            result[j+2] = data[i][2]
            j = j + 3
        return result

    def send(self, data):
        if self.verbose:
            print "sending ",data
        bytedata = self.getBytes(data)
        self.sendBytes(bytedata)

    def sendBytes(self, bytedata):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto( bytedata, (self.UDP_IP, self.UDP_PORT) )


    def run(self):
	wrapper = ClientWrapper()
	client = wrapper.Client()
	client.RegisterUniverse(self.universe, client.REGISTER, new_dmx_data)
	wrapper.Run()

# ==================================================================================================
# ====================      Argument parsing              ==========================================
# ==================================================================================================

def defineCliArguments(ola_dmx_receiver):
    parser = argparse.ArgumentParser(add_help=True,version='1.0', prog='pixelpi.py')
    parser.add_argument('--verbose', action='store_true', dest='verbose', default=False, help='enable verbose mode')
    parser.add_argument('--udp-ip', action='store', dest='UDP_IP', required=False, default='127.0.0.1', help='PixelPi ip to send RGB data to')
    parser.add_argument('--udp-port', action='store', dest='UDP_PORT', required=False, default=6803, type=int, help='PixelPi Port to send RGB data to')
    parser.add_argument('--universe', action='store', dest='universe', required=True, type=int, default='1', help='what dmx universe should we listen to')
    parser.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int,  help='Set the  number of LEDs in the string')
    parser.add_argument('--group_size', action='store', dest='group_size', required=True, default=1, type=int,  help='Set the  number of LEDs in a group')
    
    args = parser.parse_args()
    ola_dmx_receiver.UDP_IP = args.UDP_IP
    ola_dmx_receiver.UDP_PORT = args.UDP_PORT
    ola_dmx_receiver.verbose = args.verbose
    ola_dmx_receiver.num_leds = args.num_leds
    ola_dmx_receiver.universe = args.universe
    ola_dmx_receiver.group_size = args.group_size

    print "Using UDP Client at ", ola_dmx_receiver.UDP_IP,":",ola_dmx_receiver.UDP_PORT

if __name__ == '__main__':
    print "starting..."
    
    ola_dmx_receiver = DMXReceiver()
    defineCliArguments(ola_dmx_receiver)
    ola_dmx_receiver.run()
    
    print "shuting down..."


