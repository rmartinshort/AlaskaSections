#!/usr/bin/env python
#RMS Dec 2016
#GUI for making cross sections though Alaska tomography

print 'Importing modules ...'

from Tkinter import *
import numpy as np

#Allow matplotlib to be used within a tkinter canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm 
from netCDF4 import Dataset

from Browser import *
import Extract_Download_Data as EDD

#Set up a point browser instance
Browse = PointBrowser()

class SectionGUI(Frame):

	'''
	Base class for section mapper GUI
	'''

	def __init__(self,parent,width=1200,height=600,**options):

		#-----------------------------------

		#Set up the Tkinter GUI frame

		#-----------------------------------

		Frame.__init__(self,parent,**options)

		Grid.rowconfigure(self, 0, weight=1)
		Grid.columnconfigure(self, 0, weight=1)

		self.grid(sticky=E+W+N+S)
		self.userentries = {}

		top=self.winfo_toplevel()

		#Configure the width of rows and columns when tthe gui gets stretched. The second number provides the relative
		#weight of the column or row given by the first number

		norows = 14
		nocols = 14

		for i in range(norows):
			Grid.rowconfigure(self,i,weight=1)
			Grid.rowconfigure(parent,i,weight=1)
		for i in range(nocols):
			Grid.columnconfigure(self,i,weight=1)
			Grid.columnconfigure(parent,i,weight=1)

		#-----------------------------------

		#Set up the Alaska map 

		#-----------------------------------

		self.minlon = 189.0
		self.maxlon = 237.0
		self.minlat = 52.0
		self.maxlat = 73.0

		#create subplot where the map will go
		self.f = plt.figure(dpi=300,facecolor='white')

		#set the size of the figure for use with global map. Will need to choose this on the fly when
		#resizing the figure
		self.f.set_size_inches(5.0,2.2)
		self.a = self.f.add_subplot(111) #this self.a is the axis onwhich the basemap appears 

		#Initial map setup
		self.map = Basemap(ax=self.a,lat_0=62.5,lon_0=213,resolution ='l',llcrnrlon=self.minlon,llcrnrlat=self.minlat,urcrnrlon=self.maxlon,urcrnrlat=self.maxlat)

		#Display netCDF of some depth slice
		self.DisplaynetCDF('Data/VEL.SLICE.150.try.sim.kernel.P.b13.75.50.iasp.grd','P vel anomaly at 150km [%]',[-3,3],plt.cm.RdBu)

		#Basic setup - just fill the continents
		#self.map.fillcontinents()

		self.map.drawcoastlines(linewidth=0.4)

		#Set up lines of lat/lon 
		p1 = np.arange(50,75,2.0)
		m1 = np.arange(185,240,4.0)
		self.map.drawparallels(p1,labels=[True,True,False,False],linewidth=0.1,fontsize=5)
		self.map.drawmeridians(m1,labels=[False,False,False,True],linewidth=0.1,fontsize=5)

		#Plot volcanoes and seismometers
		#-----------------------------------------

		vlats,vlons = EDD.getvolcanolocations()
		xvolcanoes,yvolcanoes = self.map(vlons,vlats)
		self.volcanoes = self.map.plot(xvolcanoes,yvolcanoes,'r^',label='Volcanoes',markersize=4,alpha=0.4)

		#-----------------------------------------
		lonsTA, lonsAK, latsTA, latsAK  = EDD.getseismometerocations()

		xstationsTA,ystationsTA = self.map(lonsTA,latsTA)
		xstationsAK,ystationsAK = self.map(lonsAK,latsAK)

		self.AKstations = self.map.plot(xstationsAK,ystationsAK,'b^',label='AK',markersize=2,alpha=0.5)
		self.TAstations = self.map.plot(xstationsTA,ystationsTA,'g^',label='TA',markersize=2,alpha=0.5)

		#Canvas setup
		self.canvas = FigureCanvasTkAgg(self.f, self)

		Browse.addobjs(self.canvas,self.map)
		self.f.canvas.mpl_connect('button_press_event',Browse.onpick)
		self.f.canvas.mpl_connect('motion_notify_event', Browse.motion)
		self.f.canvas.mpl_connect('button_release_event',Browse.releasepick)

		self.canvas.get_tk_widget().grid(row=1,sticky=W+S+N+E,columnspan=nocols,rowspan=norows)
		self.canvas.show()

		self.SetElements()

		parent.title("Alaska section mapper")

	def SetElements(self):

		'''Sets up the the GUI elements'''

		Label(self,text='Section Mapper',bg='azure',height=2,pady=2,font='Helvetica 22 bold').grid(row=0,column=0,rowspan=2,columnspan=14,sticky=W+E+S+N)

		#Section creation buttons

		Button(self, text='Start drawing',pady=0,padx=2,command=self.Startdrawing).grid(row=13,columnspan=2,column=2,sticky=W+E)
		Button(self, text='Stop drawing',pady=0,padx=2,command=self.Stopdrawing).grid(row=13,columnspan=2,column=6,sticky=W+E)
		Button(self, text='Generate profile',pady=0,padx=2,command=self.GenerateProfile).grid(row=13,columnspan=2,column=10,sticky=W+E)

	def GenerateProfile(self):

		'''Return the start and end coordinates of the profile line'''

		Browse.returnlocation()

	def Startdrawing(self):

		'''Start drawing profiles'''

		Browse.startdrawing()

	def Stopdrawing(self):

		'''Start drawing profiles'''

		Browse.stopdrawing()

	def DisplaynetCDF(self,dataset,label,bounds,colormap):

		'''Generic function for displaying a netcdf dataset'''

		datasetname = dataset
		data = Dataset(datasetname)

		if 'lon' in data.variables:
			lons = data.variables['lon'][:]
			lats = data.variables['lat'][:]	
		else:
			lons = data.variables['x'][:]
			lats = data.variables['y'][:]				
		
		variable = data.variables['z'][:]

		#print min(variable)
		#print max(variable)

		#create interpolation grid

		dx = 0.5
		dy = 0.5
		nx = int((self.map.xmax-self.map.xmin)/dx)
		ny = int((self.map.ymax-self.map.ymin)/dy)

		#interpolate the nc data over the grid we've just made
		dat = self.map.transform_scalar(variable,lons,lats,nx,ny)

		#create image of the .nc dataset
		image = self.map.imshow(dat,cmap=colormap)
		image.set_clim(bounds[0],bounds[1])



if __name__ == '__main__':

	'''The GUI loop'''

	tk = Tk()
	viewer = SectionGUI(tk)
	tk.mainloop()


