#!/usr/bin/python

##########################################
# Filename: planetDB.py
#
# Creates the planetDB sqlite database if it has not been created. In the
# future, will allow users to insert new values.
##########################################

import sqlite3
import csv
import os


###############################
# table_exists
###############################
# Returns true if the given string is the name of a table in the planet_db
def table_exists(name, cursor):
    values = (name,)
    cursor.execute(''' SELECT COUNT(*) FROM sqlite_master
        WHERE type="table" AND name=?''', values)
    count = cursor.fetchone()
    return count[0] > 0
################################################################

# "Connect" to the database
if not os.path.isfile('data/planet.db'):
    print "Creating planetDB sqlite database..."
conn = sqlite3.connect('data/planet.db')

conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Create the planets table if it doesn't exist
if not table_exists('planets', cursor):
    cursor.execute('''
        CREATE TABLE planets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,planet_name TEXT,
            num_moons INT, size_ratio REAL, default_color TEXT,
            default_orbit_color TEXT)''')
    # Populate DB with planet info
    with open('data/planets.csv', 'rb') as fin:
        dr = csv.DictReader(fin)
        to_db = [(
            i['id'], i['planet_name'], i['num_moons'], i['size_ratio'],
            i['default_color'], i['default_orbit_color']) for i in dr]

    cursor.executemany(
        '''INSERT INTO planets (id, planet_name, num_moons, size_ratio, default_color,
            default_orbit_color) VALUES (?, ?, ?, ?, ?, ?);''', to_db)

    print "Created table: planets"

# Create the elements table if it doesn't exist
if not table_exists('elements', cursor):
    cursor.execute('''
        CREATE TABLE elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, element_name text,
            variable TEXT, units TEXT)''')
    # Populate DB with elements
    with open('data/elements.csv', 'rb') as fin:
        dr = csv.DictReader(fin)
        to_db = [(
            i['id'], i['element_name'],
            i['variable'], i['units']) for i in dr]

    cursor.executemany(
        '''INSERT INTO elements (id, element_name, variable, units)
        VALUES (?, ?, ?, ?);''', to_db)

    print "Created table: elements"

# Create the schlyter_terms table
if not table_exists('schlyter_terms', cursor):
    cursor.execute('''
        CREATE TABLE schlyter_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT, planet_id INTEGER,
            element_id INTEGER, coefficient REAL, constant REAL,
            FOREIGN KEY(planet_id) REFERENCES planets(id),
            FOREIGN KEY(element_id) REFERENCES elements(id))''')

    # Populate the schylter terms coefficients
    with open('data/schlyter_terms.csv', 'rb') as fin:
        dr = csv.DictReader(fin)
        to_db = [(
            i['planet_id'], i['element_id'], i['coefficient'],
            i['constant']) for i in dr]

    cursor.executemany(
        '''INSERT INTO schlyter_terms (planet_id, element_id, coefficient, constant)
        VALUES (?, ?, ?, ?);''', to_db)

    print "Created table: schlyter_terms"

# Create the vsop87 terms
if not table_exists('vsop87terms', cursor):
    # Note that c will default to 0 if not specified
    cursor.execute('''
        CREATE TABLE vsop87terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT, planet_id INTEGER,
            term TEXT, A REAL, B REAL, C REAL DEFAULT 0.0, order_term INT,
            FOREIGN KEY(planet_id) REFERENCES planets(id))''')

    cursor.execute('''SELECT * FROM planets;''')
    to_db = []

    termsDictionary = {"1": 'X', "2": 'Y', "3": "Z"}

    # Get each term for the VSOP87 method
    for planet in cursor.fetchall():
        try:
            # Files take the form VSOP87C.Earth.txt
            fileName = 'data/VSOP87C_Data/VSOP87C.'
            fileName += planet['planet_name'] + '.txt'
            with open(fileName, 'rb') as fin:
                dr = csv.DictReader(fin, delimiter=' ',)
                # Add each triplet for each term
                for count, i in enumerate(dr):
                    # Decode the term. i.e. 3120 is Version 3, for Mercury,
                    #   element Y, term 0. We only need element and term
                    termString = str(i['Term'])
                    term = termsDictionary[termString[2]] + termString[3]

                    to_db.append([
                        planet['id'], term, i['A'], i['B'], i['C'], count
                    ])

            # Insert values into db
            cursor.executemany(
                '''INSERT INTO vsop87terms (planet_id, term, A, B, C, order_term)
                VALUES (?, ?, ?, ?, ?, ?);''', to_db)
            to_db = []  # Clear to_db for next planet
        except IOError:
            strValue = 'VSOP87 terms for ' + planet['planet_name']
            strValue += ' were not found.'
            print strValue

    print "Created table: vsop87terms"

print "Opened planet database. Welcome."

# This was originally intended to be a more interactive database interface,
#   which allowed users to enter information about a celestial body to be
#   graphed with the program. This functionality was left out to leave more
#   time to create a more detailed and visually appealing error reporting
#   with the ability to save to a file

conn.commit()
conn.close()
