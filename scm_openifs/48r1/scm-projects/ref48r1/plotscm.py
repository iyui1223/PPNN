# (C) Copyright 2017- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#
#Author Ivan Bastak Duran , 9.11.2023

import sys, os, math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as cplt
import matplotlib.cm  as cm
import xarray as xr

import time

start = time.time()

#individual experiment folder names
# At present the exp_name is set to the default 
# EXPT_NAME in callscm _default timestep. 
# Needs changing for any other set-up
exp_names=[
           'ref-oifs-scm_450s'
           ]

#path to folder with experiments folders
path_base='scmout'

#Select which case name to analyse 
#casename='BOMEX'
#casename='TWPICE'
casename='DYCOMS'

##################################################
#setup of plots
##################################################
bottom_level=0 #lowest height of plot  - vc,dvc, and pr plots
top_level=3000 #highest height of plot - vc,dvc, and pr plots
time_start=0   #start of plot in time in hours - vc,dvc, and evol plots
time_end=24    #end of plot in time in hours - vc,dvc, and evol plots
itimes=[1,6,20]#profiles at these times in hours


paths=exp_names
nexps=len(exp_names)
for iexp in range(nexps):
    paths[iexp]=path_base+'_'+casename+'_'+exp_names[iexp]

ldata=True #read in data
lplot=True #make plots

#specify custom ranges via varbs_pr_min, varbs_pr_max, varbs_evol_min, varbs_evol_max, varbs_dvc_min, varbs_dvc_max, varbs_dvc_min, varbs_vc_max
l_custom_range=True
#l_custom_range=False

#plot height-time plots
lvc=True
#lvc=False

#plot height-time plots of differences
ldvc=False
#ldvc=True

#plot profile plots
lpr=True
#lpr=False

#plot evolution plots of surface variables
levol=True
#levol=False



#montage individual variable images in to one large image with imagemagick - valid for levol and lpr
lmontage=True
#lmontage=False

#remove individual variable images in to one large image with imagemagick - valid for levol and lpr
#lremove_imgs=True
lremove_imgs=False


#output directory
outdir="plots_"+casename
os.system('mkdir -p '+outdir)

#variables to be read
#3D variables to read
varbs=['time','u','v','q','t','pt','z','zh','V','temp','pres',\
       'cc','ths1','thl','ql'] #3D variables
#2D variables to read
varbs_2d=['sshf','slhf','10u','10v','2t','2d','tcc','lcc','mcc','hcc','top_swrad','top_lwrad','sfc_swrad','sfc_lwrad'] #2D variables


nvarbs=len(varbs)
nvarbs_2d=len(varbs_2d)
ntime=len(itimes)

##################################################
#setup of vertical profile plots#######################


varbs_pr=     [ 'q' ,'thl','u','v','cc'] #variables  to plot on pr
varbs_pr_min= [0.0025,  24,-10, -3,   0] #variables to plot min
varbs_pr_max= [0.02 ,   35, -5,  1,0.25] #variables to plot max
###x-axis labels
varbs_pr_unit= [r"q[$g\cdot g^{-1}$]",
                r"$\theta_l$[$\degree C$]",
                r"$u [m\cdot s^{-1}]$",
                r"$v [m\cdot s^{-1}]$",
                "Cloud cover"]
#end of setup of vertical profile plots################
##################################################

##################################################
#setup of time-height plots#######################

varbs_vc=     [ 'q' ,'thl','u','v','cc'] #variables  to plot on vc
varbs_vc_min= [0.0025,  24,-10, -3,   0] #variables to plot min
varbs_vc_max= [0.02 ,   35, -5,  1,0.25] #variables to plot max
varbs_vc_sym= [ 'a' ,  'l','l', 'l','a'] #variables to plot palletes - linear-l, not-linear symetric-s or asymetric-a color range
###x-axis labels
varbs_vc_unit= [r"q[$g\cdot g^{-1}$]",
                r"$\theta_l$[$\degree C$]",
                r"$u [m\cdot s^{-1}]$",
                r"$v [m\cdot s^{-1}]$",
                "Cloud cover"]
