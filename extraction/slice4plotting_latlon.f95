!RMS June 2016

!Extract a cross sectional slice through a tomographic model, ready for plotting with GMT
!Rewrite of an f77 version to use dynamic memory allocation

!This code takes user input of two points and will plot a slice through the model that lies between them. The two options are for a constant latitude slice or a constant longitude slice

program slicelatlon

	use transforms
	use radial_models

	implicit none

	character (len=130) :: ia
	integer :: idepth, ilon, ilon1, ilon2, ir, ilat1,ilat2,ilat,maxdepth
	integer :: ii,jj,kk,inode,nxy,ivelin,ips,i,svindicator

	double precision :: xrat, yrat, zrat, c1 ,c2 ,v1, v2 ,v3 ,v4 ,v5, v6 ,v7, v8
	double precision :: i1,i2,j1,j2,w1,w2,vel
	double precision :: lat0,lon0,lat1,lon1

	double precision, dimension(:), allocatable :: slow

	double precision :: trans(3,3)

	double precision :: x0,y0,z0,dx,dy,dz,dc,d2c,x,y,z,xlon,ylat,zrad

	double precision :: slat,slon,sdepth,srad

	double precision :: pi, twopi, rpd, dpr, Rearth, rsurf, rn, rcmb, r660, r670, r400, alpha, beta, r0

	double precision :: dkm,slat1,slat2,slon1,slon2

	integer :: lx, ly, lz, nx, ny, nz, nvolu, nface

	print *, 'Enter backgound velocity flag'
	print *, '-3: Constant velocity'
	print *, '-2: Homogenous layered model'
	print *, '-1: Flattening model'
	print *, '0: Compute PREM at T=ivelin'
	print *, '-4: Compute IASP91 [suggested]'
	print *, '2: AK135-Continent model'
	print *, '3: AK135-spherical average model'

	read *, ivelin

	print *,'P [enter 1] or S [enter 2]?'

	read *, ips

	pi = asin(1.0)*2.0
	twopi = pi*2.0
	rpd = pi/180.0
	dpr = 180.0/pi

	Rearth = 6371.0
	rsurf = Rearth
	rn = 1.0/rsurf
	r0 = rsurf

	if (ivelin.eq.-4) then
		rcmb = 3482.0
	else if (ivelin.ge.2) then
		rcmb = 3479.5
	else
		rcmb = 3480.0
	end if

	r660 = 5711.0
	r670 = 5701.0
	r400 = 5971.0

	!read the variable sizes from the mesh file
	call meshread(lx,ly,lz,nface,nvolu,nx,ny,nz,dx,dy,dz,x0,y0,z0,trans)

	print *, 'Velocity file to be displayed'
	read *, ia

	!This tells us whether we are extrcting slowness or velocity

	print *, 'Velocity (0) or slowness (1)'
	read *, svindicator

	call exists(ia)

	open(1,file=ia)

	! Fill the slowness vector from file input
	allocate(slow(nvolu))

	read(1,*)(slow(i),i=1,nvolu)
	close(1)

	! Create a file corresponding to that slowness slice

	if (svindicator.eq.1) then
		open(1,file='slow.slice')

	elseif (svindicator.eq.0) then
		open(1,file='vel.slice')

	else
		stop "svindicator must be either 0 or 1"
	end if

	print *, 'There are', nz, 'layers in this model'

	print *, 'Enter lat1 for slice:'
	read *, slat1

	print *, 'Enter lat2 for slice:'
	read *, slat2

	print *, 'Enter lon1 for slice'
	read *, slon1

	print *, 'Enter lon2 for slice'
	read *, slon2

	print *, 'Enter max depth for slice'
	read *, maxdepth

	if (slat1.gt.slat2) then
		slat=slat1
		slat1=slat2
		slat2=slat
	endif

	if (slon1.gt.slon2) then
		slon=slon1
		slon1=slon2
		slon2=slon
	endif

	! Case where we're making a slice of constant latitude

	if (slat1.eq.slat2) then

		slat=slat1
		ilon1=int(slon1*20)
		ilon2=int(slon2*20)
		print *, ' '
		print *, "Constant slice at latitude : ",slat
		print *, "Between longitudes",ilon1/20.0,ilon2/20.0
		print *, ' '

		!ilon1/10 is the first point, ilon2/10 is the last

		do ilon=ilon1,ilon2,1

			slon=dble(ilon)/20.0

			if (ilon.eq.ilon1) then
				dkm = 0.0
			else

			!Determine the distance along the profile using standard Haversine formula
			dkm = 2*r0*dasin(sqrt((dsin((slat*(pi/180)-slat*(pi/180))/2)**2 + dcos(slat*(pi/180))*&
			dcos(slat1*(pi/180))*dsin((slon*(pi/180)-(ilon1/20)*(pi/180))/2)**2)))

			endif

			do idepth=0,maxdepth,1
				sdepth=dble(idepth)

				if (slon.lt.0.0) slon=360.0+slon

				call transform(trans,slon,slat,lon0,lat0,x,y,z,1)

				srad=Rearth-sdepth

				kk=int((srad-z0)/dz)+1

				zrad=z0+dble(kk-1)*dz

				ii=int((lon0-x0)/dx)+1

				xlon=x0+dble(ii-1)*dx

				jj=int((lat0-y0)/dy)+1

				ylat=y0+dble(jj-1)*dy

				xrat=(lon0-xlon)/dx
				yrat=(lat0-ylat)/dy
				zrat=(srad-zrad)/dz

				nxy=nx*ny

				inode=((kk-1)*nxy)+((jj-1)*nx)+ii

				zrad=z0+dble(kk-1)*dz

				call findr(rsurf,ivelin,zrad,ir)
				call velo1(rn,rsurf,ivelin,ips,ir,zrad,c1,dc,d2c)

				zrad=z0+(dble(kk-1)*dz)+dz

				call findr(rsurf,ivelin,zrad,ir)
				call velo1(rn,rsurf,ivelin,ips,ir,zrad,c2,dc,d2c)

				v1=-1.0*slow(inode)*c1*100.0
				v2=-1.0*slow(inode+1)*c1*100.0
				v3=-1.0*slow(inode+nx)*c1*100.0
				v4=-1.0*slow(inode+nx+1)*c1*100.0
				v5=-1.0*slow(inode+nxy)*c2*100.0
				v6=-1.0*slow(inode+nxy+1)*c2*100.0
				v7=-1.0*slow(inode+nxy+nx)*c2*100.0
				v8=-1.0*slow(inode+nxy+nx+1)*c2*100.0


				i1=v1*(1.0-zrat)+v5*zrat
				i2=v3*(1.0-zrat)+v7*zrat
				j1=v2*(1.0-zrat)+v6*zrat
				j2=v4*(1.0-zrat)+v8*zrat

				w1=i1*(1.0-yrat)+i2*yrat
				w2=j1*(1.0-yrat)+j2*yrat

				vel=w1*(1.0-xrat)+w2*xrat

				if (slon.gt.180.0) slon=slon-360.0

				write(1,'(3f10.4,e12.4,x,f10.4)')slat,slon,sdepth,vel,dkm
			enddo
		enddo

	! Case where we're making a slice of constant longitude

	elseif (slon1.eq.slon2) then

		slon=slon1
		ilat1=int(slat1*20)
		ilat2=int(slat2*20)

		print *, ' '
		print *, "Constant slice at longitude : ",slon
		print *, "Between latitudes",ilat1/20.0,ilat2/20.0
		print *, ' '

		do ilat=ilat1,ilat2,1

			slat=dble(ilat)/20.0

			if (ilat.eq.ilat1) then
				dkm = 0.0
			else
				dkm = 2*r0*dasin(sqrt((dsin((slat1*(pi/180)-slat*(pi/180))/2)**2 + &
				dcos(slat*(pi/180))*dcos(slat1*(pi/180))*dsin((slon*(pi/180)-slon*(pi/180))/2)**2)))
				print *, "Distance along profile: ", dkm
			endif

			do idepth=0,maxdepth,1

				sdepth=dble(idepth)

				if (slon.lt.0.0) then
					slon=360.0+slon
				endif

				call transform(trans,slon,slat,lon0,lat0,x,y,z,1)

				srad=6371.0-sdepth

				kk=int((srad-z0)/dz)+1
				zrad=z0+dble(kk-1)*dz
				ii=int((lon0-x0)/dx)+1
				xlon=x0+dble(ii-1)*dx
				jj=int((lat0-y0)/dy)+1
				ylat=y0+dble(jj-1)*dy

				xrat=(lon0-xlon)/dx
				yrat=(lat0-ylat)/dy
				zrat=(srad-zrad)/dz

				nxy=nx*ny
				inode=((kk-1)*nxy)+((jj-1)*nx)+ii
				zrad=z0+dble(kk-1)*dz

				call findr(rsurf,ivelin,zrad,ir)
				call velo1(rn,rsurf,ivelin,ips,ir,zrad,c1,dc,d2c)

				zrad=z0+(dble(kk-1)*dz)+dz

				call findr(rsurf,ivelin,zrad,ir)
				call velo1(rn,rsurf,ivelin,ips,ir,zrad,c2,dc,d2c)

				v1=-1.0*slow(inode)*c1*100.0
				v2=-1.0*slow(inode+1)*c1*100.0
				v3=-1.0*slow(inode+nx)*c1*100.0
				v4=-1.0*slow(inode+nx+1)*c1*100.0
				v5=-1.0*slow(inode+nxy)*c2*100.0
				v6=-1.0*slow(inode+nxy+1)*c2*100.0
				v7=-1.0*slow(inode+nxy+nx)*c2*100.0
				v8=-1.0*slow(inode+nxy+nx+1)*c2*100.0

				i1=v1*(1.0-zrat)+v5*zrat
				i2=v3*(1.0-zrat)+v7*zrat
				j1=v2*(1.0-zrat)+v6*zrat
				j2=v4*(1.0-zrat)+v8*zrat

				w1=i1*(1.0-yrat)+i2*yrat
				w2=j1*(1.0-yrat)+j2*yrat

				vel=w1*(1.0-xrat)+w2*xrat

				write(1,'(3f10.4,e12.4,x,f10.4)')slat,slon,sdepth,vel,dkm
			enddo
		enddo

	end if

	deallocate(slow)

end program slicelatlon
