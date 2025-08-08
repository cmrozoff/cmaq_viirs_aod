#
# USER CONFIGURATION
input_dir = "/glade/work/rozoff/fire/viirs/model_structure/"
#
from datetime import datetime, timedelta
from sys import exit
import xarray as xr
import numpy as np
import os
#
start_date_arg = "20200818_12"
year = int(start_date_arg[0:4])
month = int(start_date_arg[4:6])
day = int(start_date_arg[6:8])
hour = int(start_date_arg[9:11])
#
# Start and end dates
start_date = datetime(year, month, day)
end_date = datetime(year, month, day)
#
# Loop over each date in the range
current_date = start_date
print("Reading in AOD data")
aod_mod = None
aod_obs = None
#
ref_dir = os.path.join(input_dir, start_date_arg)
all_files = os.listdir(ref_dir)
reference_file = next((os.path.join(ref_dir, f) for f in all_files if f.endswith(".nc")), None)
if reference_file is None:
    raise FileNotFoundError("No reference NetCDF file found in input directory.")
#
with xr.open_dataset(reference_file) as ref:
    lat_ref = ref['lat'].values
    lon_ref = ref['lon'].values
    shape = lat_ref.shape
#
# Forecast hours to loop over
forecast_hours = [f"f{str(i).zfill(3)}" for i in range(73)]
#
while current_date <= end_date:
    #
    print(current_date)
    for fhr in forecast_hours:
        print(f"Processing forecast hour {fhr} ...")
    current_date += timedelta(days=1)
