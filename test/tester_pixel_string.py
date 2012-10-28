import sys, argparse, socket, pygame, math
from vector import *

PIXEL_SIZE = 3
BUFFER_SIZE = NUM_PIXELS * PIXEL_SIZE

WHITE = [255,255,255]
RED = [255,0,0]
GREEN = [0,255,0]
BLUE = [0,0,255]
TURQUE = [0,255,255]
YELLOW = [255,255,0]
BLACK = [0,0,0]

class RGBTester:

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

    def toByteArray(self, grid):
        result = bytearray(self.num_leds * PIXEL_SIZE)

        i = 0
        while i < BUFFER_SIZE:
            y = i/3 % PIXEL_DIM_Y
            x = int(math.floor(i/3 / PIXEL_DIM_Y))
            if x % 2 == 0:
                c = grid[x][y]
                result[i] = c[0]
                i = i + 1
                result[i] = c[1]
                i = i + 1
                result[i] = c[2]
                i = i + 1
            else:
                c = grid[x][(PIXEL_DIM_Y-1)-y]
                result[i] = c[0]
                i = i + 1
                result[i] = c[1]
                i = i + 1
                result[i] = c[2]
                i = i + 1

        # for x in range(len(grid)):
        #     for y in range(len(grid[x])):
        #         if x % 2 == 0:
        #             result[i] = grid[x][y][0]
        #             i = i + 1
        #             result[i] = grid[x][y][1]
        #             i = i + 1
        #             result[i] = grid[x][y][2]
        #             i = i + 1
        #         else:
        #             result[i+(PIXEL_DIM_Y-1)] = grid[x][y][0]
        #             i = i + 1
        #             result[i+(PIXEL_DIM_Y-1)] = grid[x][y][1]
        #             i = i + 1
        #             result[i+(PIXEL_DIM_Y-1)] = grid[x][y][2]
        #             i = i + 1
        return result

    def createGridBuffer(self, color):
        result = []
        for x in range(PIXEL_DIM_X):
            result.append([])
            for y in range(PIXEL_DIM_Y):
                result[x].append(color)
        return result
    
    def setPixel(self, grid, v, color):
        pos = v.toIntArr()
        if pos[0] >= 0 and pos[0] < PIXEL_DIM_X and \
           pos[1] >= 0 and pos[1] < PIXEL_DIM_Y:
            grid[pos[0]][pos[1]] = color

    def clearPixels(self, grid, color):
        for x in range(len(grid)):
            for y in range(len(grid[x])):
                grid[x][y] = color

    def run(self):
        if self.cmd == 'allon':
            self.allon()
        if self.cmd == 'alloff':
            self.alloff()
        if self.cmd == 'test':
            self.test()
        elif self.cmd == 'pong':
            self.pong()

    # ==================================================================================================
    # ====================      Modes                         ==========================================
    # ==================================================================================================
	def fade():
	    data = bytearray(self.num_leds * PIXEL_SIZE)
	    current_color = bytearray(PIXEL_SIZE)

	    while True:
		for color in RAINBOW:
		    for brightness in [x*0.01 for x in range(0,100)]:
			current_color[:] = filter_pixel(color[:], brightness)
			for pixel_offset in [(x * 3) for x in range(args.num_leds)]:
				data[pixel_offset:] = current_color[:]
			self.send(data)
		    for brightness in [x*0.01 for x in range(100,0, -1)]:
			current_color[:] = filter_pixel(color[:], brightness)
			for pixel_offset in [(x * 3) for x in range(args.num_leds)]:
				data[pixel_offset:] = current_color[:]
			self.send(data)

    def allon(self):
        data = []
        for i in range(NUM_PIXELS):
            data.append(WHITE)
        
        self.send(data)

    def alloff(self):
        data = []
        for i in range(NUM_PIXELS):
            data.append(BLACK)
        
        self.send(data)

    def test2(self):
        grid = self.createGridBuffer(BLACK)

        colors = [RED,BLUE,WHITE,GREEN,YELLOW,BLUE,RED,TURQUE]

        for i in range(len(colors)):
            c = colors[i]

            self.setPixel(grid, Vector(i,i), c)
            self.setPixel(grid, Vector(i,PIXEL_DIM_Y-(1+i)), c)
            self.setPixel(grid, Vector(PIXEL_DIM_X-(1+i),i), c)
            self.setPixel(grid, Vector(PIXEL_DIM_X-(1+i),PIXEL_DIM_Y-(1+i)), c)

        self.sendBytes(self.toByteArray(grid))

    def test(self):
        grid = self.createGridBuffer(BLACK)

        clock = pygame.time.Clock()
        i = 0
        while True:
            dt = clock.tick(1) / 1000.0

            c = WHITE
            if i % 2 == 0:
                c = BLACK

            self.setPixel(grid, Vector(4,7), c)

            i += 1

            self.sendBytes(self.toByteArray(grid))

    def pong(self):
        grid = self.createGridBuffer(BLACK)
        p1 = Vector(0,4)
        p2 = Vector(11,4)
        b = Vector(6,4)
        speed = 10
        p1v = Vector(0,1) * speed
        p2v = Vector(0,1) * speed
        bv = Vector(1,1) * speed
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(40) / 1000.0

            self.clearPixels(grid, BLACK)

            self.setPixel(grid, p1, RED)
            self.setPixel(grid, p2, GREEN)
            self.setPixel(grid, b, WHITE)

            p1 += p1v * dt
            if p1.y > PIXEL_DIM_Y-1 or p1.y < 0:
                p1v *= -1
                p1.constrain(0, 0, PIXEL_DIM_X-1, PIXEL_DIM_Y-1)
            
            p2 += p2v * dt
            if p2.y > PIXEL_DIM_Y-1 or p2.y < 0:
                p2v *= -1
                p2.constrain(0, 0, PIXEL_DIM_X-1, PIXEL_DIM_Y-1)
            
            b += bv * dt
            if b.x > PIXEL_DIM_X-2 or b.x < 1:
                bv.x *= -1
                b.constrain(1, 0, PIXEL_DIM_X-2, PIXEL_DIM_Y-1)
            if b.y > PIXEL_DIM_Y or b.y < 0:
                bv.y *= -1
                b.constrain(1, 0, PIXEL_DIM_X-2, PIXEL_DIM_Y-1)

            if bv.x > 0:
                p2.y = b.y
            if bv.x < 0:
                p1.y = b.y

            self.sendBytes(self.toByteArray(grid))


