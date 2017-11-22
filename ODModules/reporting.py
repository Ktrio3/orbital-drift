######################
# reporting.py
#
# Contains functions for tracking errors, calculation times, etc.
######################

import time
import sys
import math

# If True, only calculates time actively spent on this process
noSleep = False

# If run under python 3.3 or greater, allows advanced timing
noAdvancedTime = (sys.version_info < (3, 3))


###############################
# startTimer
###############################
# Starts a "timer" for tracking calculations
#   Records and saves current time
def startTimer():
    global noSleep
    global noAdvancedTime

    if(noAdvancedTime):
        timer = time.clock()
    elif(noSleep):
        timer = time.process_time()
    else:
        timer = time.perf_counter()
    return timer


###############################
# endTimer
###############################
# Ends a "timer" for tracking calculations
#   Subtracts the time recorded in startTimer from the current time
#   Returns the time object with the difference
def endTimer(timer):
    global noSleep
    global noAdvancedTime

    if(noAdvancedTime):
        return time.clock() - timer
    elif(noSleep):
        return time.process_time() - timer
    else:
        return time.perf_counter() - timer


###############################
# calculateDifference
###############################
# Calculates the average difference between the values in A and B
#   i.e. A[0] - B[0] + A[1] - B[1] ... / numItems
def calculateDifference(valuesA, valuesB):
    total = 0
    if(len(valuesA) != len(valuesB)):
        return null
    for i in range(0, len(valuesB)):
        total += (valuesB[i] - valuesA[i])
    return total / len(valuesB)


###############################
# outputDifferenceFile
###############################
# Creates and outputs the difference file, which lists
#   the average differences between the three methods
#   coordinates
#   NOTE: This is sloppy. This should be more functionized.
#       If time, split into several functions to be DRY.
def outputDifferenceFile(planets, output, horizon):
    # Header lines
    header = ["Planet", "DiffX", "DiffY", "DiffZ", "DiffDis", "Method1",
              "Method2", "M1Time", "M2Time"]
    headerOutput = 0  # We have not yet outputted the header

    for p in planets:
        # Compate VSOP87 and Schlyter
        if('VSO' in p.method and 'Sch' in p.method):
            # If the header has not been output, output it
            if not headerOutput:
                addHeaderLine(output, header)
                headerOutput = True
            line = []
            line.append(p.name)
            # Calculate difference between x,y and z
            line.append(calculateDifference(p.orbitXSchlyter, p.orbitXVSOP))
            line.append(calculateDifference(p.orbitYSchlyter, p.orbitYVSOP))
            line.append(calculateDifference(p.orbitZSchlyter, p.orbitZVSOP))

            # Now we want to calculate the average distance from each point
            # To do this, first subtract each point in method B from method A
            x = []
            x[:] = [p.orbitXSchlyter[i] - p.orbitXVSOP[i]
                    for i in range(0, len(p.orbitXSchlyter))]
            y = []
            y[:] = [p.orbitYSchlyter[i] - p.orbitYVSOP[i]
                    for i in range(0, len(p.orbitYSchlyter))]
            z = []
            z[:] = [p.orbitZSchlyter[i] - p.orbitZVSOP[i]
                    for i in range(0, len(p.orbitZSchlyter))]
            # Now that we have the difference between each x, y, and z,
            #   calculate the distance of each set of points
            d1 = distance(x, y, z)

            # Now d1 contains the distances between each point
            # Get the average distance by summing each and dividing
            line.append(sum(d1)/len(d1))

            # Add method names
            line.append("Schlyter")
            line.append('VSOP87')

            # Add execution times
            line.append(p.SchlyterTime)
            line.append(p.VSOPTime)

            # output line
            addLine(output, line)

        # Compare VSOP87 and Horizon
        if('VSO' in p.method and horizon):
            # If the header has not been output, output it
            if not headerOutput:
                addHeaderLine(output, header)
                headerOutput = True
            line = []
            line.append(p.name)
            # Calculate difference between x,y and z
            line.append(calculateDifference(p.orbitXVSOP, p.horizonX))
            line.append(calculateDifference(p.orbitYVSOP, p.horizonY))
            line.append(calculateDifference(p.orbitZVSOP, p.horizonZ))

            # Now we want to calculate the average distance from each point
            # To do this, first subtract each point in method B from method A
            x = []
            x[:] = [p.orbitXVSOP[i] - p.horizonX[i]
                    for i in range(0, len(p.orbitXVSOP))]
            y = []
            y[:] = [p.orbitYVSOP[i] - p.horizonY[i]
                    for i in range(0, len(p.orbitYVSOP))]
            z = []
            z[:] = [p.orbitZVSOP[i] - p.horizonZ[i]
                    for i in range(0, len(p.orbitZVSOP))]
            # Now that we have the difference between each x, y, and z,
            #   calculate the distance of each set of points
            d1 = distance(x, y, z)

            # Now d1 contains the distances between each point
            # Get the average distance by summing each and dividing
            line.append(sum(d1)/len(d1))

            # Add method names
            line.append("VSOP87")
            line.append('Horizon')

            # Add execution times
            line.append(p.VSOPTime)
            line.append(p.horizonTime)

            # Output line
            addLine(output, line)

        # Compare Schlyter and Horizon
        if('Sch' in p.method and horizon):
            if not headerOutput:
                addHeaderLine(output, header)
                headerOutput = True
            line = []
            line.append(p.name)
            # Calculate difference between x,y and z
            line.append(calculateDifference(p.orbitXSchlyter, p.horizonX))
            line.append(calculateDifference(p.orbitXSchlyter, p.horizonY))
            line.append(calculateDifference(p.orbitXSchlyter, p.horizonZ))

            # Now we want to calculate the average distance from each point
            # To do this, first subtract each point in method B from method A
            x = []
            x[:] = [p.orbitXSchlyter[i] - p.horizonX[i]
                    for i in range(0, len(p.orbitXSchlyter))]
            y = []
            y[:] = [p.orbitYSchlyter[i] - p.horizonY[i]
                    for i in range(0, len(p.orbitYSchlyter))]
            z = []
            z[:] = [p.orbitZSchlyter[i] - p.horizonZ[i]
                    for i in range(0, len(p.orbitZSchlyter))]
            # Now that we have the difference between each x, y, and z,
            #   calculate the distance of each set of points
            d1 = distance(x, y, z)

            # Now d1 contains the distances between each point
            # Get the average distance by summing each and dividing
            line.append(sum(d1)/len(d1))

            # Add method names
            line.append("Schlyter")
            line.append('Horizon')

            # Add execution times
            line.append(p.SchlyterTime)
            line.append(p.horizonTime)

            # Output line
            addLine(output, line)


