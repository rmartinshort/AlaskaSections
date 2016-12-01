#!/usr/bin/env python
#RMS Dec 2016
#Class for user interaction with Alaska section GUI

class PointBrowser:

    def __init__(self, xs=None, ys=None):

        self.dragging = None
        self.line = None

    def addobjs(self, canvasobj, mapobj):

      self.mapobj = mapobj
      self.canvasobj = canvasobj

    def motion(self,event):

      '''Define what happens when the user moves the mouse over the canvas'''

      lon = event.xdata
      lat = event.ydata

      if self.dragging:

        print 'Dragging at %g %g' %(lon,lat)

        if self.line:
        	self.line[0].remove()
        	self.linepoints[0].remove()

        lats = [self.startlat,lat]
        lons = [self.startlon,lon]
        xevent,yevent = self.mapobj(lons,lats)

        self.line = self.mapobj.plot(xevent,yevent,'r-',linewidth=1,alpha=0.6)
        self.linepoints = self.mapobj.plot(xevent,yevent,'k.',linewidth=1,alpha=0.6)
        self.canvasobj.draw()

    def returnlocation(self):

    	'''Return the start and end coordinates of the profile'''

    	#This is where we need to call the profile plotting script

    	print 'Making profile!'

    def releasepick(self, event):

      '''define what happens when the user releases the cursor'''

      lon = event.xdata
      lat = event.ydata

      if self.dragging:

      	self.endlat = lat
      	self.endlon = lon

        self.dragging = None


    def onpick(self, event):

      '''define what happens when the user presses the cursor'''

      # the click locations

      lon = event.xdata
      lat = event.ydata

      self.startlon = lon
      self.startlat = lat
      self.dragging = True

