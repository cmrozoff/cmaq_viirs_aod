#!/bin/bash

# ===== USER CONFIG =====
PYTHON_SCRIPT="/glade/work/rozoff/fire/viirs/interpolate_to_model.py"
START_DATE=20200816
END_DATE=20200930
END_DATE=20200817
INCREMENT_DAYS=5
INIT_HOUR=12

# Load environment (Cheyenne example)
module load conda
conda activate npl

# Convert YYYYMMDD to seconds since epoch for looping
current=$(date -d "${START_DATE}" +%s)
end=$(date -d "${END_DATE}" +%s)

# Loop over batches of 5 day
while [ "$current" -le "$end" ]; do
    batch_start=$(date -u -d "@$current" +"%Y%m%d")
    jobfile="job_${batch_start}.pbs"

    cat > $jobfile << EOF
#!/bin/bash
#PBS -N viirs_${batch_start}
#PBS -A NSAP0003
#PBS -q casper@casper-pbs
#PBS -l select=1:ncpus=1:mpiprocs=1
#PBS -l walltime=01:00:00
#PBS -o output${batch_start}.txt
#PBS -e errorlog${batch_start}.txt
#PBS -j oe

module load conda
conda activate npl
EOF

    # Loop over 5 days in this batch
    for offset in $(seq 0 $((BATCH_SIZE_DAYS-1))); do
        this_date=$(date -u -d "@$((current + offset * 86400))" +"%Y%m%d")
        # Only process dates within END_DATE
        if [ $(date -d "$this_date" +%s) -le $end ]; then
            echo "python $PYTHON_SCRIPT ${this_date}_${INIT_HOUR}" >> $jobfile
        fi
    done

    # Submit job
    qsub $jobfile

    # Advance to next batch
    current=$(date -d "$(date -u -d "@$current" +"%Y-%m-%d") +${BATCH_SIZE_DAYS} days" +%s)
done
