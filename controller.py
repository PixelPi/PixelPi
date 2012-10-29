import sys, argparse, socket

#3 bytes per pixel
PIXEL_SIZE = 3

class RGBController:

    def __init__(self):
        self.gamma = bytearray(256)

        self.deviceName = '/dev/spidev0.0'
        self.UDP_IP = None
        self.UDP_PORT = 6803
        self.verbose = False
        self.chip_type = 'WS2801'

    def write_stream(self, spidev, pixels):
        if self.chip_type == "LPD6803":
            pixel_out_bytes = bytearray(2)
            spidev.write(bytearray(b'\x00\x00'))
            pixel_count = len(pixels) / PIXEL_SIZE
            for pixel_index in range(pixel_count):
                
                pixel_in = bytearray(pixels[(pixel_index * PIXEL_SIZE):((pixel_index * PIXEL_SIZE) + PIXEL_SIZE)])

                pixel_out = 0b1000000000000000 # bit 16 must be ON
                pixel_out |= (pixel_in[0] & 0x00F8) << 7 # RED is bits 11-15
                pixel_out |= (pixel_in[1] & 0x00F8) << 2 # GREEN is bits 6-10
                pixel_out |= (pixel_in[2] & 0x00F8) >> 3 # BLUE is bits 1-5

                pixel_out_bytes[0] = (pixel_out & 0xFF00) >> 8
                pixel_out_bytes[1] = (pixel_out & 0x00FF) >> 0
                spidev.write(pixel_out_bytes)
        else:
            spidev.write(pixels)

    def correct_pixel_brightness(self, pixel):

    	corrected_pixel = bytearray(3)	
    	corrected_pixel[0] = int(pixel[0] / 1.1)
    	corrected_pixel[1] = int(pixel[1] / 1.1)
    	corrected_pixel[2] = int(pixel[2] / 1.3)
    	
    	return corrected_pixel

    # Apply Gamma Correction and RGB / GRB reordering
    # Optionally perform brightness adjustment
    def filter_pixel(self, input_pixel, brightness):
        input_pixel[0] = int(brightness * input_pixel[0])
        input_pixel[1] = int(brightness * input_pixel[1])
        input_pixel[2] = int(brightness * input_pixel[2])
        output_pixel = bytearray(PIXEL_SIZE)
        if self.chip_type == "LPD8806":
            # Convert RGB into GRB bytearray list.
            output_pixel[0] = self.gamma[input_pixel[1]]
            output_pixel[1] = self.gamma[input_pixel[0]]
            output_pixel[2] = self.gamma[input_pixel[2]]
        else:
            output_pixel[0] = self.gamma[input_pixel[0]]
            output_pixel[1] = self.gamma[input_pixel[1]]
            output_pixel[2] = self.gamma[input_pixel[2]]
        return output_pixel
    	
    def run(self):
        spidev = file(self.deviceName, "wb")

    	print ("Start Raw RGB listener " + self.UDP_IP + ":" + str(self.UDP_PORT))
    	sock = socket.socket( socket.AF_INET, # Internet
                          socket.SOCK_DGRAM ) # UDP
    	sock.bind( (self.UDP_IP,self.UDP_PORT) )
    	UDP_BUFFER_SIZE = 1024
    	while True:
    		data, addr = sock.recvfrom( UDP_BUFFER_SIZE ) # blocking call
    		
    		pixels_in_buffer = len(data) / PIXEL_SIZE
    		pixels = bytearray(pixels_in_buffer * PIXEL_SIZE)
    		
    		for pixel_index in range(pixels_in_buffer):
    			pixel_to_adjust = bytearray(data[(pixel_index * PIXEL_SIZE):((pixel_index * PIXEL_SIZE) + PIXEL_SIZE)])
    			
    			pixel_to_filter = self.correct_pixel_brightness(pixel_to_adjust)
    			
    			pixels[((pixel_index)*PIXEL_SIZE):] = self.filter_pixel(pixel_to_filter[:], 1)
            		
    		self.write_stream(spidev, pixels)
    		spidev.flush()

def defineCliArguments(controller):
    parser = argparse.ArgumentParser(add_help=True,version='1.0', prog='pixelpi.py')
    parser.add_argument('--chip', action='store', dest='chip_type', default='WS2801', choices=['WS2801', 'LDP8806', 'LPD6803'], help='Specify chip type LPD6803, LDP8806 or WS2801')
    parser.add_argument('--verbose', action='store_true', dest='verbose', default=True, help='enable verbose mode')
    parser.add_argument('--spi_dev', action='store', dest='spi_dev_name', required=False, default='/dev/spidev0.0', help='Set the SPI device descriptor')
    parser.add_argument('--udp-ip', action='store', dest='UDP_IP', required=False, default='127.0.0.1', help='Used for PixelInvaders mode, listening address')
    parser.add_argument('--udp-port', action='store', dest='UDP_PORT', required=False, default=6803, type=int, help='Used for PixelInvaders mode, listening port')

    args = parser.parse_args()

    # Calculate gamma correction table. This includes
    # LPD8806-specific conversion (7-bit color w/high bit set).
    if args.chip_type == "LPD8806":
        for i in range(256):
            controller.gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)

    if args.chip_type == "WS2801":
        for i in range(256):
            controller.gamma[i] = int(pow(float(i) / 255.0, 2.5) * 255.0 )
            
    # LPD6803 has 5 bit color, this seems to work but is not exact.
    if args.chip_type == "LPD6803":
        for i in range(256):
            controller.gamma[i] = int(pow(float(i) / 255.0, 2.0) * 255.0 + 0.5)

    controller.deviceName = args.spi_dev_name
    controller.UDP_IP = args.UDP_IP
    controller.UDP_PORT = args.UDP_PORT
    controller.verbose = args.verbose
    controller.chip_type = args.chip_type

if __name__ == '__main__':

    controller = RGBController()
    defineCliArguments(controller)
    controller.run()

    print "shuting down..."
