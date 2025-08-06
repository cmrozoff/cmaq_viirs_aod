import os
import re
import numpy as np
import xarray as xr
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
pattern = re.compile(r"viirs_on_model_(f\d{3})_AER*\.nc$")
print(forecast_hours)
