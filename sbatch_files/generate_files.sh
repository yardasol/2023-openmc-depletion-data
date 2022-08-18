NODES=2
TIME="06:00:00"
EMAIL="oyardas@anl.gov"

CASES=(1 2 3)
TIMESCALES=('minutes' 'hours' 'days' 'months')
INTEGRATORS=('predictor' 'cecm')
for case in ${CASES[@]}
do 
  for scale in ${TIMESCALES[@]}
  do
    for integrator in ${INTEGRATORS[@]}
    do
      JOBNAME="$case-$integrator-$scale"
      FILENAME="case$JOBNAME.sbatch"
      touch $FILENAME
      echo -e "#!/bin/bash\n\n#SBATCH --nodes=$NODES\n#SBATCH --time=$TIME\n#SBATCH --partition=bdwall\n#SBATCH --account=openmcvalidation\n#SBATCH --job-name=$JOBNAME\n#SBATCH --mail-user=$EMAIL\n#SBATCH --mail-type=BEGIN,END,FAIL" > $FILENAME
      echo -e "source $HOME/.bashrc\nmodule unload intel\nconda activate openmc-env\nexport OPENMC_CROSS_SECTIONS=\$(pwd)/../cross-section-libraries/endfb71_hdf5/cross_sections.xml\nNUM_RANKS=\$((SLURM_JOB_NUM_NODES * 2))" >> $FILENAME

      echo "srun -N \$SLURM_JOB_NUM_NODES \\" >> $FILENAME
      echo "     -n \$NUM_RANKS\\" >> $FILENAME
      echo "      --cpu-bind=socket \\" >> $FILENAME
      echo "      python -u run_case$case.py -integrator $integrator -timescale $scale" >> $FILENAME
    done
  done
done
