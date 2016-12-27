#!/usr/bin/env python
#Tools for displaying .grd files 

#RMS Dec 2016

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure


def plotgrd(ingrd,quakes,startlat=None,startlon=None,endlat=None,endlon=None):

	'''Tool for python plotting of single tomo slice'''

	infile = Dataset(ingrd, model='r')

	depths = infile.variables['y'][:]
	lengths = infile.variables['x'][:]
	data = infile.variables['z'][:][:]

	infile.close()

	#Use image processing suite to find contours - lets say we want to highlight contours of
	#1.5% positive velocity contrast

	cval = 1.2
	contours = measure.find_contours(data,cval)

	xd = len(depths)
	xl = len(lengths)
	xscale = (lengths[-1]-lengths[0])/xl
	dscale = (depths[0]-depths[-1])/xd

	#Figure setup options 

	fig = plt.figure(facecolor='white',figsize=(10,6),frameon=True)
	axobj = fig

	ax = axobj.add_subplot(111)
	image = ax.imshow(data, interpolation='nearest',aspect='auto',cmap=plt.cm.seismic_r,extent=[lengths[0],lengths[-1],-depths[-1],-depths[0]])

	#plot contours, with scaling to take into account the extent
	for n, contour in enumerate(contours):
		if n == 0:
			ax.plot(xscale*contour[:, 1], dscale*contour[:, 0]+abs(min(depths)), 'r-', linewidth=2,label='contour at %g' %cval)
		else:
			ax.plot(xscale*contour[:, 1], dscale*contour[:, 0]+abs(min(depths)), 'r-', linewidth=2)

	image.set_extent([lengths[0],lengths[-1],-depths[-1],-depths[0]])

	#Obtain the earthquake information
	quakesfile = open(quakes,'r')
	lines = quakesfile.readlines()
	quakesfile.close()

	quakelens = []
	quakedeps = []

	for line in lines:
		vals = line.split()
		quakelens.append(vals[0])
		quakedeps.append(abs(float(vals[1])))

	ax.plot(quakelens,quakedeps,'k.')

	#plot text for start and end coordinates 

	ax.text(0, -20, 'Start: %g/%g' %(startlat,startlon), style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
	ax.text(lengths[-1]-50, -20, 'End: %g/%g' %(endlat,endlon), style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
	ax.text(lengths[-1]/2, -depths[0]-20, 'Contour at dv/v %g percent' %cval, style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})

	plt.gca().invert_yaxis()
	plt.xlabel('Distance along profile [km]')
	plt.ylabel('Depth [km]')
	plt.grid()

	#Set position of the colorbar
	cbar_ax = axobj.add_axes([0.88, 0.5, 0.03, 0.35])
	colors = image.set_clim(-4,4)
	axobj.colorbar(image,cbar_ax)

	plt.show()


def main():

	inslice = 'slice.grd'
	inquakes = 'Quakesdepth.gmt.dat'

	plotgrd(inslice,inquakes,1,2,4,3)




if __name__ == '__main__':

	main()