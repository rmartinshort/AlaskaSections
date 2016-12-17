#!/usr/bin/env python
#RMS Dec 2016
#Class for user interaction with Alaska section GUI
import os

class PointBrowser:

    def __init__(self, xs=None, ys=None):

        self.dragging = None
        self.line = None
        self.profiledraw = False

    def addobjs(self, canvasobj, mapobj):

      '''Attatch map objects so that we can draw on them/add text etc'''

      self.mapobj = mapobj
      self.canvasobj = canvasobj

    def addlabel(self,label):

      '''Add a gui label object so that is can be updated by user actions'''

      self.labelobj = label

    def adddataset(self,datasetpath):

      '''Add datset objects so that they can be plotted. This dataset must be within the Data directory'''

      self.datasetpath = datasetpath

    def motion(self,event):

      '''Define what happens when the user moves the mouse over the canvas'''

      lon = event.xdata
      lat = event.ydata

      if self.profiledraw == True:

        if self.dragging:

          #Update the section indicator label
          self.labelobj.set('Section: Start: %.2f/%.2f End: %.2f/%.2f' %(self.startlon,self.startlat,lon,lat))

          if self.line:
          	self.line[0].remove()
          	self.linepoints[0].remove()

          lats = [self.startlat,lat]
          lons = [self.startlon,lon]
          xevent,yevent = self.mapobj(lons,lats)

          self.line = self.mapobj.plot(xevent,yevent,'b-',linewidth=1,alpha=0.6)
          self.linepoints = self.mapobj.plot(xevent,yevent,'k.',linewidth=1,alpha=0.6)
          self.canvasobj.draw()

    def returnlocation(self):

      '''Return the start and end coordinates of the profile'''

      #This is where we need to call the profile plotting script

      if (self.profiledraw == True) or (self.line):

        print '------------------------------'
        print 'Start: %g/%g' %(self.startlat,self.startlon)
        print 'End: %g/%g' %(self.endlat,self.endlon)
        print '------------------------------'

        #User to confirm that a profile is to be made 
        userprof = str(raw_input('Continue to make profile? [Y/N]: '))

        if userprof == 'Y':

          print 'Generating profile'
          print self.datasetpath 
          os.system('extraction/SectionExtractor.sh %s 4 P %g %g %g %g 600 %g' %(self.datasetpath,self.startlat,self.endlat,self.startlon,self.endlon,4.0))

        else:

          print 'No profile to be generated'

      else:

        print 'Need to initiate profile drawing before a slice can be made!'

    def releasepick(self, event):

      '''Define what happens when the user releases the cursor'''

      lon = event.xdata
      lat = event.ydata

      if self.dragging:

      	self.endlat = lat
      	self.endlon = lon

        self.dragging = None

    def startdrawing(self):

      '''Set the drawing option to True, so the user can start drawing lines on the map'''

      self.profiledraw = True
      self.labelobj.set('Drawing!')


    def stopdrawing(self):

      '''Set the drawing option to False, so the user can stop drawing lines on the map'''

      self.profiledraw = False 
      self.labelobj.set('Not drawing')


    def onpick(self, event):

      '''Define what happens when the user presses the cursor'''

      # the click locations

      lon = event.xdata
      lat = event.ydata

      self.startlon = lon
      self.startlat = lat
      self.dragging = True

