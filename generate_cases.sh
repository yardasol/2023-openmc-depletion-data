NODES=4
TIME="3:00:00"
EMAIL="oyardas2@illinois.edu"

CASES=(1 2 3)
INTEGRATORS=('predictor' 'cecm')
MODES=('simple' 'full')
TIMESCALES=('minutes' 'hours' 'days' 'months')
for case in ${CASES[@]}
do 
  for integrator in ${INTEGRATORS[@]}
  do
    for mode in ${MODES[@]}
    do 
      for scale in ${TIMESCALES[@]}
      do
        JOBNAME="$case-$scale-$integrator-$mode"
        DIRNAME="runtime-case$JOBNAME" 
        FILENAME=$DIRNAME"/case$JOBNAME.sbatch"
        mkdir -p $DIRNAME
      	touch $FILENAME
      	echo -e "#!/bin/bash\n\n#SBATCH --nodes=$NODES\n#SBATCH --time=$TIME\n#SBATCH --partition=bdwall\n#SBATCH --account=fusionsdr\n#SBATCH --job-name=$JOBNAME\n#SBATCH --mail-user=$EMAIL\n#SBATCH --mail-type=BEGIN,END,FAIL" > $FILENAME
      	echo -e "source \$HOME/.bashrc\nmodule unload intel\nconda activate openmc-env\nexport OPENMC_CROSS_SECTIONS=\$(pwd)/../../cross-section-libraries/endfb71_hdf5/cross_sections.xml\nNUM_RANKS=\$((SLURM_JOB_NUM_NODES * 2))" >> $FILENAME

        if [[ $case -eq 3 ]]
        then
          echo "python ../run_depletion_case.py -c$case -i $integrator -m $mode -t $scale -N \$SLURM_JOB_NUM_NODES -n \$NUM_RANKS" >> $FILENAME
        else
          echo "srun -N \$SLURM_JOB_NUM_NODES \\" >> $FILENAME
          echo "     -n \$NUM_RANKS \\" >> $FILENAME
          echo "      --cpu-bind=socket \\" >> $FILENAME
          echo "      python -u ../run_depletion_case.py -c$case -i $integrator -m $mode -t $scale" >> $FILENAME
        fi
      done
    done
  done
done
