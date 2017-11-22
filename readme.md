## Obrital_Drift.py

I ran and developed this program on Ubuntu 16.0.4

Currently, I am unaware of any bugs that prevent the program
from running, and have tested all of the below examples.

Input that is not identified as either a planet or command will
be ignored. Note that options that recquire a follow up
argument or a particular format will error out or cause
odd behavior if these conditions are not met. (i.e. -c requires
an argument, and -d and -e require dates formatted as
YYYY-MM-DD, etc.)

The only package that needs to be installed is Plotly, which is
available through pip.

Plotly may spit out some warning messages during execution, but
all of the messages I have encountered can be safely ignored for
the offline mode used for this project. (Unfortunately, Plotly
provides no means of silencing or changing the messages it
outputs.+)

On completion, Plotly will print a message to stdout (after a
new prompt has appeared), and will open the file in the
default web browser. I used Chrome during testing. In some
cases, this causes errors to be output to the terminal, but
these are typically from the browser, and all of the errors
I have seen are handled by it, and can be ignored.

An internet connection is necessary to use the Horizon options.
Typically, there are no issues connecting. I did have trouble on
a network at another university that blocked telnet for guest
users.

The VSOP87 method can take about a minute to run for a single
planet for a year. The other two methods typically take less
than a couple seconds to run.

### Examples

Below are several different example commands that can be run to
test out the orbital drift program.

A complete list of the available options and explanations of
their purpose can be found in the report.

Graphs Earth, Venus, and Mars using the Schlyter and Horizon
methods.

    ./orbital_drift.py E V Ma -gh

Graphs Earth, Venus, and Mars using the Schlyter, VSOP87 and
Horizon methods.

    ./orbital_drift.py E V Ma -vs E V Ma -gh

Saves report of the differences between planet calculations to
"out.txt", without graphing

    ./orbital_drift.py E V Ma -vs E V Ma -gh -o out.txt -ng

Graphs Earth with a timer for the program

    ./orbital_drift.py E -t

Graphs Earth from January 1st, 2001 to January 22nd, 2001

    ./orbital_drift.py E -d 2001-01-01 -e 2001-01-22

Graph the Sun and Mars using geocentric coordinates.

    ./orbital_drift.py M -g

Graphs only Mars and Earth using geocentric coordinates.

    ./orbital_drift.py M E -g -n

Graphs the Earth and Sun using Mars as the center.

    ./orbital_drift.py E -c M
