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
vertical = True
stepCount = 0
previousX = -1
previousY = -1
shotX = -1
shotY = -1
stepCount = 0
shotCount = 0
thisDirection = -1

def play(botSocket, srvConf):
    global health
    global previousX
    global previousY
    global stepCount
    global shotCount
    global currentMode
    global savedDirection
    global smallestDistance
    global thisDirection
    gameNumber = 0
    movingF = False
    movingI = True
    start = True
    while True:
        try:
            # Get information to determine if bot is alive (health > 0) and if a new game has started.
            getInfoReply = botSocket.sendRecvMessage({'type': 'getInfoRequest'})
        except nbipc.NetBotSocketException as e:
            # We are always allowed to make getInfoRequests, even if our health == 0. Something serious has gone wrong.
            log(str(e), "FAILURE")
            log("Is netbot server still running?")
            quit()
        health = getInfoReply['health']
        if getInfoReply['health'] == 0:
            # we are dead, there is nothing we can do until we are alive again.
            continue

        if getInfoReply['gameNumber'] != gameNumber:
            # A new game has started. Record new gameNumber and reset any variables back to their initial state
            gameNumber = getInfoReply['gameNumber']
            log("Game " + str(gameNumber) + " has started. Points so far = " + str(getInfoReply['points']))

            # start every new game in scan mode. No point waiting if we know we have not fired our canon yet.

            # lighthouse will scan the area in this many slices (think pizza slices with this bot in the middle)
            scanSlices = 32
            global currentMode
            global savedDirection
            global smallestDistance
            # This is the radians of where the next scan will be
            nextScanSlice = 0

            # Each scan will be this wide in radians (note, math.pi*2 radians is the same as 360 Degrees)
            scanSliceWidth = math.pi * 2 / scanSlices
            try:
                # get location data from server
                getLocationReply = botSocket.sendRecvMessage({'type': 'getLocationRequest'})

                # find the closest corner:
                if (getLocationReply['x'] < (srvConf['arenaSize'] / 2)):
                    cornerX = 200
                else:
                    cornerX = 800

                if (getLocationReply['y'] < (srvConf['arenaSize'] / 2)):
                    cornerY = 200
                else:
                    cornerY = 800

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
            checkShot()
            getLocationReply = botSocket.sendRecvMessage({'type': 'getLocationRequest'})
            stepCount += 1
            checkShot()
            if (getLocationReply['x'] < (srvConf['arenaSize'] / 2)):
                cornerX = 0
            else:
                cornerX = 1000

            if (getLocationReply['y'] < (srvConf['arenaSize'] / 2)):
                cornerY = 0
            else:
                cornerY = 1000
            if (movingI):
                if round(getLocationReply['x']) <= srvConf['botRadius'] + 300:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                    stepCount += 1
                elif round(getLocationReply['x']) >= srvConf['arenaSize'] - srvConf['botRadius'] - 300:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                    stepCount += 1
                elif round(getLocationReply['y']) <= srvConf['botRadius'] + 300:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                    stepCount += 1
                elif round(getLocationReply['y']) >= srvConf['arenaSize'] - srvConf['botRadius'] - 300:
                    movingI = False
                    movingF = True
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 0})
                    stepCount += 1

            if (movingF):
                if (previousX == getLocationReply['x'] and previousY == getLocationReply['y']):
                    botSocket.sendRecvMessage({'type': 'setSpeedRequest', 'requestedSpeed': 50})
                    stepCount += 1
                if (cornerX == 0 and cornerY == 0):
                    if (int(getLocationReply['y']) >= 400):
                        botSocket.sendRecvMessage(
                            {'type': 'setDirectionRequest', 'requestedDirection': (3 * math.pi) / 2})
                        stepCount += 1
                        thisDirection = 0
                    elif (int(getLocationReply['y']) <= 200):
                        botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi / 2})
                        stepCount += 1
                        thisDirection = 1
                if (cornerX == 1000 and cornerY == 0):
                    if (int(getLocationReply['y']) >= 400):
                        botSocket.sendRecvMessage(
                            {'type': 'setDirectionRequest', 'requestedDirection': (3 * math.pi) / 2})
                        stepCount += 1
                        thisDirection = 0
                    elif (int(getLocationReply['y']) <= 200):
                        botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi / 2})
                        stepCount += 1
                        thisDirection = 1
                if (cornerX == 0 and cornerY == 1000):
                    if (int(getLocationReply['y']) <= 600):
                        botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi / 2})
                        stepCount += 1
                        thisDirection = 0
                    elif (int(getLocationReply['y']) >= 800):
                        botSocket.sendRecvMessage(
                            {'type': 'setDirectionRequest', 'requestedDirection': (3 * math.pi) / 2})
                        stepCount += 1
                        thisDirection = 1
                if (cornerX == 1000 and cornerY == 1000):
                    if (int(getLocationReply['y']) <= 600):
                        botSocket.sendRecvMessage({'type': 'setDirectionRequest', 'requestedDirection': math.pi / 2})
                        stepCount += 1
                        thisDirection = 0
                    elif (int(getLocationReply['y']) >= 800):
                        botSocket.sendRecvMessage(
                            {'type': 'setDirectionRequest', 'requestedDirection': (3 * math.pi) / 2})
                        stepCount += 1
                        thisDirection = 1

            previousX = getLocationReply['x']
            previousY = getLocationReply['y']
        except nbipc.NetBotSocketException as e:
            # Consider this a warning here. It may simply be that a request returned
            # an Error reply because our health == 0 since we last checked. We can
            # continue until the next game starts.
            log(str(e), "WARNING")
            continue

