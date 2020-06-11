import os
import sys
import argparse
import time
import signal
import math
import random

# include the netbot src directory in sys.path so we can import modules from it.
robotpath = os.path.dirname(os.path.abspath(__file__))
srcpath = os.path.join(os.path.dirname(robotpath),"src")
sys.path.insert(0,srcpath)

from netbots_log import log
from netbots_log import setLogLevel
import netbots_ipc as nbipc
import netbots_math as nbmath

robotName = "raineyfinal"
currentMode = "scan"
savedDirection = -1
smallestDistance = 0
health = 0
vertical = True
stepCount = 0

def play(botSocket, srvConf):
    global health
    movingF = False
    movingI = True
    start = True
    gameNumber = 0  # The last game number bot got from the server (0 == no game has been started)
    l = 0
    r = 31
    cornerX = 0
    cornerY = 0
    while True:

        if (start):
            start = False
            global currentMode
            global savedDirection
            global smallestDistance
            try:
                # get location data from server
                getLocationReply = botSocket.sendRecvMessage({'type': 'getLocationRequest'})

                # find the closest corner:
                if (getLocationReply['x'] < (srvConf['arenaSize'] / 2)):
                    cornerX = 0
                else:
                    cornerX = srvConf['arenaSize']

                if (getLocationReply['y'] < (srvConf['arenaSize'] / 2)):
                    cornerY = 0
                else:
                    cornerY = srvConf['arenaSize']

                # find the angle from where we are to the closest corner
                radians = nbmath.angle(getLocationReply['x'], getLocationReply['y'], cornerX, cornerY)

                # Turn in a new direction
                botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': radians})

                # Request we start accelerating to max speed
                botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 75})
                movingI = True
                # log some useful information.
                degrees = str(int(round(math.degrees(radians))))
                log("Requested to go " + degrees + " degress at max speed.", "INFO")

            except nbipc.NetBotSocketException as e:
                # Consider this a warning here. It may simply be that a request returned
                # an Error reply because our health == 0 since we last checked. We can
                # continue until the next game starts.
                log(str(e), "WARNING")
            continue
        try:
            if currentMode == "wait":
                # find out if we already have a shell in the air. We need to wait for it to explode before
                # we fire another shell. If we don't then the first shell will never explode!
                getCanonReply = botSocket.sendRecvMessage({'type': 'getCanonRequest'})
                if not getCanonReply['shellInProgress']:
                    # we are ready to shoot again!
                    currentMode = "scan"
            if currentMode == "scan":
                scanReply = botSocket.sendRecvMessage({'type': 'scanRequest', 'startRadians': 0, 'endRadians': 2*math.pi})
                smallestDistance = scanReply['distance']
                if (savedDirection != -1):
                    temp1 = savedDirection - 15
                    temp2 = savedDirection + 15
                    if (temp1 < 0):
                        temp1 = 0
                    if (temp2 > 128):
                        temp2 = 128
                    binarySearch(temp1, temp2)
                    savedDirection = -1
                else:
                    binarySearch(0, 128)
            getLocationReply = botSocket.sendRecvMessage({'type': 'getLocationRequest'})

            if (movingI):
                if round(getLocationReply['x']) <= srvConf['botRadius'] + 100:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                elif round(getLocationReply['x']) >= srvConf['arenaSize'] - srvConf['botRadius'] - 100:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                elif round(getLocationReply['y']) <= srvConf['botRadius'] + 100:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                elif round(getLocationReply['y']) >= srvConf['arenaSize'] - srvConf['botRadius'] - 100:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                else:
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 100})

            if (getLocationReply['x'] < (srvConf['arenaSize'] / 2)):
                cornerX = 0
            else:
                cornerX = 1000

            if (getLocationReply['y'] < (srvConf['arenaSize'] / 2)):
                cornerY = 0
            else:
                cornerY = 1000

            if (movingF):
               getSpeed = botSocket.sendRecvMessage({'type': 'getSpeedRequest'})
               if (cornerX == 0 and cornerY == 0):
                   if (int(getLocationReply['y']) >= 250):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': 3 * math.pi / 2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   elif(int(getLocationReply['y']) <= 100):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi/2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   else:
                       botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})

               if (cornerX == 1000 and cornerY == 0):
                   if (int(getLocationReply['y']) >= 300):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': 3 * math.pi / 2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   elif(int(getLocationReply['y']) <= 100):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi/2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   else:
                       botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})

               if (cornerX == 0 and cornerY == 1000):
                   if (int(getLocationReply['y']) <= 700):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi / 2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   elif (int(getLocationReply['y']) >= 900):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': 3 * math.pi / 2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   else:
                       botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})

               if (cornerX == 1000 and cornerY == 1000):
                   if (int(getLocationReply['y']) <= 700):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi / 2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   elif (int(getLocationReply['y']) >= 900):
                       if (getSpeed['currentSpeed'] == 50):
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                       if (getSpeed['currentSpeed'] == 0):
                           botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': 3 * math.pi / 2})
                           botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                   else:
                       botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})


        except nbipc.NetBotSocketException as e:
            # Consider this a warning here. It may simply be that a request returned
            # an Error reply because our health == 0 since we last checked. We can
            # continue until the next game starts.
            log(str(e), "WARNING")
            continue

