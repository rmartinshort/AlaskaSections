module transforms 

	use radial_models

	implicit none 

contains

	!----------------------------------------------------------

	subroutine transform(trans,lon,lat,lonp,latp,x,y,z,id)

		implicit none

		double precision :: lon,lat,lonp,latp,x,y,z,lontmp,lattmp,xp,yp,zp,r
		integer :: id
		double precision, parameter :: pi=3.14159265d0,rad=180.d0/pi
		double precision :: trans(3,3)

		!Forward transform from earth coordinates to (lonp,latp) [not actually sure what these are, to be honest]

		if(id.eq.1) then

			lontmp=lon/rad
			lattmp=lat/rad

			x=cos(lattmp)*cos(lontmp)
			y=cos(lattmp)*sin(lontmp)
			z=sin(lattmp)

			xp=trans(1,1)*x+trans(1,2)*y+trans(1,3)*z
			yp=trans(2,1)*x+trans(2,2)*y+trans(2,3)*z
			zp=trans(3,1)*x+trans(3,2)*y+trans(3,3)*z

			r=sqrt(xp*xp+yp*yp+zp*zp)

			latp=asin(zp/r)*rad
			lonp=atan2(yp,xp)*rad

			if(lonp.gt.180.d0) then
				lonp=lonp-360.d0
			end if 

			x=xp/r
			y=yp/r
			z=zp/r

		!Inverse transform from (lonp,latp) to earth coordinates

		else if(id.eq.-1) then

			lontmp=lonp/rad
			lattmp=latp/rad

			xp=cos(lattmp)*cos(lontmp)
			yp=cos(lattmp)*sin(lontmp)
			zp=sin(lattmp)

			x=trans(1,1)*xp+trans(2,1)*yp+trans(3,1)*zp
			y=trans(1,2)*xp+trans(2,2)*yp+trans(3,2)*zp
			z=trans(1,3)*xp+trans(2,3)*yp+trans(3,3)*zp

			r=sqrt(x*x+y*y+z*z)

			lat=asin(z/r)*rad
			lon=atan2(y,x)*rad

			if(lon.lt.0.d0) then
				lon=lon+360.d0
			end if

			x=x/r
			y=y/r
			z=z/r

		else
			stop 'Incorrect parameter entered in subroutine coodinatetransform'
		end if

		return

	end subroutine transform


	!----------------------------------------------------------

	subroutine exists(fname)

		! Check if a file exists

		implicit none

		logical :: ioerr
		character (len=130) :: fname

		print *, 'Checking for file ', fname

		inquire(file=fname,exist=ioerr)
		if (ioerr) then 
			print *, 'File exists'
		else
			stop "Required file does not exist!"
		end if

	end subroutine exists


	!----------------------------------------------------------


	subroutine meshread(lx,ly,lz,nface,nvolu,nx,ny,nz,dx,dy,dz,x0,y0,z0,trans)

		! Read information from the mesh.config file

		implicit none

		double precision :: trans(3,3)
		integer :: lx,ly,lz,nface,nvolu,nx,ny,nz
		double precision :: dx,dy,dz,x0,y0,z0

		integer :: i,j

		character(len=130) :: meshname

		meshname = 'mesh.config'

		call exists(meshname)

		open(1, file=meshname)
		read(1,*)lx,ly,lz,nx,ny,nz
		read(1,*)x0,y0,z0,dx,dy,dz
		read(1,*)((trans(i,j),j=1,3),i=1,3)
		close(1)

		nface = nx*ny
		nvolu = nface*nz

		return

	end subroutine meshread


	!----------------------------------------------------------


	subroutine findr(rsurf,ivin,r,ir)

		implicit none

		double precision :: r,rsurf
		integer :: i,ivin,ir

		!For flat and linear gradient model

		if (ivin.le.0.and.ivin.ge.-2) then
			if (r.le.rdis(1)) then
		 		ir=1
			else if (r.gt.rdis(1).and.r.le.rdis(2)) then
		 		ir=2
			else if (r.gt.rdis(2).and.r.le.rdis(11)) then
		 		ir=3
			else
		 		ir=4
			end if

		!PREM or 11 homogeneous layered models or IASP91

		else if (ivin.eq.1.or.ivin.le.-3) then

			if (r.le.rdis(1)) then !rdis is a vector that comes from the radial_models file
				ir=1
				return
			end if

			if (r.gt.rdis(11)) then
				ir=12
				return
			end if
		
			do i=2,11
				if (r.gt.rdis(i-1).and.r.le.rdis(i)) then
					ir=i
					return
				end if
			end do

		else if (ivin.eq.2) then

		!for ak135 continent model
			if (r.le.rdis(1)) then
				ir=1
				return
			end if

			if (r.gt.rsurf) then
				ir=10
				return
			end if

			do i=2,9
				if (r.gt.rdis(i-1).and.r.le.rdis(i)) then
					ir=i
					return
				end if
			end do

		else if (ivin.eq.3) then

		!for ak135 spherical average model

			if (r.le.rdis(1)) then
				ir=1
				return
			end if
		
			if (r.gt.rsurf) then
				ir=13
			return
		end if

		do i=2,12
			if (r.gt.rdis(i-1).and.r.le.rdis(i)) then
				ir=i
				return
			end if
		end do

	end if
	return

	end subroutine findr


	!----------------------------------------------------------

	subroutine velo1(rn,rsurf,ivin,iw,ir,r,c,dc,d2c)

      	implicit none

		double precision :: r,c,dc,d2c,rn,rsurf
		integer :: iw,ir,iw0,ivin

		iw0=iw

		if (ivin.eq.-3) then

			stop 'Not yet coded'

