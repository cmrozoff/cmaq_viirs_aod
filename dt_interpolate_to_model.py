#
import os
import numpy as np
import netCDF4 as nc
import datetime as dt
from scipy.interpolate import griddata
from glob import glob
from sys import exit
from datetime import datetime
import sys
#
if len(sys.argv) < 2:
    print("Usage: python interpolate_to_model.py YYYYMMDD_HH")
    sys.exit(1)
#
# Parse date argument from command line
start_date_arg = sys.argv[1]  # e.g., "20200816_12"
year = int(start_date_arg[0:4])
month = int(start_date_arg[4:6])
day = int(start_date_arg[6:8])
hour = int(start_date_arg[9:11])
#
# ---------------------------
# CONFIG
# ---------------------------
model_dir = f"/glade/campaign/ral/nsap/paddy/NOAA_fire/2020_ensemble_downsampled_data/rave.gfs.nei.CONTROL/{start_date_arg}/"
viirs_dir = "/glade/campaign/acom/acom-weather/pfister/ANALYSIS/MELODIES/viirs/"
model_init = dt.datetime(year, month, day, hour, 0)
time_tolerance = dt.timedelta(minutes=30)  # match VIIRS scan to forecast hour ±30 min
output_dir = f"./viirs_on_model_grid/{start_date_arg}/"
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
def read_model_file(path):
    with nc.Dataset(path) as ds:
        aod = ds.variables["aod"][:].squeeze()  # shape (yt, xt)
        lat = ds.variables["lat"][:]
        lon = ds.variables["lon"][:]
        # Convert longitudes from 0–360 to -180–180
        lon = np.where(lon > 180, lon - 360, lon)
    return aod, lat, lon
#
def read_viirs_file(path):
    with nc.Dataset(path) as ds:
        # Check if required AOD variables are present
        required_vars = [
            "Optical_Depth_Land_And_Ocean",
            "Latitude",
            "Longitude"
        ]
        for var in required_vars:
            if var not in ds.variables:
                print(f"    Skipping {os.path.basename(path)}: missing variable {var}")
                return None, None, None
        aod = ds.variables["Optical_Depth_Land_And_Ocean"][:]
        lat = ds.variables["Latitude"][:]
        lon = ds.variables["Longitude"][:]
    return aod, lat, lon
#
def interpolate_sat_to_model(sat_aod, sat_lat, sat_lon, lat_model, lon_model):
    #
    # Flatten all inputs
    sat_aod_flat = sat_aod.ravel()
    sat_lat_flat = sat_lat.ravel()
    sat_lon_flat = sat_lon.ravel()
    #
    # Convert invalid values (<0) to NaN
    sat_aod_flat = np.where(sat_aod_flat < 0, np.nan, sat_aod_flat)
    #
    # Build mask
    mask = np.isfinite(sat_aod_flat) & (~np.isnan(sat_aod_flat))
    if np.sum(mask) < 10:
        return None

    # Combine points
    points = np.column_stack((sat_lat_flat[mask], sat_lon_flat[mask]))
    grid_points = np.column_stack((lat_model.ravel(), lon_model.ravel()))

    # Perform spatial interpolation
    interp_aod = griddata(points, sat_aod_flat[mask], grid_points, method='linear')
    return interp_aod.reshape(lat_model.shape)
#
# ---------------------------
# 1. Collect VIIRS files
# ---------------------------
viirs_files = sorted(glob(os.path.join(viirs_dir, "AERDT*SNPP.A2020*.nc")))
viirs_times = [extract_viirs_time(f) for f in viirs_files]
#
# ---------------------------
# 2. Loop over model forecast hours
# ---------------------------
for h in range(0, 73):  # hours 0–72
    model_time = model_init + dt.timedelta(hours=h)
    model_file = os.path.join(model_dir, f"aqm.t12z.phy.f{h:03d}.nc")
    #
    if not os.path.exists(model_file):
        print(f"Skipping missing model file: {model_file}")
        continue
    #
    print(f"\nProcessing model forecast hour {h} ({model_time})")
    #
    # Read model data
    aod_model, lat_model, lon_model = read_model_file(model_file)
    #
    # Find VIIRS files within tolerance
    matched_files = [f for f, t in zip(viirs_files, viirs_times)
                     if abs(t - model_time) <= time_tolerance]
    #
    if not matched_files:
        print("  No VIIRS files within time tolerance")
        continue
    #
    for vf in matched_files:
        print(f"  Matching VIIRS file: {os.path.basename(vf)}")
        sat_aod, sat_lat, sat_lon = read_viirs_file(vf)
        if sat_aod is None:
            continue # Skip this file and go to the next one
        #
        # Check overlap with model domain
        lat_min, lat_max = np.nanmin(lat_model), np.nanmax(lat_model)
        lon_min, lon_max = np.nanmin(lon_model), np.nanmax(lon_model)
        overlap_mask = ((sat_lat >= lat_min) & (sat_lat <= lat_max) &
                        (sat_lon >= lon_min) & (sat_lon <= lon_max))
        if not np.any(overlap_mask):
            print("    Skipping: no overlap with model domain")
            continue
        #
        # Spatial interpolation
        interp_aod = interpolate_sat_to_model(sat_aod, sat_lat, sat_lon, lat_model, lon_model)
        if interp_aod is None or np.all(np.isnan(interp_aod)):
            print("    Skipping: all VIIRS data missing or invalid")
            continue
        # Save interpolated satellite data to NetCDF
        out_file = os.path.join(output_dir, f"viirs_on_model_f{h:03d}_{os.path.basename(vf)}")
        with nc.Dataset(out_file, "w") as ds_out:
            # Define dims
            ds_out.createDimension("grid_yt", lat_model.shape[0])
            ds_out.createDimension("grid_xt", lat_model.shape[1])
            # Variables
            lat_out = ds_out.createVariable("lat", "f4", ("grid_yt", "grid_xt"))
            lon_out = ds_out.createVariable("lon", "f4", ("grid_yt", "grid_xt"))
            aod_out = ds_out.createVariable("viirs_aod_interp", "f4", ("grid_yt", "grid_xt"), fill_value=np.nan)
            model_aod_out = ds_out.createVariable("model_aod", "f4", ("grid_yt", "grid_xt"), fill_value=np.nan)
            # Write
            lat_out[:] = lat_model
            lon_out[:] = lon_model
            aod_out[:] = interp_aod
            model_aod_out[:] = aod_model
        print(f"    Saved interpolated VIIRS data: {out_file}")
