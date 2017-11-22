#!/usr/bin/python

###############################
# FileName: plotManager.py
# Created by Kevin Dennis, 2016-9-27
#
# Purpose: Creates the necessary objects and formats necessary for plotting
#   the orbits and planets using plotly.
###############################

from plotly.offline import plot
import plotly.plotly as plotly
import plotly.graph_objs as graph


###############################
# createOrbitGraphObject
###############################
# Creates a plotly graph for given item
def createOrbitGraphObject(name, method, color, points):
    grapher = graph.Scatter3d(
        x=points['X'],
        y=points['Y'],
        z=points['Z'],
        name=name + " - " + method,
        # marker=dict(
        #    size=1,
        #    symbol='circle',
        #    color='rgb(232, 224, 2)',
        #    line=dict(
        #        color='rgba(232, 224, 2, .5)',
        #        width=2
        #    ),
        #    opacity=0.8
        # ),
        line=dict(
            color=color,
            width=1
        )
    )
    return grapher


###############################
# addSun
###############################
# Adds a sun graph object
def addSun():
    grapher = graph.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        name="Sun",
        marker=dict(
            size=10,
            symbol='circle',
            color='rgb(232, 224, 2)',
            opacity=0.8
        )
    )

    return grapher


###############################
# createPlanetGraphObject
###############################
# Adds a planet to the graph
#   This function is currently unused
#   as the planets size does not look good
#   when merged with the orbit.
def createPlanetGraphObject(planet):
    grapher = graph.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        marker=dict(
            size=10,
            symbol='circle',
            color='rgb(232, 224, 2)',
            opacity=0.8
        )
    )

    return grapher


###############################
# createGraphLayout
###############################
# Creates the layout for the plotly diagram
def createGraphLayout():
    # Setup layout -- "functionize" this
    layout = graph.Layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        )
    )
    return layout


###############################
# createPlot
###############################
# Takes the graphs, called data, and a layout,
#   and plots them using plotly
def createPlot(data, layout):
    # Create graph and plot to html file
    fig = graph.Figure(data=data, layout=layout)
    plot(fig)