! 			if (ir.eq.2) iw=1
! 			call vlyrs1(iw,ir,r,c,dc,d2c)

		else if (ivin.eq.-2) then

			stop 'Not yet coded'

! 			if (ir.eq.2) iw=1
! 			dc=0.0d0
! 			d2c=0.0d0

! 			if (r.gt.rsurf) ir=3
! 			c=hc(ir,iw)

		else if (ivin.eq.-1) then

			stop 'Not yet coded'

! 			if (ir.eq.2) iw=1
! 			call vflat1(iw,ir,r,c,dc,d2c)

		else if (ivin.eq.0) then

			stop 'Not yet coded'

! 			if (ir.eq.2) iw=1
! 			call vgrad1(iw,ir,r,c,dc,d2c)

		else if (ivin.eq.1) then

			stop 'Not yet coded'

            !prem model
! 			if (ir.eq.2) iw=1
! 			call vprem1(iw,ir,r,c,dc,d2c)

		else if (ivin.eq.-4) then

            !iasp model
			if (ir.eq.2) iw=1

			!print *, 'Call to viasp1!'
			!print *, 'iw, ir, r, c, dc, d2c'
			call viasp1(rn,rsurf,iw,ir,r,c,dc,d2c)
			!print *, '=>', iw,ir,r,c,dc,d2c 

		else if (ivin.eq.2) then

			stop 'Not yet coded'

		    !ak135 model
! 			if (ir.eq.2) iw=1
! 			call vak1351(iw,ir,r,c,dc,d2c)

		else if (ivin.eq.3) then

			stop 'Not yet coded'

			if (ir.eq.2.or.ir.eq.11) iw=1
! 			call vak1351(iw,ir,r,c,dc,d2c)

		endif

		iw=iw0

		return

 	end subroutine velo1


 	subroutine viasp1(rn,rsurf,iw,ir,r,c,dc,d2c)

		implicit none

 		double precision :: r,d2c,dc,c,rn2,x,rn,rsurf
 		integer :: ir,iw

 		rn2=rn*rn

 		if ((ir.gt.11).and.(r.ge.rsurf)) then

 			c=apc(1,11,iw)+apc(2,11,iw)+apc(3,11,iw)+apc(4,11,iw)
 			dc=rn*(apc(2,11,iw)+2.0d0*apc(3,11,iw)+3.0d0*apc(4,11,iw))
 			d2c=rn2*(2.0d0*apc(3,11,iw)+6.0d0*apc(4,11,iw))

 		else
 			
 			x=r*rn
 			c=apc(1,ir,iw)+x*(apc(2,ir,iw)+x*(apc(3,ir,iw)+x*apc(4,ir,iw)))
 			dc=rn*(apc(2,ir,iw)+x*(2.0d0*apc(3,ir,iw)+x*3.0d0*apc(4,ir,iw)))
 			d2c=rn2*(2.0d0*apc(3,ir,iw)+x*6.0d0*apc(4,ir,iw))
 		endif

 		return

 	end subroutine viasp1 


end module transforms