import os
import re
import numpy as np
import xarray as xr
from sys import exit
#
# === USER CONFIGURATION ===
start_date_arg = "20200815_12"
input_dir = f"/glade/work/rozoff/fire/viirs/viirs_on_model_grid/{start_date_arg}"
output_dir = f"/glade/work/rozoff/fire/viirs/model_structure/{start_date_arg}"
os.makedirs(output_dir, exist_ok=True)
#
# Forecast hours to loop over
forecast_hours = [f"f{str(i).zfill(3)}" for i in range(73)]
#
# Regex to capture forecast hour
pattern = re.compile(r"viirs_on_model_(f\d{3})_AER\w+.*\.nc$")
#
# Index all available files
all_files = os.listdir(input_dir)
forecast_groups = {}
for fname in all_files:
    match = pattern.match(fname)
    if match:
        fhr = match.group(1)
        forecast_groups.setdefault(fhr, []).append(os.path.join(input_dir, fname))
#
# Reference grid (from any available file)
reference_file = next((os.path.join(input_dir, f) for f in all_files if f.endswith(".nc")), None)
if reference_file is None:
    raise FileNotFoundError("No reference NetCDF file found in input directory.")
#
with xr.open_dataset(reference_file) as ref:
    lat_ref = ref['lat'].values
    lon_ref = ref['lon'].values
    shape = lat_ref.shape
#
for fhr in forecast_hours:
    files = forecast_groups.get(fhr, [])
    print(f"Processing forecast hour {fhr} with {len(files)} file(s)...")

    exit()
