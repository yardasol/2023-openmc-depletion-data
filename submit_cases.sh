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
        FILENAME="case$JOBNAME.sbatch"
        cd $DIRNAME
        sbatch $FILENAME
        cd ../
      done
    done
  done
done
