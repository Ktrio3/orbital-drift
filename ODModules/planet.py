#############################
# Planet.py
# Created by: Kevin Dennis, 2016-09-06
#
# Purpose: The planet class contains methods for plotting a planet using
#   Kepler's planetary laws
#############################

import math


class Planet:

    ########
    # Values of Planet class
    ########
    #
    # name -> String, name of planet
    # orbitX -> array
    # orbitY -> array
    # orbitZ -> array
    #
    # NOTE: All orbital elements are updated constantly while drawing the
    #   orbits. There is currently no tracking of these values while graphing.
    #
    #
    # VARIABLES ADDED BY VSOP87
    # eclipLong -> float, radians, ecliptical longitude
    # helioLat  -> float, radians, heliocentric latitude
    # radVector -> float, radians, radius vactor
    #
    # VARIABLES ADDED BY SchlyterCalc
    # longAscNode -> float, longitude of the ascending node
    # incElip -> float, inclination to the ecliptic
    # argPerih -> float, argument of perihelion
    # semiMajAx -> float, semi-major axis
    # meanAnom -> float, Radians. Mean Anomaly
    # eccen -> float, Radians. Eccentricity.
    # eccenAnom -> float, Radians. Eccentic Anomaly.
    # distance -> float, distance from sun
    # xAnom -> float, x Anomaly
    # yAnom -> float, y Anomaly
    # anom -> true Anomaly

    ################
    # __init__
    ################
    # Creates a planet object and initializes the planet data using the info
    # provided in __________
    def __init__(self, name, epoch, dbResults):
        self.epoch = epoch
        if dbResults != 0:
            self.name = dbResults['planet_name']
            self.id = dbResults['id']
            self.num_moons = dbResults['num_moons']
            self.size_ratio = dbResults['size_ratio']
            self.color = dbResults['default_color']
            self.orbit_color = dbResults['default_orbit_color']
            self.elements = {}
            self.orbitXSchlyter = []
            self.orbitYSchlyter = []
            self.orbitZSchlyter = []
            self.orbitXVSOP = []
            self.orbitYVSOP = []
            self.orbitZVSOP = []
            self.method = []

    ###############################
    # setElements
    ###############################
    # Creates the dictionary of elements for the planet from the database.
    # Note that this does not retrieve coefficients or terms. It retrieves the
    # name and id of each element and places it in the dictionary.
    def setElementsDict(self, dbInterface):
        data = dbInterface.getAllElements()
        for element in data:
            self.elements[element['variable']] = {
                "id": element['id'],
                "name": element['element_name'],
                "units": element['units'],
            }

    ###############################
    # setSchlyterTerms
    ###############################
    # Retrieves the terms used for the Schlyter method from the database
    #   and adds them to the DB.
    def setSchlyterTerms(self, dbInterface):
        for key in self.elements:
            data = dbInterface.getSchlyterTerms(
                    self.id, self.elements[key]['id'])
            self.elements[key]['coefficient'] = data[0]['coefficient']
            self.elements[key]['constant'] = data[0]['constant']
