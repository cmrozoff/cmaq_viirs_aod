#!/bin/bash

# ===== USER CONFIG =====
PYTHON_SCRIPT="/glade/work/rozoff/fire/viirs/dt_interpolate_to_model.py"
START_DATE=20200815
END_DATE=20200815
BATCH_SIZE_DAYS=5
INIT_HOUR=12

# Convert YYYYMMDD to seconds since epoch
current=$(date -d "${START_DATE}" +%s)
end=$(date -d "${END_DATE}" +%s)

# Loop over 5-day batches
while [ "$current" -le "$end" ]; do
    batch_start=$(date -u -d "@$current" +"%Y%m%d")
    jobfile="job_${batch_start}.pbs"

    echo "Creating job file: $jobfile"

    # Write job header
    cat > "$jobfile" << EOF
#!/bin/bash
#PBS -N viirs_${batch_start}
#PBS -A NSAP0003
#PBS -q casper@casper-pbs
#PBS -l select=1:ncpus=1:mem=64GB
#PBS -l walltime=07:00:00
#PBS -o output${batch_start}.txt
#PBS -e errorlog${batch_start}.txt
#PBS -j oe

cd \$PBS_O_WORKDIR
module load conda
conda activate npl
EOF

    # Add Python commands for each day in the batch
    for offset in $(seq 0 $((BATCH_SIZE_DAYS-1))); do
        this_sec=$((current + offset * 86400))
        this_date=$(date -u -d "@$this_sec" +"%Y%m%d")
        if [ -n "$this_date" ] && [ $(date -d "$this_date" +%s) -le $end ]; then
            echo "  -> Adding command for $this_date"
            echo "python $PYTHON_SCRIPT ${this_date}_${INIT_HOUR}" >> "$jobfile"
        fi
    done

    # Show file content for debugging
    echo "---- PBS FILE CONTENT ----"
    cat "$jobfile"
    echo "--------------------------"

    # Submit job
    qsub "$jobfile"

    # Move to next batch
    current=$(date -d "$(date -u -d "@$current" +"%Y-%m-%d") +${BATCH_SIZE_DAYS} days" +%s)
done

