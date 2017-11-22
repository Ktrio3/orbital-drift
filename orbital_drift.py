#!/usr/bin/python

###############################
# FileName: orbital_drift.py
# Created by Kevin Dennis, 2016-8-31
# Last modified 2016-8-31
# Purpose: Runs the planet plotter program
#   Reads in options from the command line
###############################

from datetime import datetime, timedelta
import sys
import copy

from ODModules.planetDBInterface import PlanetDBInterface
from ODModules.planet import Planet
import ODModules.SchlyterCalc as SchlyterCalc
import ODModules.plotManager as plotManager
import ODModules.reporting as reporting
import ODModules.horizonsConnection as horiz
import ODModules.VSOP87 as VSOP87

#############################
# Default Main Options
#############################

# Sun will be graphed by default. -n or --nosun
noSun = False

# Galileo was never born. Planets are geocentric. -g or --galileo
noGalileo = False

# Determines which planet to use as the center. -c --center
#   NOTE: If noGalileo is not set, this will set it
centralPlanet = "Earth"

# Don't graph any objects. -ng or --nograph
graph = True

# Ignores check for number of points. -fg or --forcegraph
forceGraph = False

# The maximum number of points that will be graphed
maxPoints = 25000

# Calculate difference in methods Schlyter and VSOP87. -nd or --nodiff
noDifference = False

# Pull data from NASA's Horizons tool. -h or --horiz
noHorizon = True

# File to output the calculated method differences. -o or --output
#   A blank output will output to stdout
outputFile = ""

# If true, graphs the points obtained from the Horizon project
#   -gh or --graphhorizon
graphHorizon = False

# Defines the method to use when calculating the planet's position.
#   "Sch" -> SchlyterCalc    -s or --schlyter
#   "VSO" -> VSOP87          -vs or --vsop87
# Used as such: Earth Mars -vs Earth Mars Venus
#   The above will graph Earth and Mars with Schlyter and VSOP87, and Venus
#   with VSOP87
method = "Sch"

# Timer for entire program. -t or --mastertimer
masterTimer = False

# Default start date is today
#   dateStart -> -d --date
#   dateEnd -> -e --dateend
dateStart = datetime.now()

###########################
# End options
###########################

# Help text if no args entered -- NOTE: Update this
if(len(sys.argv) < 2):
    pStr = "To graph the planets, run the program followed by the names "
    pStr += "of the planets you would like graphed."
    print(pStr)
    pStr = "For options and more examples, please view readme.md"
    print(pStr)

    print("Example: " + sys.argv[0] + " Earth Mars")
    exit()

planets = []
db = PlanetDBInterface()  # Creates the object to handle database reads

# Process and set options -- See above list for descriptions
for i in range(1, len(sys.argv)):
    if sys.argv[i] == "-g" or sys.argv[i] == "--galileo":
        noGalileo = True
    elif sys.argv[i] == "-c" or sys.argv[i] == "--center":
        noGalileo = True
        i = i + 1
        centralPlanet = sys.argv[i]
    elif sys.argv[i] == "-n" or sys.argv[i] == "--nosun":
        noSun = True
    elif sys.argv[i] == "-s" or sys.argv[i] == "--schlyter":
        method = "Sch"
    elif sys.argv[i] == "-vs" or sys.argv[i] == "--vsop87":
        method = "VSO"
    elif sys.argv[i] == "-gh" or sys.argv[i] == "--graphhorizon":
        graphHorizon = True
    elif sys.argv[i] == "-t" or sys.argv[i] == "--mastertimer":
        masterTimer = True
    elif sys.argv[i] == "-nd" or sys.argv[i] == "--nodiff":
        noDifference = True
    elif sys.argv[i] == "-h" or sys.argv[i] == "--horiz":
        noHorizon = False
    elif sys.argv[i] == "-ng" or sys.argv[i] == "--nograph":
        graph = False
    elif sys.argv[i] == "-fg" or sys.argv[i] == "--forcegraph":
        forceGraph = True
    elif sys.argv[i] == "-o" or sys.argv[i] == "--output":
        i += 1
        outputFile = sys.argv[i]
    elif sys.argv[i] == "-o" or sys.argv[i] == "--output":
        i += 1
        output = sys.argv[i]
    elif sys.argv[i] == "-d" or sys.argv[i] == "--date":
        i += 1
        dateStart = datetime.strptime(sys.argv[i], '%Y-%m-%d')
        if 'dateEnd' in locals():
            if dateEnd < dateStart:
                print("The start date must be before the end date.")
                exit()
    elif sys.argv[i] == "-e" or sys.argv[i] == "--dateend":
        i += 1
        dateEnd = datetime.strptime(sys.argv[i], '%Y-%m-%d')
        if dateEnd < dateStart:
            out = "The end date must be after the start date."
            out += " The default date is today."
            print(out)
            exit()
    else:
        # This must be a planet name, if it did not match any options
        dbResults = db.getPlanet(sys.argv[i])  # Find planet in DB
        # If found in db, add to planets
        if dbResults != 0:
            found = False
            for planet in planets:
                if(planet.name == dbResults['planet_name']):
                    # Planet has already been added to planet array.
                    #   Add new method, if method is new
                    if(method not in planet.method):
                        planet.method.append(method)
                    found = True
            if not found:
                # Add new planet to planets array
                planets.append(Planet(sys.argv[i], 0000, dbResults))
                planets[-1].method.append(method)