#color palletes for variables
varbs_vc_pal= ["viridis", 
               "coolwarm",
               "viridis" ,
               "viridis" ,
               "viridis",
               ]
#end of setup of time-height plots################
##################################################

##################################################
#setup of diff in time-height plots#######################
varbs_dvc=     [ 'q' , 'thl', 'u','v', 'cc'] #variables  to plot on vc
varbs_dvc_min= [-0.0025,  -2,  -1, -1,-0.25] #variables to plot min
varbs_dvc_max= [ 0.0025,   2,   1,  1, 0.25] #variables to plot max
varbs_dvc_sym= [   's' , 's', 's','s',  's'] #variables to plot palletes - linear-l, not-linear symetric-s or asymetric-a color range
###x-axis labels
varbs_dvc_unit= [r"q[$g\cdot g^{-1}$]",
                r"$\theta_l$[$\degree C$]",
                r"$u [m\cdot s^{-1}]$",
                r"$v [m\cdot s^{-1}]$",
                "Cloud cover"]
#color palleters for variables
varbs_dvc_pal= [
               "coolwarm",
               "coolwarm",
               "coolwarm",
               "coolwarm",
               "coolwarm",
               ]
#end of setup of time-height plots################
##################################################

##################################################
#setup of one-level evolution plots plots#######################
varbs_evol=['sshf','slhf','10u','10v','2t','2d','tcc','lcc','mcc','hcc','top_swrad','top_lwrad','sfc_swrad','sfc_lwrad']
varbs_evol_min= [-20,-140,-10,-5,295,290,-0.1,-0.1,-0.1,-0.1,0,-300,0,-45]
varbs_evol_max= [  0, -60, 0,  5,305,300,1.1,1.1,1.1,1.1,1250,-275,750,-15]
varbs_evol_unit= [r"sshf[$W\cdot m^{-2}$]" , r"slhf[$W\cdot m^{-2}$]",r"10u[$m\cdot s^{-1}$]",r"10v[$m\cdot s^{-1}$]",r"2t[$K$]",r"2d[$K$]",r"tcc",r"lcc",r"mcc",r"lcc",r"top_swrad[$W\cdot m^{-2}$]",r"top_lwrad[$W\cdot m^{-2}$]",r"sfc_swrad[$W\cdot m^{-2}$]",r"sfc_lwrad[$W\cdot m^{-2}$]"]

#end of setup of one-level evolution plots plots################
##################################################

###general plotting setup##
titles_size=18
label_size=16
legend_size=14
linewidth=2

azs=['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)','(i)','(j)','(k)','(l)','(m)','(n)','(o)','(p)','(q)','(r)','(s)','(t)','(u)','(v)','(w)','(x)','(y)','(z)','(aa)','(ab)','(ac)','(ad)','(ae)','(af)','(ag)','(ah)','(ai)']


#constants
T0=273.16
RG=9.81
kap = 0.4 #von Karman constant
Rd=287.06 #gas constant of dry air
Rv=461.53 #gas constant of water vapor
Rvd=Rv/Rd
Lv=2.501e+6 #latent heat of vaporization
Ls=2.8345E+6 #latent heat of freezing
cp=1004.7 #specific heat of dry air
RKAPPA=Rd/cp
p0=100000.0 #surface pressure
g=9.81 #gas
Lambda=5.87


