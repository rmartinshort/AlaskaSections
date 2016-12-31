#!/usr/bin/env python
#Tools for displaying .grd files 

#RMS Dec 2016

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure
import os


#For mapping
from mpl_toolkits.basemap import Basemap, cm


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

	figax = axobj.add_subplot(111)
	image = figax.imshow(data, interpolation='nearest',aspect='auto',cmap=plt.cm.seismic_r,extent=[lengths[0],lengths[-1],-depths[-1],-depths[0]])

	#plot contours, with scaling to take into account the extent
	for n, contour in enumerate(contours):
		if n == 0:
			figax.plot(xscale*contour[:, 1], dscale*contour[:, 0]+abs(min(depths)), 'r-', linewidth=2,label='contour at %g' %cval)
		else:
			figax.plot(xscale*contour[:, 1], dscale*contour[:, 0]+abs(min(depths)), 'r-', linewidth=2)

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

	figax.plot(quakelens,quakedeps,'k.')

	#plot text for start and end coordinates 

	figax.text(0, -20, 'Start: %g/%g' %(startlat,startlon), style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
	figax.text(lengths[-1]-50, -20, 'End: %g/%g' %(endlat,endlon), style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
	figax.text(lengths[-1]/2, -depths[0]-20, 'Contour at dv/v %g percent' %cval, style='italic',bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})

	plt.gca().invert_yaxis()
	plt.xlabel('Distance along profile [km]')
	plt.ylabel('Depth [km]')
	plt.grid()

	#Set position of the colorbar
	cbar_ax = axobj.add_axes([0.88, 0.5, 0.03, 0.35])
	colors = image.set_clim(-4,4)
	axobj.colorbar(image,cbar_ax)

	sectioname = 'Tomo_section_%.2f_%.2f_%.2f_%.2f.png' %(startlat,startlon,endlat,endlon)

	fig.savefig(sectioname,dpi=200)


	#Simple map with the section coordinates plotted on 
	print 'Plotting section line on a map'

	fig1 = plt.figure(facecolor='white',figsize=(10,6),frameon=True)
	m = Basemap(width=2000000,height=1800000,resolution='l',projection='aea',lat_1=54.0,lat_2=69.0,lon_0=-146,lat_0=61)
	m.shadedrelief()

	p1 = np.arange(-90.,91.,5.)
	m1 = np.arange(-180.,181.,10.)

	m.drawparallels(p1,labels=[False,True,False,False])
	m.drawmeridians(m1,labels=[False,False,False,True])

	x,y = m([startlon,endlon],[startlat,endlat])
	m.plot(x,y,'r-')

	mapname = 'Section_line_%.2f_%.2f_%.2f_%.2f.png' %(startlat,startlon,endlat,endlon)

	fig1.savefig(mapname,dpi=150)

	return sectioname,mapname





def main():

	inslice = 'slice.grd'
	inquakes = 'Quakesdepth.gmt.dat'

	plotgrd(inslice,inquakes,1,2,4,3)


if __name__ == '__main__':

	main()