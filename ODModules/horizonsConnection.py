###############################
# FileName: horizonsConnection.py
# Created by Kevin Dennis, 2016-8-31
# Last modified 2016-8-31
# Purpose: Connects to Nasa's horizon project to
#   receive high-accuracy coordinates of
#   a given planet that can be used to compare
#   to the coordinates calculated by
#   another method.
###############################
from telnetlib import Telnet
import reporting

planetIDs = {'Mercury': "199", "Venus": "299", 'Earth': "399", "Mars": "499",
             "Jupiter": "599", "Saturn": "699", "Uranus": "799",
             "Neptune": "899"}


# Calculates the coordinates of several planets.
#
# INPUT:
#   planets -- array of planet names to calculate
#   dateStart -- the date that the coordinates should begin on
#   dateEnd -- the date that the coordinates should end on
#   interval -- the time interval to calculate
def calculatePlanets(planets, dateStart, dateEnd, interval):
    for planet in planets:
        # Start timer for Horizon method
        timer = reporting.startTimer()

        # Connect to Horizon telnet server
        try:
            tel = Telnet('horizons.jpl.nasa.gov', 6775)
        except:
            print("Error connecting to Horizons service.")
            print("For help troubleshooting, please visit:")
            print("http://ssd.jpl.nasa.gov/?horizons#telnet")
            exit()

        # Send id of planet to read when prompted
        tel.read_until('Horizons>')
        tel.write(planetIDs[planet.name] + "\n")

        # We want the results through the tenet connection, so choose E
        tel.read_until("Select ... [E]phemeris, [F]tp, [M]ail, [R]")
        tel.write("E\n")

        # We want Vectors, so we can receive 3D coordinates
        tel.read_until("Observe, Elements, Vectors  [o,e,v,?] :")
        tel.write("v\n")

        # We would like to center our coordinates on the sun -- Prompting
        #   center may be a nice future addition
        tel.read_until("Coordinate center [ <id>,coord,geo  ] :")
        tel.write("500@10\n")  # Sun's ID

        # Asks to confirm sun as center
        tel.read_until("Confirm selected station    [ y/n ] -->")
        tel.write("y\n")

        # Our reference plane is in the ecliptical
        tel.read_until("Reference plane [eclip, frame, body ] :")
        tel.write("eclip\n")

        # Need to format date to  match string
        tel.read_until(":")  # Prompt for start date
        tel.write(dateStart.strftime("%Y-%b-%d %H:%M") + "\n")
        tel.read_until(":")  # Prompt for end date.
        tel.write(dateEnd.strftime("%Y-%b-%d %H:%M") + "\n")

        # We output once a day with the other methods -- Time may be a nice
        #   future addition
        tel.read_until("Output interval [ex: 10m, 1h, 1d, ? ] :")
        tel.write("1d\n")

        # We want to format the output, so we can read it easier
        tel.read_until("Accept default output [ cr=(y), n, ?] :")
        tel.write("n\n")

        # The reference is in J2000 time
        tel.read_until("Output reference frame [J2000, B1950] :")
        tel.write("J2000\n")

        # Add the extra accuraccy for Light Time and Speed
        tel.read_until("Corrections [ 1=NONE, 2=LT, 3=LT+S ]  :")
        tel.write("3\n")

        # Receive units in Astronomical Units
        tel.read_until("Output units [1=KM-S, 2=AU-D, 3=KM-D] :")
        tel.write("2\n")
        tel.read_until("Spreadsheet CSV format    [ YES, NO ] :")
        tel.write("YES\n")
        tel.read_until("Output delta-T (TDB-UT)   [ YES, NO ] :")
        tel.write("NO\n")
        tel.read_until("Select output table type  [ 1-6, ?  ] :")
        tel.write("1\n")
        tel.read_until('$SOE')
        results = tel.read_until('$EOE')
        results = results.split("\r\n")
        results.remove('')
        results.remove('$$EOE')
        planet.horizonX = []
        planet.horizonY = []
        planet.horizonZ = []
        for result in results:
            values = result.split(", ")
            planet.horizonX.append(float(values[2]))
            planet.horizonY.append(float(values[3]))
            # value Z has a comma hanging on it
            valueZ = values[4].replace(',', '')
            planet.horizonZ.append(float(valueZ))
        tel.close()
        planet.horizonTime = reporting.endTimer(timer)
