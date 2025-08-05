#
import os
import numpy as np
import netCDF4 as nc
import datetime as dt
from scipy.interpolate import griddata
from glob import glob
#
file_viirs='/glade/campaign/acom/acom-weather/pfister/ANALYSIS/MELODIES/viirs/AERDB_L2_VIIRS_SNPP.A2020259.1954.002.2023076071527.nc'
file_model='/glade/campaign/ral/nsap/paddy/NOAA_fire/2020_ensemble_downsampled_data/rave.gfs.nei.CONTROL/20200915_12/aqm.t12z.phy.f007.nc'

# ---------------------------
# CONFIG
# ---------------------------
model_dir = "/glade/campaign/ral/nsap/paddy/NOAA_fire/2020_ensemble_downsampled_data/rave.gfs.nei.CONTROL/20200915_12/"
viirs_dir = "/glade/campaign/acom/acom-weather/pfister/ANALYSIS/MELODIES/viirs/"
model_init = dt.datetime(2020, 9, 15, 12, 0)
time_tolerance = dt.timedelta(minutes=30)  # match VIIRS scan to forecast hour ±30 min
output_dir = "./viirs_on_model_grid/"
os.makedirs(output_dir, exist_ok=True)
#
# ---------------------------
# FUNCTIONS
# ---------------------------
def extract_viirs_time(fname):
    # Example: A2020259.1954 -> 2020, day 259, time 19:54 UTC
    base = os.path.basename(fname)
    year = int(base[21:25])
    doy = int(base[25:28])
    hour = int(base[29:31])
    minute = int(base[31:33])
    return dt.datetime(year, 1, 1) + dt.timedelta(days=doy-1, hours=hour, minutes=minute)

#
# ---------------------------
# 1. Collect VIIRS files
# ---------------------------
viirs_files = sorted(glob(os.path.join(viirs_dir, "AER*SNPP.A2020*.nc")))
viirs_times = [extract_viirs_time(f) for f in viirs_files]
print(viirs_times)