# Start timer for whole program
if(masterTimer):
    timer = reporting.startTimer()

# Default length is one year
if 'dateEnd' not in locals():
    dateEnd = dateStart + timedelta(days=365)

dayDifference = dateEnd - dateStart

# Test if graphing should be done. If more than maxPoints points, don't graph
if not forceGraph and graph:
    numDays = dayDifference.days
    numPoints = 0
    for planet in planets:
        numMethods = len(planet.method)
        if(graphHorizon):
            numMethods + 1
        # Each planet gets graphed once every day, for each method it has
        numPoints = numPoints + numDays * numMethods

    if(numPoints > maxPoints):
        # Print warning and set graph option to false
        graph = False
        strout = "Graphing will result in " + str(numPoints) + " points. "
        strout += "The recommended number of points is under " + str(maxPoints)
        print(strout)
        print("To graph these planets, run with -fg (--forcegraph).")

# If graphing, create a place to hold graphs
if graph:
    graphs = []

# Creating graphs for each in planet
for planet in planets:
    # Run Schlyter method
    if("Sch" in planet.method):
        planet.setElementsDict(db)  # Create dictionary of Schylter elements
        planet.setSchlyterTerms(db)  # Set the values for each element
        # For every day in range, run the calculations
        for i in range(dayDifference.days + 1):
            newDate = dateStart + timedelta(days=i)
            # Calculate points, and save in planet object
            SchlyterCalc.runSchlyterCalc(planet, newDate, [])

    # Run VSOP87 method
    if("VSO" in planet.method):
        # No setup needed for VSOP87. Run once each day
        for i in range(dayDifference.days + 1):
            newDate = dateStart + timedelta(days=i)
            VSOP87.runVSOP87(planet, newDate, db.cursor)

# Retrieve horizon info if requested.
if(graphHorizon or not noHorizon):
    # Retrieves horizon info for each planet in date range
    horiz.calculatePlanets(planets, dateStart, dateEnd, 0)

# If geocentric coordinates requested, subtract origin from each planet
# NOTE: When revisiting project in future, functionize this mess
origin = False
if noGalileo:
    # Find each method needed
    neededMethods = []
    for planet in planets:
        for method in planet.method:
            if method not in neededMethods:
                neededMethods.append(method)
        # If origin is already done, use points found
        if planet.name == centralPlanet:
            origin = copy.copy(planet)
    if origin is False:
        # Did not find an origin object.
        dbResults = db.getPlanet(centralPlanet)
        origin = Planet(centralPlanet, 0000, dbResults)
        if graphHorizon or not noHorizon:
            neededMethods.append("Hori")

    # For each method needed, calculate for orgin if not done yet
    for method in neededMethods:
        if method not in origin.method:
            if method is "Sch":
                origin.method.append("Sch")
                origin.setElementsDict(db)
                origin.setSchlyterTerms(db)  # Set the values for each element
                # For every day in range, run the calculations
                for i in range(dayDifference.days + 1):
                    newDate = dateStart + timedelta(days=i)
                    # Calculate points, and save in planet object
                    SchlyterCalc.runSchlyterCalc(origin, newDate, [])
            if method is "VSO":
                # No setup needed for VSOP87. Run once each day
                origin.method.append("VSO")
                for i in range(dayDifference.days + 1):
                    newDate = dateStart + timedelta(days=i)
                    VSOP87.runVSOP87(origin, newDate, db.cursor)
            if method is "Hori":
                horiz.calculatePlanets([origin], dateStart, dateEnd, 0)

    # Subtract origin's coordinates for each planet for each method
    for planet in planets:
        if "Sch" in planet.method:
            x = []
            x[:] = [planet.orbitXSchlyter[i] - origin.orbitXSchlyter[i]
                    for i in range(0, len(origin.orbitXSchlyter))]
            planet.orbitXSchlyter = x
            y = []
            y[:] = [planet.orbitYSchlyter[i] - origin.orbitYSchlyter[i]
                    for i in range(0, len(origin.orbitYSchlyter))]
            planet.orbitYSchlyter = y
            z = []
            z[:] = [planet.orbitZSchlyter[i] - origin.orbitZSchlyter[i]
                    for i in range(0, len(origin.orbitZSchlyter))]
            planet.orbitZSchlyter = z
        if "VSO" in planet.method:
            x = []
            x[:] = [planet.orbitXVSOP[i] - origin.orbitXVSOP[i]
                    for i in range(0, len(origin.orbitXVSOP))]
            planet.orbitXVSOP = x
            y = []
            y[:] = [planet.orbitYVSOP[i] - origin.orbitYVSOP[i]
                    for i in range(0, len(origin.orbitYVSOP))]
            planet.orbitYVSOP = y
            z = []
            z[:] = [planet.orbitZVSOP[i] - origin.orbitZVSOP[i]
                    for i in range(0, len(origin.orbitZVSOP))]
            planet.orbitZVSOP = z
        if graphHorizon or not noHorizon:
            x = []
            x[:] = [planet.horizonX[i] - origin.horizonX[i]
                    for i in range(0, len(origin.horizonX))]
            planet.horizonX = x
            y = []
            y[:] = [planet.horizonY[i] - origin.horizonY[i]
                    for i in range(0, len(origin.horizonY))]
            planet.horizonY = y
            z = []
            z[:] = [planet.horizonZ[i] - origin.horizonZ[i]
                    for i in range(0, len(origin.horizonZ))]
            planet.horizonZ = z