##################################################################
# Standard stuff below.
##################################################################
def checkShot():
    global currentMode
    global shotCount
    global smallestDistance
    global savedDirection
    global stepCount
    stepDif = stepCount - shotCount
    if ((stepDif + 8) * 40 >= smallestDistance):
        scanReply = botSocket.sendRecvMessage(
            {'type': 'scanRequest', 'startRadians': 0, 'endRadians': 2 * math.pi})
        stepCount += 1
        smallestDistance = scanReply['distance']
        binarySearch(0, 64)
def binarySearch(l, r):
    # Check base case
    if r >= l:
        global currentMode
        global savedDirection
        global smallestDistance
        global previousX
        global previousY
        global shotX
        global shotY
        global stepCount
        global shotCount
        mid = (l + r) / 2
        # If element is present at the middle itself
        if (mid >= r - 1):
            fireDirection = ((((mid + r) / 2) / 64) * 2 * math.pi)
            savedDirection = (mid + r) / 2
            currentMode = "wait"
            tempX = smallestDistance * math.cos(fireDirection)
            tempY = smallestDistance * math.sin(fireDirection)
            if (nbmath.distance(shotX, shotY, tempX, tempY) < 30 and shotX != -1):
                tempSteps = smallestDistance // 40
                tempAngle = nbmath.angle(shotX, shotY, tempX, tempY)
                v = nbmath.distance(tempX, tempY, shotX, shotY)
                newX = previousX + (math.cos(tempAngle) * tempSteps * v)
                newY = previousY + (math.sin(tempAngle) * tempSteps * v)
                newAngle = nbmath.angle(previousX, previousY, newX,newY)
                botSocket.sendRecvMessage(
                    {'type': 'fireCanonRequest', 'direction': newAngle, 'distance': smallestDistance})
            else:
                botSocket.sendRecvMessage(
                    {'type': 'fireCanonRequest', 'direction': fireDirection, 'distance': smallestDistance})
            stepCount += 1
            shotCount = stepCount
            shotX = tempX
            shotY = tempY
            return
        elif (mid <= l + 1):
            fireDirection = ((((mid + l) / 2) / 64) * 2 * math.pi)
            savedDirection = (mid + l) / 2
            currentMode = "wait"
            tempX = smallestDistance * math.cos(fireDirection)
            tempY = smallestDistance * math.sin(fireDirection)
            if (nbmath.distance(shotX, shotY, tempX, tempY) < 30 and shotX != -1):
                tempSteps = smallestDistance // 40
                tempAngle = nbmath.angle(shotX, shotY, tempX, tempY)
                v = nbmath.distance(tempX, tempY, shotX, shotY)
                newX = previousX + (math.cos(tempAngle) * tempSteps * v)
                newY = previousY + (math.sin(tempAngle) * tempSteps * v)
                newAngle = nbmath.angle(previousX, previousY, newX,newY)
                botSocket.sendRecvMessage(
                    {'type': 'fireCanonRequest', 'direction': newAngle, 'distance': smallestDistance})
            else:
                botSocket.sendRecvMessage(
                    {'type': 'fireCanonRequest', 'direction': fireDirection, 'distance': smallestDistance})
            stepCount += 1
            shotCount = stepCount
            shotX = tempX
            shotY = tempY
            return
        scanReply = botSocket.sendRecvMessage(
            {'type': 'scanRequest', 'startRadians': (l / 64) * 2 * math.pi, 'endRadians': (mid / 64) * 2 * math.pi})
        stepCount += 1
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
