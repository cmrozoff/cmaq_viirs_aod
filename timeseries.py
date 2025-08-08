#
# USER CONFIGURATION
input_dir = "/glade/work/rozoff/fire/viirs/model_structure/"
#
from datetime import datetime, timedelta
from sys import exit
#
# Start and end dates
start_date = datetime(2020, 8, 18)
end_date = datetime(2020, 9, 30)
#
# Loop over each date in the range
current_date = start_date
print("Reading in AOD data")
aod_mod = None
aod_obs = None
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
