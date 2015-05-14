#!/usr/bin/env python
"""
  read the level1b file, geom file, cloud model file and the cloud mask file from dump_cloudmask.py and
  produce plots of the the particle phase

  usage:

  ./plot_palettes.py names.json

"""
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
import seaborn as sns
#
# compat module redefines importlib.reload if we're
# running python3
#
from compat import cpreload as reload
from planck import planckInvert
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import Normalize
from matplotlib import cm
import numpy as np
import textwrap
import io,json
from collections import OrderedDict as od
import compat
from compat import text_
import numpy.ma as ma
#
# two different ways of generating a colormap
# use this for continuous variables
from matplotlib.colors import LinearSegmentedColormap
#
# and use this for discrete colors
#
from matplotlib.colors import ListedColormap
import pdb




    
if __name__ == "__main__":

    linebreaks=argparse.RawTextHelpFormatter
    descrip=textwrap.dedent(globals()['__doc__'])
    parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
    parser.add_argument('initfile',type=str,help='name of json file with filenames')
    args=parser.parse_args()

    with io.open(args.initfile,'r',encoding='utf8') as f:
        name_dict=json.loads(f.read(),object_pairs_hook=od)

    geom_file,mod06_file=name_dict['geom_file'],name_dict['m06_file'],
    with h5py.File(geom_file) as geom_h5:
        the_lon=geom_h5['MODIS_Swath_Type_GEO']['Geolocation Fields']['Longitude'][...]
        the_lat=geom_h5['MODIS_Swath_Type_GEO']['Geolocation Fields']['Latitude'][...]

    with h5py.File(mod06_file) as m06_h5:
        phase=m06_h5['mod06']['Data Fields']['Cloud_Phase_Infrared_1km'][...]
        phase=phase.astype(np.int32)

    test=h5py.File(mod06_file)
    the_keys=list(test.keys())
    eff_rad=test['mod06']['Data Fields']['Cloud_Effective_Radius'][...]
    eff_rad=eff_rad.astype(np.float32)
    hit=eff_rad== -9999.
    eff_rad[hit]=np.nan
    print(np.sum(hit)/eff_rad.size)
    eff_rad=ma.array(eff_rad,mask=np.isnan(eff_rad))
    plt.close('all')
    plt.hist(eff_rad.compressed())
    plt.show()
    
