#!/usr/bin/env python
#RMS Dec 2016
#GUI for making cross sections though Alaska tomography

print 'Importing modules ...'

from Tkinter import *
import tkFileDialog
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

        
        #The user must specify these dataset names - the map .grd file to be displayed in the GUI and the
        #tomography output text file that get sliced
		self.mapgrdfile = "VEL.SLICE.150.try.sim.kernel.P.b13.75.50.iasp.grd"
		self.dataset = "try.sim.kernel.P.b13.75.50.iasp"
		self.phasename = 'P'

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
		self.DisplaynetCDF('Data/%s' %self.mapgrdfile,'P vel anomaly at 150km [%]',[-3,3],plt.cm.RdBu)

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
		self.plottingseismometers = False
		#-----------------------------------------

		#Canvas setup
		self.canvas = FigureCanvasTkAgg(self.f, self)

		Browse.addobjs(self.canvas,self.map)
		self.f.canvas.mpl_connect('button_press_event',Browse.onpick)
		self.f.canvas.mpl_connect('motion_notify_event', Browse.motion)
		self.f.canvas.mpl_connect('button_release_event',Browse.releasepick)
		self.f.canvas.mpl_connect('key_press_event',Browse.multirelease)

		self.canvas.get_tk_widget().grid(row=1,sticky=W+S+N+E,columnspan=nocols,rowspan=norows)
		self.canvas.show()

		self.SetElements()

		parent.title("Alaska section mapper")

		#Add the chosen dataset to the browse object, so that it can be manipulated

		Browse.adddataset(self.dataset)

		#Generate the options menu

		self.Createmenubar(parent)

	def SetElements(self):

		'''Sets up the the GUI elements'''

		Label(self,text='Section Mapper',bg='azure',height=2,pady=2,font='Helvetica 22 bold').grid(row=0,column=0,rowspan=2,columnspan=14,sticky=W+E+S+N)


		# Add label that updates with the section coodinates
		self.sectioninfo = StringVar()
		Label(self,textvariable=self.sectioninfo,bg='white',height=2,padx=2,pady=2,font='Helvetica 10 bold').grid(row=0,column=12,columnspan=1,sticky=W+E+S+N)
		self.sectioninfo.set('Not drawing')
		Browse.addlabel(self.sectioninfo)

		# Add label that updates with the section type (GMT is default)
		self.sectiontype = StringVar()
		Label(self,textvariable=self.sectiontype,bg='white',height=1,padx=0,pady=0,font='Helvetica 10 bold').grid(row=1,column=12,columnspan=1,sticky=W+E+S+N)
		self.SetGMTSections()

		# Add dataset label
		self.datasetname = StringVar()
		self.phasestring = StringVar()
		Label(self,textvariable=self.datasetname,bg='white',height=1,padx=0,pady=0,font='Helvetica 10 bold').grid(row=0,column=2,columnspan=1,sticky=W+E+S+N)
		Label(self,textvariable=self.phasestring,bg='white',height=1,padx=0,pady=0,font='Helvetica 10 bold').grid(row=1,column=2,columnspan=1,sticky=W+E+S+N)
		self.Setdatasetname(self.dataset)

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

	def SetPythonSections(self):

		'''Set plotting options in python'''

		self.plottype = 'Python'
		self.sectiontype.set('Section type: Python')
		Browse.addslicetype(self.plottype,self.phasename)

	def SetGMTSections(self):

		'''Set plotting options in GMT'''

		self.plottype = 'GMT'
		self.segments = 'Single'
		self.sectiontype.set('Section type: GMT, %s' %self.segments)
		Browse.addslicetype(self.plottype,self.phasename)

	def SetSingleSections(self):

		'''Set plotting options to single sections'''

		self.segments = 'Single'
		self.sectiontype.set('Section type: %s, %s' %(self.plottype,self.segments))
		Browse.singlesection()

	def SetMultiSections(self):

		'''Set plotting options to multi sections'''

		self.segments = 'Multi'
		self.sectiontype.set('Section type: %s, %s' %(self.plottype,self.segments))
		Browse.multisection()

	def Setdatasetname(self,name):

		'''Set the name of the dataset that appears in the GUI'''

		try:
			nameparts = name.split('/')
			name = nameparts[-1]
		except:
			pass

		self.datasetname.set(name)

		phase = name.split('.')

		#Set the phase string and update the Browse class so that is knows 
		#what phase is being plotted

		self.phasename = phase[3]
		self.phasestring.set('Phase: %s' %self.phasename)
		Browse.addslicetype(self.plottype,self.phasename)


	def Askfordataset(self):

		'''Asks user for the name of a topography dataset to slice'''

		print '--------------------------'
		print 'Choose the 3D tomography file to extract slices from'
		print '--------------------------'

		filelocation = tkFileDialog.askopenfilename(initialdir='Data')
		
		self.olddataset = self.dataset
		self.dataset = filelocation.split('/')[-1]

		print '\n------------------------\n'

		print 'Now slicing dataset %s' %self.dataset
		Browse.adddataset(self.dataset)
		self.Setdatasetname(self.dataset)

		print '\n------------------------\n'

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

	def Plot_instruments(self):

		'''Options for getting and plotting seismometer locations'''

		#-------------------------------------------
		if self.plottingseismometers == False:

			lonsTA, lonsAK, latsTA, latsAK  = EDD.getseismometerocations()

			xstationsTA,ystationsTA = self.map(lonsTA,latsTA)
			xstationsAK,ystationsAK = self.map(lonsAK,latsAK)

			self.AKstations = self.map.plot(xstationsAK,ystationsAK,'b^',label='AK',markersize=2,alpha=0.5)
			self.TAstations = self.map.plot(xstationsTA,ystationsTA,'g^',label='TA',markersize=2,alpha=0.5)
			self.canvas.draw()

			self.plottingseismometers = True

		else:

			print 'Seismometers already plotted!'

	def Createmenubar(self,parent): 

		'''Create the drop down menu: allows user to add data layers to the Alaska'''

		menubar = Menu(self)
		parent.config(menu=menubar)
		filemenu = Menu(menubar,tearoff=0,font="Helvetica 16 bold") #insert a drop-down menu

		submenu1 = Menu(filemenu)
		submenu1.add_command(label='GMT sections',command=self.SetGMTSections)
		submenu1.add_command(label='Python sections',command=self.SetPythonSections)
		submenu1.add_command(label='Multi-segment sections',command=self.SetMultiSections)
		submenu1.add_command(label='Single-segment sections',command=self.SetSingleSections)
		filemenu.add_cascade(label='Section options',menu=submenu1,underline=0)

		filemenu.add_separator()

		submenu2 = Menu(filemenu)
		submenu2.add_command(label='Add instruments',command=self.Plot_instruments)
		submenu2.add_command(label='Choose tomography file',command=self.Askfordataset)
		filemenu.add_cascade(label='Overlay options',menu=submenu2,underline=0) #add the drop down menu to the menu bar

		menubar.add_cascade(label='Options',menu=filemenu)



if __name__ == '__main__':

	'''The GUI loop'''

	tk = Tk()
	viewer = SectionGUI(tk)
	tk.mainloop()


