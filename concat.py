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
    #
    if len(files) == 1:
        with xr.open_dataset(files[0]) as ds:
            lat = ds['lat'].values
            lon = ds['lon'].values
            model_aod = ds['model_aod'].values
            viirs_aod_interp = ds['viirs_aod_interp'].values
    elif len(files) > 1:
        # Merge multiple files
        with xr.open_dataset(files[0]) as ds_base:
            model_aod = ds_base['model_aod'].values
        #
        viirs_aod_interp = np.full(shape, np.nan, dtype = np.float32)
        #
        for f in files:
            with xr.open_dataset(f) as ds:
                interp = ds['viirs_aod_interp'].values
                #
                mask_interp = ~np.isnan(interp)
                viirs_aod_interp[mask_interp] = interp[mask_interp]

    else:
        # No files → fill all with NaNs
        model_aod = np.full(shape, np.nan, dtype=np.float32)
        viirs_aod_interp = np.full(shape, np.nan, dtype=np.float32)
    # Build merged dataset
    merged_ds = xr.Dataset(
        {
            "lat": (("grid_yt", "grid_xt"), lat_ref),
            "lon": (("grid_yt", "grid_xt"), lon_ref),
            "model_aod": (("grid_yt", "grid_xt"), model_aod),
            "viirs_aod_interp": (("grid_yt", "grid_xt"), viirs_aod_interp),
        }
    )

    # Save output file with requested naming
    out_name = f"viirs_model.{fhr}.nc"
    out_path = os.path.join(output_dir, out_name)
    merged_ds.to_netcdf(out_path)
    print(f"Saved: {out_path}")
