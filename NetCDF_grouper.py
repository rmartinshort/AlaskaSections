#!/usr/bin/env python
#RMS Jan 2017
#Tool for merging multiple netCDF files into one, ready for plotting

import glob
import sys 
from netCDF4 import Dataset
import numpy as np


def groupfiles(infiles):

	''' Generates a single .grd file by combining a series of .grd files in the order given by
	the list infiles'''

	print '----------------------------------------'
	print 'Generating grouped .grd files'
	print '----------------------------------------'

	lens = []
	datasets = []
	iternum = 0

	for grdfile in infiles:

		infile = Dataset(grdfile, model='r')

		#build up a master list of the lengths
		lengths = infile.variables['x'][:]

		for val in lengths:
			lens.append(val)


		#The depths vector should be the same for all netCDF files, so we only need to extract it once

		if iternum == 0:
			depths = infile.variables['y'][:]


		#Get data and append it to the appropriate list
		data = infile.variables['z'][:][:]

		infile.close()

		datasets.append(data)

		iternum += 1

	#Generate new netCDF in the data directory
	outfilename = 'Data/groupedslice.grd'

	groupedgrd = Dataset(outfilename,"w",format='NETCDF4')

	#Make X and Y dimensions 
	lendim = groupedgrd.createDimension("X",len(lens))
	depthdim = groupedgrd.createDimension("Y",len(depths))

	#Make the variables
	grdlengths = groupedgrd.createVariable("x","f4",("X",))
	grddepths = groupedgrd.createVariable("y","f4",("Y",))
	grddata = groupedgrd.createVariable("z","f4",("Y","X"))

	#Add all the data 
	grdlengths[:] = np.array(lens)
	grddepths[:] = depths


	D = np.zeros([len(depths),len(lens)])

	l = 0

	for element in datasets:
		(ydim,xdim) = np.shape(element)
		D[0:ydim,l:(xdim+l)] = element
		l += xdim

	grddata[:,:] = D

	groupedgrd.close()

	return outfilename



if __name__ == '__main__':

	infiles = sorted(glob.glob('Data/slice*.grd'))
	groupfiles(infiles)

