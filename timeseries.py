from datetime import datetime, timedelta
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
while current_date <= end_date:
    #
    print(current_date)
    current_date += timedelta(days=1)