if(ldata):
  #read the data
  print('reading data')
  exps = [ [] for _ in range(nexps+1) ]
  exps_2d = [ [] for _ in range(nexps+1) ]
  for iexp in range(0,nexps):
     print('exp: ',iexp,paths[iexp])
     ##reference
     dp=xr.open_dataset(paths[iexp]+'/progvar.nc',decode_times=False)
     dd=xr.open_dataset(paths[iexp]+'/diagvar.nc')
     dd2=xr.open_dataset(paths[iexp]+'/diagvar2.nc')
     #2D variables - can be extended
     var_2d = [ [] for _ in range(nvarbs_2d) ]
     for ivar in range(0,nvarbs_2d):
         #print('var: ',varbs_2d[ivar])
         if (varbs_2d[ivar]=='sshf'):
           var_2d[ivar] = dd['sfc_sen_flx'].values
         elif (varbs_2d[ivar]=='slhf'):
           var_2d[ivar] = dd['sfc_lat_flx'].values
         elif (varbs_2d[ivar]=='top_swrad'):
           var_2d[ivar] = dd['top_swrad'].values
         elif (varbs_2d[ivar]=='sfc_swrad'):
           var_2d[ivar] = dd['sfc_swrad'].values
         elif (varbs_2d[ivar]=='top_lwrad'):
           var_2d[ivar] = dd['top_lwrad'].values
         elif (varbs_2d[ivar]=='sfc_lwrad'):
           var_2d[ivar] = dd['sfc_lwrad'].values
         elif (varbs_2d[ivar]=='10u'):
           var_2d[ivar] = dd['u_wind_10m'].values
         elif (varbs_2d[ivar]=='10v'):
           var_2d[ivar] = dd['v_wind_10m'].values
         elif (varbs_2d[ivar]=='2t'):
           var_2d[ivar] = dd['temperature_2m'].values
         elif (varbs_2d[ivar]=='2d'):
           var_2d[ivar] = dd['dew_point_2m'].values
         elif (varbs_2d[ivar]=='tcc'):
           var_2d[ivar] = dd['total_cloud'].values
         elif (varbs_2d[ivar]=='lcc'):
           var_2d[ivar] = dd['low_cloud'].values
         elif (varbs_2d[ivar]=='mcc'):
           var_2d[ivar] = dd['middle_cloud'].values
         elif (varbs_2d[ivar]=='hcc'):
           var_2d[ivar] = dd['high_cloud'].values
         elif (varbs_2d[ivar]=='hpbl'):
           var_2d[ivar] = dd['pbl_height'].values
     dvar_2d=dict(zip(varbs_2d, var_2d))
     exps_2d[iexp]=dvar_2d
     #3D variables  - can be extended
     var = [ [] for _ in range(nvarbs) ]
     for ivar in range(0,nvarbs):
         if (varbs[ivar]=='z'):
           var[ivar] = dp['height_f'].values
         elif (varbs[ivar]=='zh'):
           var[ivar] = dp['height_h'].values
         elif (varbs[ivar]=='time'):
           var[ivar] = (dp['time'].values/(3600))
         elif (varbs[ivar]=='V'):
           u = dp['u'].values
           v = dp['v'].values
           var[ivar] =np.sqrt(u**2+v**2)
         elif (varbs[ivar]=='u'):
           var[ivar] = dp['u'].values
         elif (varbs[ivar]=='v'):
           var[ivar] = dp['v'].values
         elif (varbs[ivar]=='cc'):
           var[ivar] = dp['cloud_fraction'].values
         elif (varbs[ivar]=='ths1'):
           t = dp['t'].values
           p = dp['pressure_f'].values
           pt =t*(p0/p)**RKAPPA
           q = dp['q'].values
           ql = dp['ql'].values
           qi = dp['qi'].values
           ptl=pt*(1.0-(Lv*ql+Ls*qi)/(cp*t))
           var[ivar]=ptl*np.exp(Lambda*(q+ql+qi))
         elif (varbs[ivar]=='thl'):
           t = dp['t'].values
           p = dp['pressure_f'].values
           pt =t*(p0/p)**RKAPPA
           q = dp['q'].values
           ql = dp['ql'].values
           qi = dp['qi'].values
           ptl=pt*(1.0-(Lv*ql+Ls*qi)/(cp*t))-T0
           var[ivar]=ptl
         elif (varbs[ivar]=='pt'):
           t = dp['t'].values
           p = dp['pressure_f'].values
           var[ivar] =t*(p0/p)**RKAPPA
         elif (varbs[ivar]=='q'):
           var[ivar] = dp['q'].values
         elif (varbs[ivar]=='ql'):
           var[ivar] = dp['ql'].values
         elif (varbs[ivar]=='pres'):
           var[ivar] = dp['pressure_f'].values
         elif (varbs[ivar]=='temp'):
           var[ivar] = dp['t'].values
     dvar=dict(zip(varbs, var))
     exps[iexp]=dvar
     dp.close()
     dd.close()
     dd2.close()

