CASES=(2)
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
      sbatch sbatch_files/$FILENAME
    done
  done
done
