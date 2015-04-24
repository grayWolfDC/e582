keep_list=[]
for fname in glob.glob(path):
  with h5py.File(fname) as airs_h5:
       missing_val =  airs_h5['/L2_Standard_atmospheric&surface_product']['Data Fields']['CH4_total_column'].attrs['_FillValue']
       ch4_col = airs_h5['/L2_Standard_atmospheric&surface_product']['Data Fields']['CH4_total_column'][...]
       the_lon = airs_h5['/L2_Standard_atmospheric&surface_product']['Geolocation Fields']['Longitude'][...]
       the_lat = airs_h5['/L2_Standard_atmospheric&surface_product']['Geolocation Fields']['Latitude'][...]
       keep_dict=dict(fname=fname,missing_val=missing_val,ch4_col=ch4col,the_lon=the_lon,the_lat=the_lat)
       keep_list.append(keep_dict)



