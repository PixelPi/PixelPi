PixelPi
=======
RGB Pixel Array Driver for the Raspberry Pi; this provides a OLA output device which can display DMX data on LED pixels; or groups of pixels.  

Project Page:
http://thegreatgeekery.blogspot.ca/2012/08/raspberry-pi-and-ws2801.html

	usage: pixelpi.py [-h] [-v] [--verbose] [--udp-ip UDP_IP]
			  [--udp-port UDP_PORT] --universe UNIVERSE --num_leds
			  NUM_LEDS --group_size GROUP_SIZE

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  --verbose             enable verbose mode
	  --udp-ip UDP_IP       PixelPi ip to send RGB data to
	  --udp-port UDP_PORT   PixelPi Port to send RGB data to
	  --universe UNIVERSE   what dmx universe should we listen to
	  --num_leds NUM_LEDS   Set the number of LEDs in the string
	  --group_size GROUP_SIZE
				Set the number of LEDs in a groupk


