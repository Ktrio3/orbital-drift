#!/usr/bin/python

import sqlite3
import os


class PlanetDBInterface:

    # Open database when the class is created
    def __init__(self):

        # The database is contained in the data folder in the directory this
        #   file is contained in
        dirPath = os.path.dirname(os.path.realpath(__file__))
        self.connection = sqlite3.connect(dirPath + '/data/planet.db')

        # Set row_factory to return 'dict' with column names as key
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    # Close the database when object is deleted
    def __del__(self):
        self.connection.close()

    ###############################
    # getPlanet
    ###############################
    # Retrieves the information about a planet from the database and returns
    # the values.
    def getPlanet(self, name):
        # This search allows you to use e or E for Earth, or even Eart
        # Note that if an M is entered, it will assume you mean Mars and not
        #   Mercury. Mercury must be Me...
        search = (name + "%",)

        self.cursor.execute('''
            SELECT * FROM planets WHERE planet_name LIKE ?''', search)
        result = self.cursor.fetchone()

        if result is None:
            str = "Error -- Could not find planet: " + name
            # print(str, file=sys.stderr)
            return 0
        return result

    ###############################
    # getAllElements
    ###############################
    # Retrieves the information about all elements from the database
    #
    # OUTPUT:
    #   Dictionary containing results
    def getAllElements(self):
        self.cursor.execute('''
            SELECT * FROM elements''')
        return self.cursor.fetchall()

    ###############################
    # getElement
    ###############################
    # Retrieves the information about a given element from the database
    #
    # INPUT:
    #   element - string, name of element to find
    # OUTPUT:
    #   Dictionary containing results
    def getElement(self, element):
        search(element, )

        self.cursor.execute('''
            SELECT * FROM elements WHERE variable = ?''', search)
        return self.cursor.fetchall()

    ###############################
    # getSchlyterTerms
    ###############################
    # Retrieves the coefficient and constant for calculating the given element
    # for a given planet
    #
    # INPUT:
    #   planet_id - int, id of the planet to find terms for
    #   element_id - int, id of the element to find terms for
    # OUTPUT:
    #   Dictionary containing results
    def getSchlyterTerms(self, planet_id, element_id):
        search = (planet_id, element_id,)

        self.cursor.execute('''
            SELECT * FROM schlyter_terms WHERE planet_id = ?
                AND element_id = ?''', search)
        return self.cursor.fetchall()
