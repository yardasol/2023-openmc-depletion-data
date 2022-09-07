#!/bin/bash

#SBATCH --nodes=2
#SBATCH --time=06:00:00
#SBATCH --partition=bdwall
#SBATCH --account=openmcvalidation
#SBATCH --job-name=1-cecm-minutes
#SBATCH --mail-user=oyardas@anl.gov
#SBATCH --mail-type=BEGIN,END,FAIL


# Setup environment (slurm doesn't run a shell, so no bashrc/profile by default
source $HOME/.bashrc 
module unload intel
conda activate openmc-env

# Go to working dir and set cross sections
export OPENMC_CROSS_SECTIONS=$(pwd)/../../cross-section-libraries/endfb71_hdf5/cross_sections.xml

# Determine number of MPI ranks
NUM_RANKS=$((SLURM_JOB_NUM_NODES * 2))


# Run job
srun -N $SLURM_JOB_NUM_NODES \
     -n $NUM_RANKS\
      --cpu-bind=socket \
      python -u run_case.py
