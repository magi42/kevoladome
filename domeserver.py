#!/usr/bin/python

import threading,time,sys,signal
import RPi.GPIO as GPIO
from BaseHTTPServer import *

serviceThreads = []
PORT_NUMBER = 8080

# IO pins (BCM numbering)
DOME_MAGSWITCH_1 = 17
DOME_MAGSWITCH_2 = 18
DOME_RESETSWITCH = 27

################################################################################
# DirectionService
#
# Reads input from direction detector
################################################################################
class DirectionService(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.direction = 0
        self.start()
    
    def run(self):
        print "Direction service started."
        
        # Configure I/O
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DOME_MAGSWITCH_1, GPIO.IN)
        GPIO.setup(DOME_MAGSWITCH_2, GPIO.IN)
        GPIO.setup(DOME_RESETSWITCH, GPIO.IN)
        
        state = 0
        stepdir = 0

        while self.shutdown == False:
            # Stepping - could use triggers as well
            time.sleep(0.01)

            # We use here a simple state machine to count stepping -
            # not sure if this is the best solution, but it works.
            #
            # When stepping, there is a first contact,
            # then a double contact with the overlapping
            # sensors, and then reverse single contact.
            # While at the reverse single contact, the
            # encoder can be rolled backwards.
            #
            # Contact noise filtering is not implemented.
            if state == 0: # No contact
                if GPIO.input(DOME_MAGSWITCH_1):
                    state = 1
                    stepdir = +1
                if GPIO.input(DOME_MAGSWITCH_2):
                    state = 1
                    stepdir = -1
            elif state == 1: # First contact
                if not GPIO.input(DOME_MAGSWITCH_1) and not GPIO.input(DOME_MAGSWITCH_2):
                    state = 0 # return to normal state
                elif GPIO.input(DOME_MAGSWITCH_1) and GPIO.input(DOME_MAGSWITCH_2):
                    state = 2 # Middle position
            elif state == 2: # Double contact
                if stepdir > 0 and not GPIO.input(DOME_MAGSWITCH_1) and GPIO.input(DOME_MAGSWITCH_2):
                    state = 1
                    stepdir = -1
                    self.direction += stepdir
                elif stepdir < 0 and GPIO.input(DOME_MAGSWITCH_1) and not GPIO.input(DOME_MAGSWITCH_2):
                    state = 1
                    stepdir = +1
                    self.direction += stepdir
                    
            # On reset (south direction), we reset the direction,
            # but not the state, as the magnet switches could
            # have a contact, which is just OK.
            if GPIO.input(DOME_RESETSWITCH):
                self.direction = 0
        print "Direction service stopped."
        
    def stop(self):
        self.shutdown = True

################################################################################
# Interrupt signal handler
################################################################################
def sigintHandler(signal, frame):
    print "Dome server received interrupt signal. Stopping service threads."
    for thread in serviceThreads:
        if thread.isAlive():
            thread.stop()
    for thread in serviceThreads:
        thread.join()

    print "Stopping HTTP server"
    server.socket.close()
    print "Dome server stopped."
    sys.exit(0)

signal.signal(signal.SIGINT, sigintHandler)

################################################################################
# Web Server
################################################################################
class myHandler(BaseHTTPRequestHandler):
    # Handler for HTTP GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        
        # For all requests, send the same response
        self.wfile.write("dome=%d" % directionService.direction)
        return

################################################################################
# Main
################################################################################

# Start service threads
directionService = DirectionService()
serviceThreads.append(directionService)

# Create a web server and define the handler to manage the
# incoming request
server = HTTPServer(('', PORT_NUMBER), myHandler)
print "Started HTTP server on port %d" % (PORT_NUMBER)
print "Dome server started."

# Wait forever for incoming HTTP requests
server.serve_forever()
