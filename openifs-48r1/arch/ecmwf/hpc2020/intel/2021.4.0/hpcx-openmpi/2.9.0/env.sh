# Source me to get the correct configure/build/run environment

# Store tracing and disable (module is *way* too verbose)
{ tracing_=${-//[^x]/}; set +x; } 2>/dev/null

module_load() {
  echo "+ module load $*"
  module load $*
}
module_unload() {
  echo "+ module unload $*"
  module unload $*
}
module_purge() {
  echo "+ module purge"
  module purge
}

# Unload all modules to be certain
[[ ${IFS_RUNTIME_ENV:-unset} == "unset" ]] && module_purge

# Load modules (adapted for CSD3)
# module_load prgenv/intel  # Not available on your system
module_load intel-oneapi-compilers/2022.1.0
module_load intel-oneapi-mpi/2021.6.0
# module_load intel-mkl/19.0.5  

# Don't load these modules if env.sh is used as part of the IFS runtime environment - only the modules above are required
if [[ ${IFS_RUNTIME_ENV:-unset} == "unset" ]]; then
  # Try to load modules that might be available on the system
  module_load netcdf-c || true
  module_load netcdf-fortran || true
  module_load python || true
  # module_load fftw/3.3.9  # Comment out if not available
  # module_load netcdf4/4.7.4  # Comment out if not available
  # module_load hdf5/1.10.6  # Comment out if not available
  # module_load eigen/3.3.7  # Comment out if not available
  # module_load cmake/3.20.2  # Comment out if not available
  # module_load ninja/1.10.0  # Comment out if not available
  # module_load fcm/2019.05.0  # Comment out if not available
  # module_load aec/1.0.4  # Comment out if not available
fi

# Setting required for bit reproducibility with Intel MKL:
export MKL_CBWR=AUTO,STRICT

# Record the RPATH in the executable
export LD_RUN_PATH=$LD_LIBRARY_PATH

# Restore tracing to stored setting
{ if [[ -n "$tracing_" ]]; then set -x; else set +x; fi } 2>/dev/null