# ==================================================================================================
# ====================      Argument parsing              ==========================================
# ==================================================================================================

def defineCliArguments(tester):
    parser = argparse.ArgumentParser(add_help=True,version='1.0', prog='pixelpi.py')
    parser.add_argument('--verbose', action='store_true', dest='verbose', default=True, help='enable verbose mode')
    parser.add_argument('--udp-ip', action='store', dest='UDP_IP', required=False, default='127.0.0.1', help='PixelPi ip to send RGB data to')
    parser.add_argument('--udp-port', action='store', dest='UDP_PORT', required=False, default=6803, type=int, help='PixelPi Port to send RGB data to')
    parser.add_argument('--cmd', action='store', dest='cmd', required=True, default='allon', help='what should the tester do?')
    parser_fade.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int,  help='Set the  number of LEDs in the string')
    
    args = parser.parse_args()
    tester.UDP_IP = args.UDP_IP
    tester.UDP_PORT = args.UDP_PORT
    tester.verbose = args.verbose
    tester.cmd = args.cmd
    tester.num_leds = args.num_leds

    print "Using UDP Client at ", tester.UDP_IP,":",tester.UDP_PORT

if __name__ == '__main__':
    print "starting..."
    
    tester = RGBTester()
    defineCliArguments(tester)
    tester.run()
    
    print "shuting down..."


