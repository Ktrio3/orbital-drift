#############################
# SchlyterCalc.py
# Created by: Kevin Dennis, 2016-09-12
#
# Purpose: Contains the functions necessary to calculate the orbital elements
#   needed to graph the planets as performed by Paul Schlyter at
#   http://www.stjarnhimlen.se/
#############################

import math
from planet import Planet
import reporting

#############################
# Options and default values for module
#############################

# Accuracy for eccentric anomoly calculations
#
accuracy = .000000001

# Method for calculating Eccentric Anomaly
#   Values: 0 => eccAnomApprox
#           1 => eccAnomIter1
#           2 => eccAnomIter2
methodForEccen = 1

# If 1, track time for calculation
time = 0

# An array of the time taken for each iteration of the
#   runSchlyterCalc function.
timeValues = []


################
# setTestMoon
################
# Sets the necessary values for Moon for testing purposes as described at
# http://stjarnhimlen.se/comp/tutorial.html
# Will be moved into database in future
# INPUT:
#
# OUTPUT:
#
def setTestMoon(planet, d):
    planet.longAscNode = math.radians(125.1228 - 0.0529538083 * d)
    planet.incElip = math.radians(5.1454)
    planet.argPerih = math.radians(318.0634 + 0.1643573223 * d)
    planet.semiMajAx = 60.2666
    planet.eccen = 0.054900
    planet.meanAnom = math.radians(115.3654 + 13.0649929509 * d)


###############################
# runSchlyterCalc
###############################
# Calls the functions necessary to perform the planetary calculations necessary
#   in order. Options that are passed are used to control the steps.
#
# INPUT:
#   planet - planet object to be used
#   date - a date object, contains the date to calculate
#   options - dict, contains the options passed in from the user
#       Relevant options will be listed here as they are added.
# OUTPUT:
#   boolean, returns 1 if no errors
def runSchlyterCalc(planet, date, options):
    timer = reporting.startTimer()
    time = convertToday(date)
    calculateElements(planet, time)
    eccAnomIter1(planet)
    calculateXYAnomaly(planet)
    calculatePlanetDistance1(planet)
    calculateAnomaly(planet)
    calculateHelioXYZ(planet)
    try:
        planet.SchlyterTime += reporting.endTimer(timer)
    except AttributeError:
        planet.SchlyterTime = reporting.endTimer(timer)


def calculateElements(planet, time):
    for key in planet.elements:
        value = planet.elements[key]['coefficient'] * time
        value = value + planet.elements[key]['constant']
        if planet.elements[key]['units'] == 'Rad':
            value = math.radians(value)
        planet.__dict__[key] = value


################
# calculateHelioXYZ
################
# The final function in the runSchlyterCalc. Calculates the 3-dimensional
#   heliocentric coordinates of the planet and appends them to the planets
#   orbit array
#
#   NOTE: May want to change output to make it possible to calculate geocentric
#
# xh = r * ( cos(N) * cos(v+w) - sin(N) * sin(v+w) * cos(i) )
# yh = r * ( sin(N) * cos(v+w) + cos(N) * sin(v+w) * cos(i) )
# zh = r * ( sin(v+w) * sin(i) )
#
# INPUT:
#   p - planet object to use
def calculateHelioXYZ(p):
    x = math.sin(p.longAscNode) * math.sin(p.anom + p.argPerih)
    x = x * math.cos(p.incElip)
    x = math.cos(p.longAscNode) * math.cos(p.anom + p.argPerih) - x
    x = x * p.semiMajAx

    y = math.cos(p.longAscNode) * math.sin(p.anom + p.argPerih)
    y = y * math.cos(p.incElip)
    y = math.sin(p.longAscNode) * math.cos(p.anom + p.argPerih) + y
    y = y * p.semiMajAx

    z = math.sin(p.anom + p.argPerih) * math.cos(p.incElip)
    z = z * p.semiMajAx

    p.orbitXSchlyter.append(x)
    p.orbitYSchlyter.append(y)
    p.orbitZSchlyter.append(z)


