#!/bin/bash

# ===== USER CONFIG =====
PYTHON_SCRIPT="/glade/work/rozoff/fire/viirs/interpolate_to_model.py"
START_DATE=20200816
END_DATE=20200930
INCREMENT_DAYS=5
INIT_HOUR=12

# Load environment (Cheyenne example)
module load conda
conda activate npl

# Convert YYYYMMDD to seconds since epoch for looping
current=$(date -d "${START_DATE}" +%s)
end=$(date -d "${END_DATE}" +%s)

# Loop over 5-day increments
while [ $current -le $end ]; do
    date_str=$(date -u -d "@$current" +"%Y%m%d")
    rundate="${date_str}_${INIT_HOUR}"

    # Create PBS script for this run
    jobfile="job_${rundate}.pbs"
    cat > $jobfile << EOF
#!/bin/bash
#PBS -N viirs_${rundate}
#PBS -A NSAP0003
#PBS -q regular
#PBS -l select=1:ncpus=1:mem=64GB
#PBS -l walltime=05:00:00
#PBS -j oe

cd \$PBS_O_WORKDIR
module load conda
conda activate npl

python $PYTHON_SCRIPT $rundate
EOF

    # Submit job
    qsub $jobfile

    # Advance 5 days
    current=$(date -d "@$current +${INCREMENT_DAYS} days" +%s)
done
