#!/usr/bin/env python 

#########
#Functions for extrating useful data from files in the the Data directory of the Alaska Section tool
#########

import os
import numpy as np
from obspy.fdsn import Client as fdsnClient
import datetime
from obspy import UTCDateTime


def getvolcanolocations():
	'''Opens the file of active volcano locations and returns their positions'''

	regioncoords = [188,237,51.0,73.0]
	infile = open('Data/Active_volanoes.csv','r')
	lines = infile.readlines()

	print len(lines)

	outfile = open('Alaska_volcanoes.dat','w')

	vlons = []
	vlats = []
	for line in lines[2:]:
		vals = line.split(',')
		try:
			vlat = float(vals[4])
			vlon = 360+float(vals[5])

			if ((regioncoords[0] < vlon < regioncoords[1]) and (regioncoords[2] < vlat < regioncoords[3])):
				vlons.append(vlon)
				vlats.append(vlat)

				#One time use:
				outfile.write('%g %g\n' %(vlon,vlat))
		except:
			continue
	outfile.close()

	return vlats,vlons

def getseismometerocations():

	client = fdsnClient('IRIS')

	starttime = '2013-01-01'
	endtime = str(datetime.datetime.today()).split(' ')[0]

	#region of interest: can change if desired
	regioncoords = [-171.0,-123.0,53.5,72.0]

	if os.path.isfile('Data/TAstations.dat'):
		print 'Found TA station data: No need to redownload'
	else:
		outfile = open('Data/TAstations.dat','w')

		print 'Getting seismometer locations - TA'

		inventoryTA = client.get_stations(network='TA',station='*',level='station',starttime=starttime,endtime=endtime,minlongitude=regioncoords[0],minlatitude=regioncoords[2],maxlongitude=regioncoords[1],maxlatitude=regioncoords[3])
		for entry in inventoryTA[0]:
			lon = float(360+entry.longitude)
			lat = float(entry.latitude)
			outfile.write('%g %g\n' %(lon,lat))
		outfile.close()

	if os.path.isfile('Data/AKstations.dat'):
		print 'Found AK station data: no need to redownload'

	else:
		outfile = open('Data/AKstations.dat','w')

		print 'Getting seismometer location - AK'

		inventoryAK = client.get_stations(network='AK',station='*',level='station',starttime=starttime,endtime=endtime,minlongitude=regioncoords[0],minlatitude=regioncoords[2],maxlongitude=regioncoords[1],maxlatitude=regioncoords[3])
		for entry in inventoryAK[0]:
			lon = float(360+entry.longitude)
			lat = float(entry.latitude)
			outfile.write('%g %g\n' %(lon,lat))
		outfile.close()

	#open the TA station file, extract the coordinates and plot the data
	infile = open('Data/TAstations.dat','r')
	lines = infile.readlines()
	infile.close()
	latsTA = []
	lonsTA = []
	for line in lines:
		vals= line.split(' ')
		lonsTA.append(float(vals[0]))
		latsTA.append(float(vals[1]))


	#open the AK station file, extract the coordinates and plot the data
	infile = open('Data/AKstations.dat','r')
	lines = infile.readlines()
	infile.close()
	latsAK = []
	lonsAK = []
	for line in lines:
		vals= line.split(' ')
		lonsAK.append(float(vals[0]))
		latsAK.append(float(vals[1]))

	return lonsTA,lonsAK,latsTA,latsAK



def get_quakes(coors,mindepth,maxdepth,minmag=3.0):
	'''Get earthquakes within a region around the start and end coordinates. These will be plotted on the section, with x distance'''

	client = fdsnClient('IRIS')

	evlons = []
	evlats = []

	if os.path.isfile('Data/quakedata.dat'):

		#The quake data file already exists

		infile = open('Data/quakedate.dat','r')

		lines = infile.readlines()
		infile.close()

		for line in lines:
			vals = line.split()
			evlons.append(float(vals[0]))
			evlats.append(float(vals[1]))

	else:

		#Need to download the event data anew

		quakefile = open('Data/quakedata.dat','w')

		minlon = min(coors[0],coors[1])
		maxlon = max(coors[0],coors[1])

		minlat = min(coors[2],coors[3])
		maxlat = max(coors[2],coors[3])

		starttime = '1970-01-01'
		endtime = str(datetime.datetime.today()).split(' ')[0]

		#Download an earthquake catalog
		quakecat = client.get_events(starttime=UTCDateTime(starttime), endtime=UTCDateTime(endtime), minlongitude=minlon, maxlongitude=maxlon, minlatitude=minlat, maxlatitude=maxlat, minmagnitude=minmag,mindepth=mindepth,maxdepth=maxdepth)

		for event in quakecat:

			evlon = event.origins[0].longitude
			evlat = event.origins[0].latitude
			evdep = event.origins[0].depth

			quakefile.write('%s %s %s\n' %(evlon,evlat,evdep))

			evlons.append(evlon)
			evlat.append(evlat)

		quakefile.close()

	return evlons, evlats
