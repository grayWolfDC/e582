#!/usr/bin/env python

from __future__ import division
import argparse
import h5py
import glob
from matplotlib import pyplot as plt
import site
site.addsitedir('../utilities')
from reproject import reproj_numba
import planck
import os,errno
#
# compat module redefines importlib.reload if we're
# running python3
#
from compat import cpreload as reload
reload(planck)
from planck import planckInvert
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import Normalize
from matplotlib import cm
import numpy as np
import textwrap
import io,json
from collections import OrderedDict as od
import compat
reload(compat)
from compat import text_
import numpy.ma as ma

def make_plot(lcc_values):
    """
      set up the basic map projection details with coastlines and meridians
      return the projection object for further plotting
    """
    proj = Basemap(**lcc_values)
    parallels = np.arange(-90, 90, 1)
    meridians = np.arange(0, 360, 2)
    proj.drawparallels(parallels, labels=[1, 0, 0, 0],
                       fontsize=10, latmax=90)
    proj.drawmeridians(meridians, labels=[0, 0, 0, 1],
                       fontsize=10, latmax=90)
    # draw coast & fill continents
    # map.fillcontinents(color=[0.25, 0.25, 0.25], lake_color=None) # coral
    proj.drawcoastlines(linewidth=3., linestyle='solid', color='r')
    return proj


def find_corners(lons, lats):
    """
      guess values for the upper right and lower left corners of the
      lat/lon grid and the grid center based on max/min lat lon in the
      data and return a dictionary that can be passed to Basemap to set
      the lcc projection.  Also return the smallest lat and lon differences
      to get a feeling for the image resolution
    """
    min_lat, min_lon = np.min(lats), np.min(lons)
    max_lat, max_lon = np.max(lats), np.max(lons)
    llcrnrlon, llcrnrlat = min_lon, min_lat
    urcrnrlon, urcrnrlat = max_lon, max_lat
    lon_res=np.min(np.abs(np.diff(lons.flat)))
    lat_res=np.min(np.abs(np.diff(lats.flat)))
    out=dict(llcrnrlon=llcrnrlon,llcrnrlat=llcrnrlat,
             urcrnrlon=urcrnrlon,urcrnrlat=urcrnrlat,
             lat_1=llcrnrlat,lat_2=urcrnrlat,lat_0=(llcrnrlat+urcrnrlat)/2.,
             lon_0=(llcrnrlon + urcrnrlon)/2.)
    return(out,lon_res,lat_res)

in_file = 'svc_AIRS.2015.04.05.225.L2.RetStd.v6.0.11.0.G15096141835.h5'

with h5py.File(in_file) as airs_h5:
    missing_val=airs_h5['/L2_Standard_atmospheric&surface_product']['Data Fields']['CH4_total_column'].attrs['_FillValue']
    ch4_col = airs_h5['/L2_Standard_atmospheric&surface_product']['Data Fields']['CH4_total_column'][...]
    the_lon = airs_h5['/L2_Standard_atmospheric&surface_product']['Geolocation Fields']['Longitude'][...]
    the_lat = airs_h5['/L2_Standard_atmospheric&surface_product']['Geolocation Fields']['Latitude'][...]

bad_values=ch4_col == missing_val    
#plt.scatter(the_lon,the_lat)
#plt.hist(ch4_col)

ch4_col_converted = ch4_col*(16*1.66054e-27/1.e-4) #convert from molecules ch4/cm^2 to kg/m^2
ch4_col_converted[bad_values]=missing_val

plt.close('all')
fig,ax=plt.subplots(1,1,figsize=(10,10))
ax.hist(ch4_col_converted.ravel())
ax.set_title('pre-gridded')



#ch4_col_test = ch4_col*(2.656864e22)
#plt.hist(ch4_col_test)


#plt.show()

#make a basemap

lcc_values,lon_res,lat_res=find_corners(the_lon,the_lat)
lcc_values['fix_aspect']=True
lcc_values['lat_0']=53.
lcc_values['lat_1']=41.
lcc_values['lat_2']=65.
lcc_values['llcrnrlat']=39.
lcc_values['urcrnrlat']=56.
lcc_values['llcrnrlon']= -159.
lcc_values['urcrnrlon']= -125.
lcc_values['width']=200.e3
lcc_values['height']=500.e3
lcc_values['resolution']='c'
lcc_values['projection']='lcc'


latlim=[lcc_values['llcrnrlat'],lcc_values['urcrnrlat']]
lonlim=[lcc_values['llcrnrlon'],lcc_values['urcrnrlon']]
res=0.5
ch4_col_grid, longrid, latgrid, bin_count = reproj_numba(ch4_col_converted,missing_val, the_lon, the_lat, lonlim, latlim, res)
ch4_col_grid=ma.array(ch4_col_grid,mask=np.isnan(ch4_col_grid))

fig,ax=plt.subplots(1,1,figsize=(10,10))
hit=np.logical_not(np.isnan(ch4_col_grid))
ax.hist(ch4_col_grid[hit])
ax.set_title('gridded')

#phase_grid,longrid, latgrid, bin_count = reproj_numba(phase,missing_val, the_lon, the_lat, lonlim, latlim, res)

    
cmap=cm.YlGn  #see http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
cmap.set_over('r')
cmap.set_under('b') 
cmap.set_bad('0.75') #75% grey
vmin= 0.009
vmax= 0.011

the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)
fig,ax=plt.subplots(1,1,figsize=(10,10))
    #
    # tell Basemap what axis to plot into
    #
lcc_values['ax']=ax
proj=make_plot(lcc_values)
x,y=proj(longrid,latgrid)
CS=proj.ax.pcolormesh(x,y,ch4_col_grid,cmap=cmap,norm=the_norm)
CBar=proj.colorbar(CS, 'right', size='5%', pad='5%',extend='both')
CBar.set_label('Methane Total Column')
proj.ax.set_title('Methane total column')
proj.ax.figure.canvas.draw()
plt.show()   
 #fch4ig.savefig('{}/ch4totcol.png'.format(plot_dir))




