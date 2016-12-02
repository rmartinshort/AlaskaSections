## makefile 
## RMS DEC 2016

#Compiler option should be gfortran
GFOR = gfortran
GFLAGS = -ffixed-line-length-none -ffree-line-length-none -fdollar-ok

BIN = bin

all:
	
	#New plotting script(s) - written in f95 with dynamic memory allocation
	$(GFOR) $(GFLAGS) radial_models.f95 transforms.f95 slice4plotting_latlon.f95 -o $(BIN)/extract_plot_lonlat_slice.exe
	$(GFOR) $(GFLAGS) radial_models.f95 transforms.f95 slice4plotting.f95 -o $(BIN)/extract_plot_2point_slice.exe
	$(GFOR) $(GFLAGS) radial_models.f95 transforms.f95 svcpt13_table_cont.f95 -o $(BIN)/svcpt13_table_cont.exe

clean:
	rm -f *.o
	rm $(BIN)/*.exe
	






