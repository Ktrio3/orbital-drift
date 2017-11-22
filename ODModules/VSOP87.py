#!/usr/bin/python

###############################
# FileName: VSOP87.py
# Created by Kevin Dennis, 2016-9-13
# Purpose: Contains the functions necessary for calculating the locations
#   of the planets using VSOP87-C method as described in
#   Astronomical Algorithms by Jean Meeus
#
#   NOTE: The functions for VSOP87-A have been left in the file,
#   in case they are added to the program as an option in the future
###############################

import math as Math
from datetime import datetime, timedelta
import reporting


###############################
# runVSOP87
###############################
# Calls the functions needed to run the VSOP87
#   method
def runVSOP87(planet, date, db):
    # Start timer and pull planet info from DB
    timer = reporting.startTimer()
    data = (planet.id,)

    # Retrieve all the terms for the given planet (Not all planets have all
    #   five terms)
    db.execute('''
        SELECT DISTINCT term FROM vsop87terms WHERE planet_id = ?
    ''', data)

    terms = db.fetchall()

    # All term values start at zero, and will be replaced if the planet has
    #   that term
    termValues = {
        'X0': 0, 'X1': 0, 'X2': 0, 'X3': 0, 'X4': 0, 'X5': 0,
        'Y0': 0, 'Y1': 0, 'Y2': 0, 'Y3': 0, 'Y4': 0, 'Y5': 0,
        'Z0': 0, 'Z1': 0, 'Z2': 0, 'Z3': 0, 'Z4': 0, 'Z5': 0}

    # Convert the standard date to its JDN equivalent
    JDN = calculateJDN(date)

    # Using JDN, calculate the Julian Millenia
    time = calculateJMillenia(JDN)
    # Calculate the term
    for term in terms:
        termValues[term[0]] = calculateTerm(planet, term[0], time, db)

    # Calculate the final value for each value
    calculateXYZTerms(planet, termValues, time)

    # Add this run's time to the total time
    try:
        planet.VSOPTime += reporting.endTimer(timer)
    except AttributeError:
        planet.VSOPTime = reporting.endTimer(timer)  # Create attribute


###############################
# calculatePoint
###############################
# Takes the calculated values from the VSOP87 method, and add the point
#   NOTE: This function was built for VSOP87-A, which is used to calculate
#   Spherical coordinates. Due to issues converting spherical coordinates,
#   this function has been replaced by calculateXYZTerms
def calculatePoint(planet):
    R = planet.radVector
    B = planet.helioLat
    L = planet.eclipLong

    x = R * Math.cos(B) * Math.cos(L)
    y = R * Math.cos(B) * Math.sin(L)
    z = R * Math.sin(B)

    planet.orbitXVSOP.append(x)
    planet.orbitYVSOP.append(y)
    planet.orbitZVSOP.append(z)


###############################
# calculateXYZTerms
###############################
# Takes the calculated values from the VSOP87 method, and adds the
#   coordinate to the planet object. This properly implements VSOP87-C,
#   which calculates rectangular coordinates
def calculateXYZTerms(planet, terms, time):
    x = 0
    y = 0
    z = 0

    # The formula takes the form:
    #   E * t^6 + E * t^5 + E * t^4 ...

    # terms['E' + str(i)] finds the term
    #   for E * t ^ i, where E is the value in the array
    for i in range(0, 6):
        x = x + terms['X' + str(i)] * Math.pow(time, i)
    for i in range(0, 6):
        y = y + terms['Y' + str(i)] * Math.pow(time, i)
    for i in range(0, 6):
        z = z + terms['Z' + str(i)] * Math.pow(time, i)

    planet.orbitXVSOP.append(x)
    planet.orbitYVSOP.append(y)
    planet.orbitZVSOP.append(z)


###############################
# calculateFinalTerms
###############################
# This functions is equivalent to the above,
#   calculateXYZTerms, except that it does not directly
#   calculate the terms as points. Instead, it adds the results to the
#   the planet to be used in the old calculatePoint function
#   for VSOP87-A, which was replaced
def calculateFinalTerms(planet, terms, time):
    planet.eclipLong = 0
    planet.helioLat = 0
    planet.radVector = 0

    for i in range(0, 6):
        planet.eclipLong += terms['L' + str(i)] * Math.pow(time, i)
    for i in range(0, 6):
        planet.helioLat += terms['B' + str(i)] * Math.pow(time, i)
    for i in range(0, 6):
        planet.radVector += terms['R' + str(i)] * Math.pow(time, i)


###############################
# calculateTerm
###############################
# Calculates the exponents to be used
#   in calculateXYZTerms using the terms stored
#   in the DB.
def calculateTerm(planet, term, time, db):
    data = (planet.id, term, )

    db.execute('''
        SELECT * FROM vsop87terms WHERE planet_id = ? AND term = ?
    ''', data)

    terms = db.fetchall()
    value = 0

    for term in terms:
        value += term['A'] * Math.cos(term['B'] + (term['C'] * time))

    return value


###############################
# calculateJDE
###############################
# Converts a standard date to it's JDE
#   equivalent using the process described below
#
#   The final JDE date takes the form CYYDDD
#
#   NOTE: The JDE method ended up being replaced by the
#       Julian Day Number, calculateJDN
def calculateJDE(date):
    # First, calculate the century, with 2000 being century 1
    JDE = (date.year - 2000 + 100) * 1000

    # Note that the above will also put our year in the YY spot i.e. 2016 gives
    #   116000, which is the correct CYY.
    #
    # Calculating the day is a little more hands on. The DDD should be the day
    #   ranging from 1 to 365. i.e. Jan 1st gives 001 and Dec 31st, gives 365
    #   (unless it is a leapyear, which will give 366). Since we are using the
    #   datetime and timedelta object, leapyears will be accounted for.
    # To get this number, subtract the days of today from Jan 1st, and add 1
    dayDifference = date - datetime(date.year, 1, 1)
    days = dayDifference.days + 1

    # We now have CYYDDD
    JDE = JDE + days
    return JDE


###############################
# calculateJDN
###############################
# Converts a standard date to it's
#   JDN equivalent
def calculateJDN(date):
    a = Math.floor((14 - date.month) / 12)
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3

    JDN = date.day + Math.floor((153 * m + 2) / 5)
    JDN = JDN + 365 * y + Math.floor(y / 4)
    JDN = JDN - Math.floor(y / 100) + Math.floor(y / 400) - 32045
    return JDN


###############################
# calculateJD
###############################
# Converts a standard date to it's JD
#   equivalent using the process described below
def calculateJD(date):
    month = date.month
    year = date.year
    if(month == 1 or month == 2):
        year = year - 1
        month = month + 12

    A = Math.floor(year / 100)
    B = 2 - A + Math.floor(A / 4)

    JD = Math.floor(365.25 * (year + 4716))
    JD = JD + Math.floor(30.6001 * (month + 1))
    JD = JD + date.day + B - 1524.5
    return JD


###############################
# calculateJDE
###############################
# Converts the JDN into the
#   format necessary for the VSOP87 method
def calculateJMillenia(JDN):
    return (JDN - 2451545.0) / 365250
