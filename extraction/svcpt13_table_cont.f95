program svcpt13_table_cont

	!RMS rewrite of svcpt13_table_cont.f, for f95. This is just practice with fortran, really

	use transforms

	implicit none

	integer, dimension(:), allocatable :: ir, ig, ib

	double precision :: x,y,xx,yy,dc,y1,y2

	integer :: i,j,nc,ir0,ib0,ig0

	character(len=300) :: datafilepath

	! User inputs

	print *, 'Input the color range xmin to xmax'
	read *, x, y

	print *, 'Enter path to color base file'
	read(*,'(a)') datafilepath

	call exists(datafilepath)

	open(1,file=datafilepath)

	!The outpue files, used in GMT
	open(2,file='svel13.cpt')

	read(1,*)nc

	allocate(ig(nc))
	allocate(ib(nc))
	allocate(ir(nc))

	if (x.ge.y) then

		do i=0,nc-1
			read(1,*)ir(nc-i),ig(nc-i),ib(nc-i)
		end do

		xx=y
		y=x
		x=xx

	else
		do i=1,nc
			read(1,*)ir(i),ig(i),ib(i)
		end do

	end if

	dc=(y-x)/(nc-1)

	do i=1,nc-1

		if (i.eq.1) then
			ir0=ir(i)
			ig0=ig(i)
			ib0=ib(i)
		end if

		y1=x+(i-1)*dc
		y2=y1+dc
		write(2,99)y1,ir(i),ig(i),ib(i),y2,ir(i+1),ig(i+1),ib(i+1)
	end do

	write(2,199)ir0,ig0,ib0
	write(2,299)ir(nc),ig(nc),ib(nc)
	write(2,399)255,255,255

	deallocate(ir)
	deallocate(ig)
	deallocate(ib)

99      format(f10.4,3i8,f10.4,3i8)
199     format('B',8x,3i8)
299     format('F',8x,3i8)
399     format('N',8x,3i8)

end program svcpt13_table_cont