# Add each planet for graphing
if graph:
    for planet in planets:
        # Add Schlyter method
        if("Sch" in planet.method):
            # If graphing, add the points to a graphObject
            if graph:
                points = {'X': planet.orbitXSchlyter,
                          'Y': planet.orbitYSchlyter,
                          'Z': planet.orbitZSchlyter}
                graphObject = plotManager.createOrbitGraphObject(
                    planet.name, "Schlyter", planet.orbit_color, points)
                graphs.append(graphObject)

        # Add VSOP87 method
        if("VSO" in planet.method):
            # If graphing, add the points to a graphObject
            if graph:
                points = {'X': planet.orbitXVSOP, 'Y': planet.orbitYVSOP,
                          'Z': planet.orbitZVSOP}
                graphObject = plotManager.createOrbitGraphObject(
                        planet.name, "VSOP87", planet.orbit_color, points)
                graphs.append(graphObject)

        # If graphing, add the points to a graphObject
        if(graphHorizon):
                points = {'X': planet.horizonX, 'Y': planet.horizonY,
                          'Z': planet.horizonZ}
                graphObject = plotManager.createOrbitGraphObject(
                    planet.name, "Horizon", planet.orbit_color, points)
                graphs.append(graphObject)

# Output difference file
if not noDifference:
    includeHorizon = not noHorizon or graphHorizon
    reporting.outputDifferenceFile(planets, outputFile, includeHorizon)

# Add the sun, unless not requested
if not noSun and graph:
    # If geocentric coordinates, the "Sun" is just the origin's coordinates
    if noGalileo:
        if("Sch" in origin.method):
            # If graphing, add the points to a graphObject
            if graph:
                points = {'X': origin.orbitXSchlyter,
                          'Y': origin.orbitYSchlyter,
                          'Z': origin.orbitZSchlyter}
                graphObject = plotManager.createOrbitGraphObject(
                    "Sun", "Schlyter", "#E9C300", points)
                graphs.append(graphObject)

        # Add VSOP87 method
        if("VSO" in origin.method):
            # If graphing, add the points to a graphObject
            if graph:
                points = {'X': origin.orbitXVSOP, 'Y': origin.orbitYVSOP,
                          'Z': origin.orbitZVSOP}
                graphObject = plotManager.createOrbitGraphObject(
                        "Sun", "VSOP87", "#E9C300", points)
                graphs.append(graphObject)

        # If graphing, add the points to a graphObject
        if(graphHorizon):
                points = {'X': origin.horizonX, 'Y': origin.horizonY,
                          'Z': origin.horizonZ}
                graphObject = plotManager.createOrbitGraphObject(
                    "Sun", "Horizon", "#E9C300", points)
                graphs.append(graphObject)
    else:
        graphs.append(plotManager.addSun())

# If graphing, create layout, then graph
if graph:
    layout = plotManager.createGraphLayout()
    plotManager.createPlot(graphs, layout)

# Finish timing
if(masterTimer):
    print("Total time taken: " + str(reporting.endTimer(timer)))
