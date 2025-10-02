# --- paths (adjust only the first three if yours differ) ---
OIFS_HOME="/home/yi260/rds/hpc-work/openifs/openifs-48r1"
OIFS_EXPT="/home/yi260/rds/hpc-work/openifs/openifs-expt/48r1"
IMAGE="$HOME/rds/hpc-work/containers/openifs_48r1.1.sif"

CASE=BOMEX
TS=900
EXP=bomex_test

SCM_VERSIONDIR="$OIFS_EXPT"
SCM_PROJDIR="$SCM_VERSIONDIR/scm-projects"
SCM_RUNDIR="$SCM_PROJDIR/ref48r1"
OUT="$SCM_RUNDIR/scmout_${CASE}_${EXP}_${TS}s"
SCM_TEST="$OIFS_HOME/scripts/scm"
SCM_EXEC="$OIFS_HOME/build/bin/MASTER_scm.DP"
RAD_DIR="$OIFS_EXPT/scm-ancillary"   # <- where your RADRRTM/RADSRTM live

# Start clean to avoid stale partial output
rm -rf "$OUT"
mkdir -p "$SCM_RUNDIR"

# 1) Have callscm create the run directory
export APPTAINER_BINDPATH="$OIFS_HOME:$OIFS_HOME,$SCM_VERSIONDIR:$SCM_VERSIONDIR"
apptainer exec --cleanenv "$IMAGE" bash -lc "
  set -euo pipefail
  export OIFS_HOME='$OIFS_HOME'
  export SCM_TEST='$SCM_TEST'
  export SCM_EXEC='$SCM_EXEC'
  export SCM_RUNDIR='$SCM_RUNDIR'
  export SCM_PROJDIR='$SCM_PROJDIR'
  export SCM_VERSIONDIR='$SCM_VERSIONDIR'
  export SCM_LOGFILE='$SCM_RUNDIR/scm_run_log.txt'
  ulimit -s unlimited
  '$SCM_TEST'/callscm -c '$CASE' -t '$TS' -x '$EXP'
"

# 2) Stage radiation tables into the working directory (links OK)
# ln -sf "$RAD_DIR/RADRRTM" "$OUT/RADRRTM"
# ln -sf "$RAD_DIR/RADSRTM" "$OUT/RADSRTM"

# 3) Run the executable **from the working directory**
export APPTAINER_BINDPATH="$OUT:$OUT,$OIFS_HOME:$OIFS_HOME"
export OMP_NUM_THREADS=1  # start simple; you can raise later
apptainer exec --cleanenv "$IMAGE" bash -lc "
  set -euo pipefail
  ulimit -s unlimited
  cd '$OUT'
  '$SCM_EXEC' 2>&1 | tee run.log
"