##################################################################
# Standard stuff below.
##################################################################
def binarySearch(l, r):
    # Check base case
    if r >= l:
        global currentMode
        global savedDirection
        global smallestDistance
        mid = (l + r) / 2
        # If element is present at the middle itself
        #print(str(l) + " " + str(mid) + " " + str(r))
        if (mid >= r - 1):
            fireDirection = ((((mid + r) / 2) / 128) * 2 * math.pi)
            savedDirection = (mid + r) / 2
            currentMode = "wait"
            botSocket.sendRecvMessage(
                {'type': 'fireCanonRequest', 'direction': fireDirection, 'distance': smallestDistance})
            return
        elif (mid <= l + 1):
            fireDirection = ((((mid + l) / 2) / 128) * 2 * math.pi)
            savedDirection = (mid + l) / 2
            currentMode = "wait"
            botSocket.sendRecvMessage(
                {'type': 'fireCanonRequest', 'direction': fireDirection, 'distance': smallestDistance})
            return
        scanReply = botSocket.sendRecvMessage(
            {'type': 'scanRequest', 'startRadians': (l / 128) * 2 * math.pi, 'endRadians': (mid / 128) * 2 * math.pi})

        #print("scan" + str((l/128) * 2 * math.pi) + " " + str((mid/128) * 2 * math.pi))
        if ((scanReply['distance'] >= smallestDistance - float(30)) and (scanReply['distance'] <= smallestDistance + float(30))):
            smallestDistance = scanReply['distance']
            return binarySearch(l, mid)
            # Else the element can only be present
        # in right subarray
        else:
            return binarySearch(mid, r)
    else:
        # Element is not present in the array
        return -1




def quit(signal=None, frame=None):
    global botSocket
    log(botSocket.getStats())
    log("Quiting", "INFO")
    exit()


def main():
    global botSocket  # This is global so quit() can print stats in botSocket
    global robotName

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-ip', metavar='My IP', dest='myIP', type=nbipc.argParseCheckIPFormat, nargs='?',
                        default='127.0.0.1', help='My IP Address')
    parser.add_argument('-p', metavar='My Port', dest='myPort', type=int, nargs='?',
                        default=20010, help='My port number')
    parser.add_argument('-sip', metavar='Server IP', dest='serverIP', type=nbipc.argParseCheckIPFormat, nargs='?',
                        default='127.0.0.1', help='Server IP Address')
    parser.add_argument('-sp', metavar='Server Port', dest='serverPort', type=int, nargs='?',
                        default=20000, help='Server port number')
    parser.add_argument('-debug', dest='debug', action='store_true',
                        default=False, help='Print DEBUG level log messages.')
    parser.add_argument('-verbose', dest='verbose', action='store_true',
                        default=False, help='Print VERBOSE level log messages. Note, -debug includes -verbose.')
    args = parser.parse_args()
    setLogLevel(args.debug, args.verbose)

    try:
        botSocket = nbipc.NetBotSocket(args.myIP, args.myPort, args.serverIP, args.serverPort)
        joinReply = botSocket.sendRecvMessage({'type': 'joinRequest', 'name': robotName}, retries=300, delay=1, delayMultiplier=1)
    except nbipc.NetBotSocketException as e:
        log("Is netbot server running at" + args.serverIP + ":" + str(args.serverPort) + "?")
        log(str(e), "FAILURE")
        quit()

    log("Join server was successful. We are ready to play!")

    # the server configuration tells us all about how big the arena is and other useful stuff.
    srvConf = joinReply['conf']
    log(str(srvConf), "VERBOSE")

    # Now we can play, but we may have to wait for a game to start.
    play(botSocket, srvConf)


if __name__ == "__main__":
    # execute only if run as a script
    signal.signal(signal.SIGINT, quit)
    main()
