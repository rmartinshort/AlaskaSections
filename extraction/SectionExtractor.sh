#!/bin/bash

#RMS Dec 2016
GMT=gmt4

if [ -z "$1" ]; then 
   echo "No arguments supplied"
   echo "call SectoionExtractor.sh smodid (sim.kernel.P.b.1.0.1.0.iasp) dvmax (eg 4) P|S lat1 lat2 lon1 lon2 maxdepth"
   echo "It will create a netCDF file corresponding to the specified slice. This can then be plotted in GMT or Python"
   exit 1
fi 

#Change to directory where the data files are present
cd Data

if [ ! -f mesh.config ]; then
   echo "mesh configuration file not found mesh.config needs to be in this directory"
   pwd
   cd ../
   exit 1
fi

## VARIABLES
modid=$1
cmax=$2	## set min/max for color scale
velPS=$3
lat1=$4
lat2=$5
lon1=$6
lon2=$7
maxdepth=$8
quakemag=$9

#Set to 1 for slowness, 0 for velocity
velslow=1


## Check the type of section we want to plot
if [ $lat1 == $lat2 ]; then
  TYPE="CSTLAT"
  preplot=../extraction/bin/extract_plot_lonlat_slice.exe
elif [ $lon1 == $lon2 ]; then
  TYPE="CSTLON"
  preplot=../extraction/bin/extract_plot_lonlat_slice.exe
else 
  TYPE="OBLIQUE"
  preplot=../extraction/bin/extract_plot_2point_slice.exe
  #preplot=$GroupTomo/bin/extract_plot_2point_slice.old.exe
fi

#####################################################################
#Get earthquake information
#####################################################################

if [ $quakemag == "N" ]; then
  echo "Do not include quakes"
  Iquakes="N"
else
  Iquakes="Y"
  echo "INCUDE QUAKES!: MAY TAKE SOME TIME TO GET THEM"
  $GroupTomo/WRAPPER_SCRIPTS/Quake_Fetch_Tools.gmt4.py $lon1 $lat1 $lon2 $lat2 $quakemag
fi 

#####################################################################
#check parameters
#####################################################################

echo "------------------------------------------"
echo "Plotting slice through model" $modid
echo "Slice type:"
echo $TYPE
echo "------------------------------------------"

#Make lon1 and lon2 positive if they are not already
lon1b=`echo $lon1 | awk '{ if ($1 < 0) print(360+$1) ; else print($1)}'`
lon2b=`echo $lon2 | awk '{ if ($1 < 0) print(360+$1) ; else print($1)}'`
lon1=$lon1b
lon2=$lon2b

## Velocity file for data extraction 
velfile=$1

if [ ! -f $velfile ]; then
   echo "Data file to extract from not found!"
   pwd
   cd ../
   exit 1
fi

## WAVE TYPE (P OR S)
if [ $velPS == "P" ]; then
  echo 'P detected!'
	veltype=1
elif [ $velPS == "S" ]; then
  echo 'S detected!'
	veltype=2
else
	echo "ERROR: plt.lat: veltype not P or S!"
	exit 1
fi

## EXTRACT BACKGROUND MODEL
## background model -4: IASP91; 2: AK135-Continent; 3: AK135-spherical avg
#Default is iasp
mdl="iasp"
if [ $mdl == "iasp" ]; then
	bgmod=-4
elif [ $mdl == "ak1c" ]; then
	bgmod=2
else
	echo "ERROR: plt.lat: unrecognized bg mod"
	exit 1 
fi 

## EXTRACT SLICE FROM THE MODEL
if [ -f slow.slice ]; then
rm slow.slice
fi
if [ -f slow.grd ]; then
rm slow.grd
fi


#####################################################################
#RUN FORTRAN PROGAM TO EXTRACT SLICE
#####################################################################

$preplot << END
$bgmod
$veltype
$velfile
$velslow
$lat1
$lat2
$lon1
$lon2
$maxdepth
END

#mv vel.slice slow.slice

## MAKE VELOCITY CPT FILE (extract from an RGB table)

CPT=tomovels.cpt
#path to the rgb table we want to use
datapath="$GroupTomo/DATA/plotting/svel.rgb13"

../extraction/bin/svcpt13_table_cont.exe << END
-$cmax $cmax
$datapath
END

mv svel13.cpt $CPT
#Test - use this different color file for Alaska maps 
CPT=$GroupTomo/DATA/plotting/vel_AK.cpt