################
# calculateAnomaly
################
# v = atan2( yv, xv )
#
# INPUT:
#   p - planet object to use
def calculateAnomaly(p):
    p.anom = math.atan2(p.yAnom, p.xAnom)


################
# calculateXYAnomaly
################
#
#
#   xv = r * cos(v) = a * ( cos(E) - e )
#   yv = r * sin(v) = a * ( sqrt(1.0 - e*e) * sin(E) )
#
# INPUT:
#   p - planet object to use
def calculateXYAnomaly(p):
    p.xAnom = math.cos(p.eccenAnom) - p.eccen
    p.xAnom = p.semiMajAx * p.xAnom

    p.yAnom = math.sqrt(1.0 - p.eccen * p.eccen)
    p.yAnom = p.yAnom * math.sin(p.eccenAnom)
    p.yAnom = p.yAnom * p.semiMajAx


################
# calculatePlanetDistance1
################
# Calculates the distance to the sun. For use in the process described at
#   http://stjarnhimlen.se/comp/ppcomp.html
#
#   r = sqrt(xv*xv + yv*yv)
#   Where r is the planets distance, xv is the x anomaly, and yv is the
#   y anomaly
#
# INPUT:
#   p - planet object to use
def calculatePlanetDistance1(p):
    p.semiMajAx = math.sqrt(p.xAnom*p.xAnom+p.yAnom*p.yAnom)


################
# eccAnomIter1
################
# Calculates the eccentric anomaly using the Iterative method described in
# Chapter 30 of Astronomical Algorithms
#
# This function is an option when using the method for plotting planets
# found at http://stjarnhimlen.se/comp/ppcomp.html
#
# E = M + esinE
# where E is Eccentric anomaly, M is the mean anomaly in radians,
#   and e is the eccentricity in radians
def eccAnomIter1(planet):
    E0 = planet.meanAnom
    # Calculate first E1
    E1 = planet.meanAnom + planet.eccen * math.sin(E0)

    # NOTE: ADD ACCURACY OPTION HERE
    while (E1 - E0 > .000000001) or (E1 - E0 < -.000000001):
        E0 = E1
        E1 = planet.meanAnom + planet.eccen * math.sin(E0)
    planet.eccenAnom = E1


################
# eccAnomIter2
################
# Calculates the eccentric anomaly using the second Iterative method
# described in Chapter 30 of Astronomical Algorithms
#
# E1 = E0 + (M + e * sin(E0) - E0)/(1 - e*cos(E0))
# where E is Eccentric anomaly, M is the mean anomaly in degrees,
#   and e is the eccentricity in degrees
def eccAnomIter2(planet):
    E0 = planet.meanAnom  # E0 starts out equal to mean Anomoly

    # Calculate first E1
    E1 = planet.meanAnom + planet.eccen * math.sin(E0) - E0
    E1 = E1 / (1 - planet.eccen * math.cos(E0))
    E1 = E0 + E1

    # Calculate progessively more accurate eccenAnom
    # NOTE: ADD ACCURACY OPTION HERE
    while (E1 - E0 > .000000001) or (E1 - E0 < -.000000001):
        E0 = E1
        E1 = planet.meanAnom + planet.eccen * math.sin(E0) - E0
        E1 = E1 / (1 - planet.eccen * math.cos(E0))
        # Adjust using trick devised by John M. Steele
        if E1 > .5:
            E1 = .5
        if E1 < -.5:
            E1 = -.5
        E1 = E0 + E1
    planet.eccenAnom = E1


def eccAnomApprox(planet):
    blank


################
# convertDate()
################
# The convertToday function converts a standard date into the day number
#   form required for computing the orbits of the planets. This function
#   is specific to the calculation method found at
#   http://stjarnhimlen.se/comp/ppcomp.html
#
def convertToday(date):
    d = 367 * date.year
    d -= (7 * (date.year + ((date.month + 9) / 12))) / 4
    d += (275 * date.month) / 9
    d += date.day
    d -= 730530

    return d
