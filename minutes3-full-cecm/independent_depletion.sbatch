#!/bin/bash

#SBATCH --nodes=4
#SBATCH --time=06:00:00
#SBATCH --partition=bdwall
#SBATCH --account=openmcvalidation
#SBATCH --job-name=3-cecm-minutes
#SBATCH --mail-user=oyardas@anl.gov
#SBATCH --mail-type=BEGIN,END,FAIL


# Setup environment (slurm doesn't run a shell, so no bashrc/profile by default
source $HOME/.bashrc 
module unload intel
conda activate openmc-env

# Go to working dir and set cross sections
export OPENMC_CROSS_SECTIONS=$(pwd)/../../cross-section-libraries/endfb71_hdf5/cross_sections.xml

# Run job
python -u run_case.py