#####################################################################
#Make .grd file
#####################################################################

Jdegkm="-Jx0.45/0.0045" #For the lon/lat section models

#Note: for preplot scripts that plot distance, use this projection for all models 
Jkmkm="-Jx0.017/0.017" #For the oblique slice models

#Decide which of the three plotting options we have, and run GMT commands to make the .grd file

if [ $TYPE == 'CSTLAT' ]; then 
  J=$Jkmkm
  frame=-BWSa200f50:Distance_[km]:/a200f50:Depth_[km]:
  Rslice=`awk '{print($5,-$3)}' slow.slice | $GMT minmax -I2`
  awk '{print($5,-$3,$4)}' slow.slice | $GMT surface -Gslice.grd $Rslice -I2/2 -T0.1 -V

elif [ $TYPE == 'CSTLON' ]; then
  J=$Jkmkm
  frame=-BWSa200f50:Distance_[km]:/a200f50:Depth_[km]:
  Rslice=`awk '{print($5,-$3)}' slow.slice | $GMT minmax -I2`
  awk '{print($5,-$3,$4)}' slow.slice | $GMT surface -Gslice.grd $Rslice -I2/2 -T0.1 -V

elif [ $TYPE == 'OBLIQUE' ]; then
  J=$Jkmkm
  frame=-BWSa200f50:Distance_[km]:/a200f50:Depth_[km]:
  Rslice=`awk '{print($5,-$3)}' slow.slice | $GMT minmax -I2`
  awk '{print($5,-$3,$4)}' slow.slice | $GMT surface -Gslice.grd $Rslice -I2 -V -T0.1

fi 

#####################################################################
#Do the plotting - this could be moved to another script but at the moment its probably
#unnecessary
#####################################################################

## PS FILE
PS=latlon.$lat1.$lat2.$lon1.$lon2.$velfile.ps

#Give the model a name
MODNAME=Alaska

$GMT pstext << END -X2 -Y10 -R0/8.5/0/11 -Jx1 -K  > $PS
0.75 7.5 16 0 1 LM ${MODNAME} 2016 - $velPS 
0.75 6.5 12 0 0 LM lat1: $lat1 lat2: $lat2 lon1: $lon1 lon2: $lon2
0.75 5.9 12 0 LM $velfile
END

echo $Rslice

$GMT grdimage slice.grd $J $Rslice -C$CPT -O -K -X1.0 -Y-6.0 -V >> $PS
$GMT psbasemap $frame $J $Rslice -O -K -V >> $PS

if [ $Iquakes == "Y" ]; then
   $GMT psxy Quakesdepth.gmt.dat -Sc0.05 -Gblack -Wthinnest $J $Rslice -O -K >> $PS
   $GMT psxy Slabmodel.gmt.dat -Wthin,red $J $Rslice -O -K >> $PS
fi 

echo $veltype

if [ $veltype == 1 ]; then
  $GMT psscale -Y-2 -D1.5/-0.5/4.5/0.5h -E -Ba1/:"P-velocity anomaly [%]": -C$CPT -O -V -K >> $PS

elif [ $veltype == 2 ]; then
  $GMT psscale -Y-2 -D1.5/-0.5/4.5/0.5h -E -Ba1/:"S-velocity anomaly [%]": -C$CPT -O -V -K >> $PS

fi

## INSET MAP THAT GIVES THE POSITION OF THE SLICE
#These are the values that will need to be edited when we move to a new region 
Jinset="-JB-147/62.5/52/73/3.5i"
Rinset="-R-171/-123/52/73"

$GMT pscoast $Rinset $Jinset -Di -X17.0 -Y10 -Ba10f5WSen -O -K -V -Wthinnest >> $PS

#Stations
sfile=station_correction.$modid
$GMT psxy $sfile -: -Sc0.03 -Gred -Wthinnest,red $Rinset $Jinset -O -K >> $PS

#Plot the actual section line on the map, rather than just a great circle path linking the start and end points. This latter approach looks bad at
#high latitudes
pointsfile=tmppoints.xyp
$GMT project -C$lon1/$lat1 -E$lon2/$lat2 -G20 -Q > $pointsfile
$GMT psxy $pointsfile $Jinset $Rinset -W5,red -O >> $PS
open $PS

mv slow.slice ../extraction/plots/slow.slice.$lat1.$lat2.$lon1.$lon2
mv slice.grd ../extraction/plots/slice.$lat1.$lat2.$lon1.$lon2.grd
cd ../
