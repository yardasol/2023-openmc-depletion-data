NODES=2
TIME="06:00:00"
EMAIL="oyardas2@illinois.edu"

MODES=('simple' 'full')
for mode in ${MODES[@]}
do 
  JOBNAME="setup-$mode"
  DIRNAME="runtime-$JOBNAME" 
  FILENAME=$DIRNAME"/$JOBNAME.sbatch"
  mkdir -p $DIRNAME
  touch $FILENAME
  echo -e "#!/bin/bash\n\n#SBATCH --nodes=$NODES\n#SBATCH --time=$TIME\n#SBATCH --partition=bdwall\n#SBATCH --account=openmcvalidation\n#SBATCH --job-name=$JOBNAME\n#SBATCH --mail-user=$EMAIL\n#SBATCH --mail-type=BEGIN,END,FAIL" > $FILENAME
  echo -e "source \$HOME/.bashrc\nmodule unload intel\nconda activate openmc-env\nexport OPENMC_CROSS_SECTIONS=\$(pwd)/../../cross-section-libraries/endfb71_hdf5/cross_sections.xml\nNUM_RANKS=\$((SLURM_JOB_NUM_NODES * 2))" >> $FILENAME

  echo "python ../run_depletion_setup.py -m $mode -N \$SLURM_JOB_NUM_NODES -n \$NUM_RANKS" >> $FILENAME
done
