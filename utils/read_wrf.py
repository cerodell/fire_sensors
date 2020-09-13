import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime

from wrf import (getvar, g_uvmet, get_cartopy, latlon_coords)


""" ####################################################################### """
""" ###################### Grab WRF Variables ####################### """

def readwrf(filein):
    """
    This Fucntion read wrfout file and grabs varibels of internts and outputs as an xarray
    
    Parameters
    ----------
    
    files: netcdf files, delacred file name to write zar
    Returns
    -------
    
    ds_wrf: an xarray (zar) of wind speed (km h-1), temp (degC) & rh (%) 
    """
    ds_list = []
    pathlist = sorted(Path(filein).glob('wrfout_d01*'))
    # print(pathlist)
    for path in pathlist:
        path_in_str = str(path)
        wrf_file = Dataset(path_in_str,'r')
        
        slp        = getvar(wrf_file, "slp")
        rh        = getvar(wrf_file, "rh2")
        temp      = getvar(wrf_file, "T2")
        wsp_wdir  = g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='m s-1')

        rain_c    = getvar(wrf_file, "RAINC")
        rain_sh   = getvar(wrf_file, "RAINSH")
        rain_nc   = getvar(wrf_file, "RAINNC")
        
        # cord = get_cartopy(rh)
        # lat,lon = latlon_coords(rh)

        var_list = [slp, rh,temp,wsp_wdir,rain_c, rain_sh, rain_nc]
        # var_list = [rh]
        ds = xr.merge(var_list)
        # cord_list.append(cord)
        # lat_list.append(lat)
        # lon_list.append(lon)
        ds_list.append(ds)


    ds_wrf = xr.combine_nested(ds_list, 'time')

    # cord = cord_list[0]
    # lat, lon = lat_list[0], lon_list[0]

    # out_dir = str(context.data_dir)
    # out_dir = Path(str(context.data_dir)+str('/xr/') + str('/') +  str(ds_name) + str(f".zarr"))
    # out_dir.mkdir(parents=True, exist_ok=True)

    # # now = datetime.now() # current date and time
    # # folder_date = now.strftime("%Y%m%d")
    # # file_date = now.strftime("%Y%m%d_%H")
    # # print("date and time:",file_date)

    # ## Write and save DataArray (.zarr) file
    # # full_dir = str(out_dir) + str('/') +  str(ds_name) + str(f".zarr")

    # ds_wrf.compute()
    # ds_wrf.to_zarr(out_dir, "w")
    # print(f"wrote {out_dir}")
    
    return ds_wrf