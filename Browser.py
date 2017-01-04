#!/usr/bin/env python
#RMS Dec 2016
#Class for user interaction with Alaska section GUI
import os
import sys
import NetCDF_plotter as ncp

class PointBrowser:

    def __init__(self, xs=None, ys=None):

        self.dragging = None
        self.multilist = []
        self.multi = None
        self.line = None
        self.profiledraw = False
        self.singlesectionflag = True
        self.multisectionflag = False

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
      
    def addslicetype(self,slicetype,phasename):
        
      '''Add the slice type - python plotting or GMT plotting of the .grd file thy gets made by the slicing
        tool '''
        
      self.slicetype = slicetype
      self.phasename = phasename

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


        if self.multi:

          print '------------------------------'
          print 'Multiple segment plotting'
          print '------------------------------'

        else:

          print '------------------------------'
          print 'Start: %g/%g' %(self.startlat,self.startlon)
          print 'End: %g/%g' %(self.endlat,self.endlon)
          print '------------------------------'

        #User to confirm that a profile is to be made 
        userprof = str(raw_input('Continue to make profile? [Y/N]: '))

        if userprof == 'Y':

          print 'Generating profile'
          print self.datasetpath

          if self.multi:

            #Create a series of .grd files for merging and then plotting

            i = 1

            for element in self.multilist:

              print element

              print 'Section: %g/%g to %g/%g' %(element[0],element[1],element[2],element[3])

              os.system('extraction/ExtractionOnly.sh %s 4 P %g %g %g %g 600 N' %(self.datasetpath,element[0],element[2],element[1],element[3]))

              os.system('mv Data/slice.grd Data/slice_%02d.grd' %i)

              print '\n-------------------------------------\n'
              print 'Generated slice "slice_%02d.grd"' %i
              print '\n-------------------------------------\n'

              i += 1

            print 'Resetting the multilist'
            self.multilist = []


          else:
          
              if self.slicetype == "GMT":

                 #GMT slicing tool
                 os.system('extraction/SectionExtractor.sh %s 4 P %g %g %g %g 600 %g' %(self.datasetpath,self.startlat,self.endlat,self.startlon,self.endlon,4.0))

              elif self.slicetype ==  "Python":

                #print self.startlat, self.startlon, self.endlat, self.endlon

                os.system('extraction/ExtractionOnly.sh %s 4 P %g %g %g %g 600 %g' %(self.datasetpath,self.startlat,self.endlat,self.startlon,self.endlon,4.0))

                #We are now in the 'Data' directory, so can immediately go ahead and plot the python slice
                f1, f2 = ncp.plotgrd('Data/slice.grd','Data/Quakesdepth.gmt.dat',self.startlat,self.startlon,self.endlat,self.endlon)

                cwd = os.getcwd()
                print cwd

                #Return to the directory above 'Data'
                #os.chdir('../')

                #Move the images to the correct folder
                os.system('mv %s %s images' %(f1,f2))

                #Open the files for viewing
                os.system('open images/%s images/%s' %(f1,f2))

              else:
                  print 'Do not understand input slicetype'
                  sys.exit(1)

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

        if self.multi:

          self.endlat = lat
          self.endlon = lon

          lats = [self.startlat,lat]
          lons = [self.startlon,lon]
          xevent,yevent = self.mapobj(lons,lats)

          #Draw lines that do not get removed - for a multiple section cross section 

          self.prevline = self.mapobj.plot(xevent,yevent,'b-',linewidth=1,alpha=0.6)
          self.prevlinepoints = self.mapobj.plot(xevent,yevent,'k.',linewidth=1,alpha=0.6)
          self.previous_lines.append(self.prevline)
          self.previous_points.append(self.prevlinepoints)
          self.canvasobj.draw()

          #Add a list of the start and end coordinates to a list that records the section line

          self.multilist.append([self.startlat,self.startlon,self.endlat,self.endlon])
          self.startlat = self.endlat
          self.startlon = self.endlon

    def multirelease(self,event):

      '''Define what happends when user presses a key - aim to stop the multi section drawing process'''

      print 'You pressed %s' %event.key
      print 'Must press enter to remove lines drawn with multi-section tool selected'

      if event.key == 'enter':

        if self.prevline:

          try:

            for element in zip(self.previous_lines,self.previous_points):

              element[0][0].remove()
              element[1][0].remove()

            #Remake the lines/points lists

            self.previous_lines = []
            self.previous_points = []
            self.multilist = []

          except:

            print 'Something wrong with removing lines!'

          self.canvasobj.draw()

    def multisection(self):

      '''Signal that the drawing option is of type multi'''

      self.multisectionflag = True
      self.singlesectionflag = False
      self.previous_lines = []
      self.previous_points = []

    def singlesection(self):

      '''Signal that the drawing option is of type multi'''

      self.singlesectionflag = True
      self.multisectionflag = False 


    def startdrawing(self):

      '''Set the drawing option to True, so the user can start drawing lines on the map'''

      self.profiledraw = True
      self.labelobj.set('Drawing!')


    def stopdrawing(self):

      '''Set the drawing option to False, so the user can stop drawing lines on the map'''

      self.profiledraw = False 
      self.labelobj.set('Not drawing')

      #Remove any existing lines

      self.line[0].remove()
      self.linepoints[0].remove()
      self.line = None
      self.canvasobj.draw()


    def onpick(self, event):

      '''Define what happens when the user presses the cursor'''

      # the click locations

      lon = event.xdata
      lat = event.ydata

      self.startlon = lon
      self.startlat = lat

      if self.singlesectionflag == True:
        self.dragging = True
        self.multi = None
      elif self.multisectionflag == True:
        self.dragging = True
        self.multi = True