##################################################
##additional functions

#rolling average
def roll_average(var,roll_dt):
     return var[0:var.shape[0]].rolling(t=roll_dt,center=True).mean().values

#wind speed from components and wind direction
def uv2ws(u,v):
     wspd = np.sqrt(u**2+v**2)
     wdir = (np.arctan2(u,v)*180/np.pi)%360
     return wspd, wdir

#adjust colormap
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    '''
    https://stackoverflow.com/a/18926541
    '''
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

#creare asymetric non-linear colormap
def get_asym_nonlin_clevels_ticks(vmin,vmax):
    number=vmax-vmin
    unit=10**math.floor(math.log(number/50., 10))
    if (number/50./unit>=2.5):
      unit=5*unit
    imin=np.round(number/unit/5,-1)
    imid=np.round(number/unit/4*3,-1)
    imax=np.round(number/unit,-1)
    clevels=np.hstack([np.arange(vmin,vmin+imin*unit,unit/2),np.arange(vmin+imin*unit,vmin+imid*unit,unit*5/2),np.arange(vmin+imid*unit,vmin+imax*unit,unit*10/2)])
    ticks=np.round(np.hstack([np.arange(vmin,vmin+imin*unit,unit),np.arange(vmin+imin*unit,vmin+imid*unit,unit*5),np.arange(vmin+imid*unit,vmin+imax*unit,unit*10)]),-math.floor(math.log(number/50., 10))+1)
    #clevels=np.hstack([np.arange(vmin,vmin+imin*unit,unit/2),np.arange(vmin+imin*unit,vmin+imid*unit,unit*5/2),np.arange(vmin+imid*unit,vmin+imax*unit,unit*10/2),[imax*unit]])
    #ticks=np.round(np.hstack([np.arange(vmin,vmin+imin*unit,unit),np.arange(vmin+imin*unit,vmin+imid*unit,unit*5),np.arange(vmin+imid*unit,vmin+imax*unit,unit*10),[imax*unit]]),-math.floor(math.log(number/50., 10))+1)
    return clevels,ticks

def get_lin_clevels_ticks(vmin,vmax):
    number=vmax-vmin
    unit=10**math.floor(math.log(number/50., 10))
    if (number/50./unit>=2.5):
      unit=5*unit
    clevels=np.arange(vmin,vmax+unit,unit)
    ticks=np.arange(vmin,vmax+unit*10,unit*10)
    return clevels,ticks

#creare symetric non-linear colormap
def get_sym_nonlin_clevels_ticks(vmin,vmax):
    number=max(np.abs(vmax),np.abs(vmin))
    unit=10**math.floor(math.log(number/25., 10))
    if (number/25./unit>=2.5):
      unit=5*unit
    imin=np.round(number/unit/10,0)
    imid=np.round(number/unit/2,-1)
    imax=np.round(number/unit,-1)
    clevelsr=np.hstack([np.arange(0,imin*unit,unit/2),np.arange((imin+1)*unit,imid*unit,unit*2),np.arange((imid+1)*unit,imax*unit,unit*10/2),[imax*unit]])
    clevels=np.hstack([[-(imax+1)*unit],-clevelsr[:0:-1],clevelsr])

    ticksr=np.hstack([np.arange(0,imin*unit,unit),np.arange((imin+1)*unit,imid*unit,unit*4),np.arange((imid+1)*unit,imax*unit,unit*10),[imax*unit]])

    ticks=np.round(np.hstack([-ticksr[:0:-1],ticksr]),-math.floor(math.log(number/25., 10))+1)

    return clevels,ticks