###############################
# addHeaderLine
###############################
# Output the header, using the following format:
# ****Planet****  ***Header*** ... etc.
def addHeaderLine(output, values):
    out = '{0[0]:*^10}  {0[1]:*^14}  {0[2]:*^14}'.format(values)
    out += '  {0[3]:*^14}  {0[4]:*^14}  {0[5]:*^10}'.format(values)
    out += '  {0[6]:*^10}  {0[7]:*^14}  {0[8]:*^14}\n'.format(values)
    if output is not '':
        f = open(output, 'w')
        f.write(out)
        f.close
    else:
        print(out)


###############################
# addLine
###############################
# Output the given line, using the same
#   format as the header, without asterisks
def addLine(output, values):
    out = '{0[0]:^10}  {0[1]:^14.10f}  {0[2]:^14.10f}'.format(values)
    out += '  {0[3]:^14.10f}  {0[4]:^14.10f}  {0[5]:^10}'.format(values)
    out += '  {0[6]:^10}  {0[7]:^14.10f}  {0[8]:^14.10f}\n'.format(values)
    if output is not '':
        f = open(output, 'a')
        f.write(out)
        f.close
    else:
        print(out)


###############################
# distance
###############################
# Returns an array containing the distance
#   for each point from xyz = (0,0,0)
def distance(xVals, yVals, zVals):
    if(len(xVals) != len(yVals) or len(xVals) != len(zVals)):
        return false
    distance = []
    for i in range(0, len(xVals)):
        x = math.pow(xVals[i], 2)
        y = math.pow(yVals[i], 2)
        z = math.pow(zVals[i], 2)
        distance.append(math.sqrt(x + y + z))
    return distance
