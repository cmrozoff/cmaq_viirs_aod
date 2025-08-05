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
# 1. Collect VIIRS files
# ---------------------------
viirs_files = sorted(glob(os.path.join(viirs_dir, "AER*SNPP.A2020*.nc")))
print(viirs_files)

