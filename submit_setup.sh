MODES=('simple' 'full')
for mode in ${MODES[@]}
do 
  JOBNAME="setup-$mode"
  DIRNAME="runtime-$JOBNAME"
  FILENAME="$JOBNAME.sbatch"
  cd $DIRNAME
  sbatch $FILENAME
  cd ../
done