#end of additional functions
##################################################


if(lplot):
 nz=dp.nlev.size
 print('plotting',casename)
 #plot profiles
 if(lpr):
  nvarbs_pr=len(varbs_pr)
  for itime in range(0,ntime):
    for ivar in range(0,nvarbs_pr):
     fig, axs = plt.subplots(nrows = 1, ncols=1, figsize=(10,8))
     fig.subplots_adjust(hspace=0.5,wspace=0.4)
     string=varbs_pr[ivar]+" t="+f'{itimes[itime]:04d} h'
     axs.set_title(string,fontsize=titles_size, fontweight='bold')
     axs.set_ylim([bottom_level,top_level])
     for iexp in range(0,nexps):
      tim = exps[iexp]['time'][:]
      dtime=np.abs(itimes[itime]-tim)
      itime_scm=np.where(dtime.min()==np.abs(dtime))[0][0]
      zz = exps[iexp]['z'][itime_scm,:]
      axs.plot(exps[iexp][varbs_pr[ivar]][itime_scm,:],zz,label=exp_names[iexp],lw=2)
     if(l_custom_range):
      axs.set_xlim([varbs_pr_min[ivar],varbs_pr_max[ivar]])
     axs.legend()
     plt.savefig(outdir+'/pr_'+varbs_pr[ivar]+'-t'+f'{itimes[itime]:04d}'+\
            '.png',bbox_inches='tight')
     plt.close()
    #montage individual images
    if(lmontage):
     string="montage "+outdir+'/pr_*-t'+f'{itimes[itime]:04d}'+\
            '.png -geometry +1+1 '+outdir+'/prall-t'+f'{itimes[itime]:04d}'+\
            '.png'
     os.system(string)
    #remove individual images
    if(lremove_imgs):
     string="rm "+outdir+'/pr_*-t'+f'{itimes[itime]:04d}'+\
            '.png'
     os.system(string)

 #plot time evolution - 2D variables
 if(levol):
  nvarbs_evol=len(varbs_evol)
  evolstring='evol'
  for ivar in range(0,nvarbs_evol):
     fig, axs = plt.subplots(nrows = 1, ncols=1, figsize=(10,8))
     fig.subplots_adjust(hspace=0.5,wspace=0.4)
     string=varbs_evol[ivar]+' evol'
     axs.set_title(string,fontsize=titles_size, fontweight='bold')


     #plot evolution
     for iexp in range(0,nexps):
      tim = exps[iexp]['time'][:]
      itime_st=np.where((np.abs(time_start-tim)).min()==np.abs(time_start-tim))[0][0]
      itime_end=np.where((np.abs(time_end-tim)).min()==np.abs(time_end-tim))[0][0]
      tim = tim[itime_st:itime_end]
      axs.plot(tim,exps_2d[iexp][varbs_evol[ivar]][itime_st:itime_end],label=exp_names[iexp],lw=2)

     if(l_custom_range):
      axs.set_ylim([varbs_evol_min[ivar],varbs_evol_max[ivar]])
     axs.set_xlabel('Time [h]', fontsize = label_size) 
     axs.set_ylabel(varbs_evol_unit[ivar], fontsize = label_size) 
     axs.tick_params(axis='both', labelsize=legend_size )
     axs.legend()

     plt.savefig(outdir+'/'+varbs_evol[ivar]+'-'+str(evolstring)+'.png',bbox_inches='tight')
     plt.close()
  #montage individual images
  if(lmontage):
   string="montage "+outdir+'/*-'+str(evolstring)+\
            '.png -geometry +1+1 '+outdir+'/evall'+\
            '.png'
   os.system(string)
  if(lremove_imgs):
   #remove individual images
   string="rm "+outdir+'/*-'+str(evolstring)+\
             '.png'
   os.system(string)

 #time - height plot
 if(lvc):
  nvarbs_vc=len(varbs_vc)
  vcstring='vc'
  #define the cross section
  for ivar in range(0,nvarbs_vc):
     fig, axs = plt.subplots(nrows = nexps, ncols=1, figsize=(10,5*(nexps)+3))
     if(nexps==1):
         axs=[axs]
     fig.subplots_adjust(hspace=0.5,wspace=0.4)

     #plotting ranges
     if(l_custom_range):
      if(varbs_vc_sym[ivar]=='s'):
       clevels,ticks=get_sym_nonlin_clevels_ticks(varbs_vc_min[ivar],varbs_vc_max[ivar])
       cmap = plt.cm.get_cmap(varbs_vc_pal[ivar])
      elif(varbs_vc_sym[ivar]=='a'):
       clevels,ticks=get_asym_nonlin_clevels_ticks(varbs_vc_min[ivar],varbs_vc_max[ivar])
       cmap = truncate_colormap(plt.cm.get_cmap(varbs_vc_pal[ivar]).reversed(), 0, 0.9)
      elif(varbs_vc_sym[ivar]=='l'):
       clevels,ticks=get_lin_clevels_ticks(varbs_vc_min[ivar],varbs_vc_max[ivar])
       cmap = plt.cm.get_cmap(varbs_vc_pal[ivar])
      norm=cplt.BoundaryNorm(boundaries=clevels, ncolors=cmap.N)
     else:
      if(varbs_vc_sym[ivar]=='s'):
       cmap = plt.cm.get_cmap(varbs_vc_pal[ivar])
      elif(varbs_vc_sym[ivar]=='a'):
       cmap = truncate_colormap(plt.cm.get_cmap(varbs_vc_pal[ivar]).reversed(), 0, 0.9)
      elif(varbs_vc_sym[ivar]=='l'):
       cmap = plt.cm.get_cmap(varbs_vc_pal[ivar])

     #plot experiments
     for iexp in range(0,nexps):
      tim = exps[iexp]['time'][:]
      itime_st=np.where((np.abs(time_start-tim)).min()==np.abs(time_start-tim))[0][0]
      itime_end=np.where((np.abs(time_end-tim)).min()==np.abs(time_end-tim))[0][0]
      tim = tim[itime_st:itime_end]
      zz = exps[iexp]['z'][itime_st,:]
      var = exps[iexp][varbs_vc[ivar]][itime_st:itime_end,:]
      if(iexp==0):
       itop=np.where(np.abs(zz-top_level)==np.abs(zz-top_level).min())[0][0]-1
       ibot=np.where(np.abs(zz-bottom_level)==np.abs(zz-bottom_level).min())[0][0]
      nz=zz.size
      nt=tim.size

      #contour of variable
      if(l_custom_range):
       cs0 = axs[iexp].contour(tim, zz, var.T,levels=ticks[1::5],colors='0.7' ) 
      else:
       if(iexp==0):
        cs0 = axs[iexp].contour(tim, zz[itop:ibot],var[:,itop:ibot].T,colors='0.7') 
       else:
        cs0 = axs[iexp].contour(tim, zz[itop:ibot],var[:,itop:ibot].T,colors='0.7',levels=cs0.levels) 
      #inline labels
      #axs[iexp].clabel(cs, ticks[1::10],  # label every 10th level
      #     inline=1,fmt='%1.1f',  fontsize=14)
      #filled contour of variable

      if(l_custom_range):
       cs = axs[iexp].contourf(tim, zz, var.T, levels=clevels, cmap = cmap,norm=norm,extend='both') 
      else:
       if(iexp==0):
        cs = axs[iexp].contourf(tim, zz[itop:ibot], var[:,itop:ibot].T, cmap=cmap,extend='both') 
       else:
        cs = axs[iexp].contourf(tim, zz[itop:ibot], var[:,itop:ibot].T, cmap = cmap, levels=cs.levels,extend='both') 

      axs[iexp].set_ylim([bottom_level,top_level])
      axs[iexp].set_xlabel('Time [h]', fontsize = label_size) 
      axs[iexp].set_ylabel(r'Height [$\mathrm{m}$]', fontsize = label_size) 
      #axs[iexp].set_xticks(xticks)
      #axs[iexp].set_xticklabels(xlabss)
      axs[iexp].tick_params(axis='both', labelsize=legend_size )
      string=exp_names[iexp]
      axs[iexp].set_title(string,fontsize=titles_size, fontweight='bold')
      #axs[iexp].set_title(string,fontsize=titles_size, fontweight='bold',loc='right')

     #color bar
     if(l_custom_range):
      mapp=cm.ScalarMappable(norm=norm, cmap=cmap)
      mapp.set_array([])
      if(nexps==1):
       cbar=fig.colorbar( mappable=mapp, cax=None, ax= axs[0],use_gridspec=True, ticks=ticks,orientation='horizontal',pad=0.11,format='%.1e',extend='max',aspect=50)
      else:
       cbar=fig.colorbar( mappable=mapp, cax=None, ax= axs.ravel().tolist(),use_gridspec=True, ticks=ticks,orientation='horizontal',pad=0.11,format='%.1e',extend='max',aspect=50)
      cbar.ax.set_xticklabels(ticks, rotation='vertical')
     else:
      if(nexps==1):
       cbar=fig.colorbar(mappable=cs, cax=None, ax= axs[0],use_gridspec=True, orientation='horizontal',pad=0.11,format='%.1e',extend='max',aspect=50)
      else:
       cbar=fig.colorbar(mappable=cs, cax=None, ax= axs.ravel().tolist(),use_gridspec=True, orientation='horizontal',pad=0.11,format='%.1e',extend='max',aspect=50)
     cbar.set_label(label=varbs_vc_unit[ivar], size=label_size)
     plt.savefig(outdir+'/'+varbs_vc[ivar]+'-'+str(vcstring)+'.png',bbox_inches='tight')
     plt.close()


 #diff in time - height plot
 if(ldvc):
  nvarbs_dvc=len(varbs_dvc)
  #define the cross section
  vcstring='dvc'
  for ivar in range(0,nvarbs_dvc):
     fig, axs = plt.subplots(nrows = nexps, ncols=1, figsize=(10,5*nexps+3))
     if(nexps==1):
         axs=[axs]
     fig.subplots_adjust(hspace=0.5,wspace=0.4)
     for iexp in range(0,nexps):
      tim = exps[iexp]['time'][:]
      itime_st=np.where((np.abs(time_start-tim)).min()==np.abs(time_start-tim))[0][0]
      itime_end=np.where((np.abs(time_end-tim)).min()==np.abs(time_end-tim))[0][0]
      tim=tim[itime_st:itime_end]
      zz = exps[iexp]['z'][itime_st,:]
      var = exps[iexp][varbs_dvc[ivar]][itime_st:itime_end,:]-exps[0][varbs_dvc[ivar]][itime_st:itime_end,:]
      if(iexp<=1):
       itop=np.where((zz-top_level)==np.abs(zz-top_level).min())[0][0]
       ibot=np.where((zz-bottom_level)==np.abs(zz-bottom_level).min())[0][0]
      nz=zz.size
      nt=tim.size
      if(l_custom_range):
       if(varbs_dvc_sym[ivar]=='s'):
        clevels,ticks=get_sym_nonlin_clevels_ticks(varbs_dvc_min[ivar],varbs_dvc_max[ivar])
        cmap = plt.cm.get_cmap(varbs_dvc_pal[ivar])
       elif(varbs_dvc_sym[ivar]=='s'):
        clevels,ticks=get_asym_nonlin_clevels_ticks(varbs_dvc_min[ivar],varbs_dvc_max[ivar])
        cmap = truncate_colormap(plt.cm.get_cmap(varbs_dvc_pal[ivar]).reversed(), 0, 0.9)
       elif(varbs_dvc_sym[ivar]=='l'):
        clevels,ticks=get_lin_clevels_ticks(varbs_dvc_min[ivar],varbs_dvc_max[ivar])
        cmap = plt.cm.get_cmap(varbs_dvc_pal[ivar])
       norm=cplt.BoundaryNorm(boundaries=clevels, ncolors=cmap.N)
      else:
       if(varbs_dvc_sym[ivar]=='s'):
        cmap = plt.cm.get_cmap(varbs_dvc_pal[ivar])
       elif(varbs_dvc_sym[ivar]=='s'):
        cmap = truncate_colormap(plt.cm.get_cmap(varbs_dvc_pal[ivar]).reversed(), 0, 0.9)
       elif(varbs_dvc_sym[ivar]=='l'):
        cmap = plt.cm.get_cmap(varbs_dvc_pal[ivar])

      #contour of variable
      if(l_custom_range):
       cs = axs[iexp].contour(tim, zz, var.T,levels=ticks[1::5],colors='0.7' ) 
      else:
       if(iexp<=0):
        cs2 = axs[iexp].contour(tim, zz[itop:ibot], var[:,itop:ibot].T,colors='0.7' ) 
       else:
        cs2 = axs[iexp].contour(tim, zz[itop:ibot], var[:,itop:ibot].T,levels=cs2.levels,colors='0.7' ) 
      #inline labels
      #axs[iexp].clabel(cs, ticks[1::10],  # label every 10th level
      #     inline=1,fmt='%1.1f',  fontsize=14)
      #filled contour of variable
      if(l_custom_range):
       cs = axs[iexp].contourf(tim, zz, var.T, levels=clevels, cmap = cmap,norm=norm,extend='both') 
      else:
       if(iexp<=1):
        cs3 = axs[iexp].contourf(tim, zz[itop:ibot], var[:,itop:ibot].T,cmap = cmap,extend='both') 
       else:
        cs3 = axs[iexp].contourf(tim, zz[itop:ibot], var[:,itop:ibot].T,cmap = cmap,levels=cs3.levels,extend='both') 

      axs[iexp].set_ylim([bottom_level,top_level])
      axs[iexp].set_xlabel('Time [h]', fontsize = label_size) 
      axs[iexp].set_ylabel(r'Height [$\mathrm{m}$]', fontsize = label_size) 
      #axs[iexp].set_xticks(xticks)
      #axs[iexp].set_xticklabels(xlabss)
      axs[iexp].tick_params(axis='both', labelsize=legend_size )
      string=exp_names[iexp]
      axs[iexp].set_title(string,fontsize=titles_size, fontweight='bold')
      #axs[iexp].set_title(string,fontsize=titles_size, fontweight='bold',loc='right')

     if(l_custom_range):
      mapp=cm.ScalarMappable(norm=norm, cmap=cmap)
      mapp.set_array([])
      if(nexps==1):
       cbar=fig.colorbar( mappable=mapp, cax=None, ax= axs[0],use_gridspec=True, ticks=ticks,orientation='horizontal',pad=0.11,format='%.1e',extend='both',aspect=50)
      else:
       cbar=fig.colorbar( mappable=mapp, cax=None, ax= axs.ravel().tolist(),use_gridspec=True, ticks=ticks,orientation='horizontal',pad=0.11,format='%.1e',extend='both',aspect=50)
      cbar.ax.set_xticklabels(ticks, rotation='vertical')
     else:
      mapp=cm.ScalarMappable( cmap=cmap)
      mapp.set_array([])
      if(nexps==1):
       cbar=fig.colorbar( mappable=cs3, cax=None, ax= axs[0],use_gridspec=True, orientation='horizontal',pad=0.11,format='%.1e',extend='both',aspect=50)
      else:
       cbar=fig.colorbar( mappable=cs3, cax=None, ax= axs.ravel().tolist(),use_gridspec=True, orientation='horizontal',pad=0.11,format='%.1e',extend='both',aspect=50)
     
     cbar.set_label(label=varbs_dvc_unit[ivar], size=label_size)
     plt.savefig(outdir+'/'+varbs_dvc[ivar]+'-'+str(vcstring)+'.png',bbox_inches='tight')
     plt.close()
   

end = time.time()
#print(end - start)
