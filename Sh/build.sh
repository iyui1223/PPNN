#!/bin/bash
#SBATCH --job-name=IFS01_scm_build
#SBATCH --partition=sapphire
#SBATCH -A MPHIL-DIS-SL2-CPU # have to change this to CRANMER-SL3-CPU after 1-Oct-2025
#SBATCH --time=00:30:00 # takes about 20 mins for full build -- reduce for partial compile
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --output=/home/yi260/rds/hpc-work/openifs/Log/%x.out
#SBATCH --error=/home/yi260/rds/hpc-work/openifs/Log/%x.err

set -euo pipefail

# Prevent arch/env.sh from purging and loading ECMWF site-specific modules
export IFS_RUNTIME_ENV=1
export IFS_KEEP_MODULES=1

ROOT_DIR="/home/yi260/rds/hpc-work/openifs"
OIFS_DIR="${ROOT_DIR}/org/openifs-data/src/48r1/openifs-48r1"
mkdir -p "${ROOT_DIR}/Log"
export PATH="/home/yi260/rds/hpc-work/openifs/.venv-ecmwf/bin:$PATH"
# Python environment for Fypp
export FYPP_PYTHON="/home/yi260/rds/hpc-work/openifs/.venv-ecmwf/bin/python"
export PYTHONPATH="${OIFS_DIR}/ifs-source/arpifs/scripts:${PYTHONPATH:-}"

type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh || true
# Toolchain
module load intel-oneapi-compilers/2022.1.0 || true
module load intel-oneapi-mpi/2021.6.0 || true
# Python (for Fypp); try to load a python module if available
module load python || true
# NetCDF (C and Fortran if available)
module load netcdf-c || true
module load netcdf-fortran || true
if ! command -v srun >/dev/null 2>&1; then
  module load slurm || module load rhel8/slurm || true
fi

# Ensure Python with PyYAML for Fypp
PYTHON_BIN=$(command -v python3 || command -v python || true)
if [ -z "${PYTHON_BIN}" ]; then
  echo "ERROR: No python interpreter found for Fypp (requires PyYAML)." >&2
  exit 1
fi

# Discover NetCDF prefixes and make them visible to the build system
NETCDF_C_PREFIX="${NETCDF_C_PREFIX:-}"
NETCDF_F_PREFIX="${NETCDF_F_PREFIX:-}"
if command -v nc-config >/dev/null 2>&1; then
  NETCDF_C_PREFIX="$(nc-config --prefix)"
fi
if command -v nf-config >/dev/null 2>&1; then
  NETCDF_F_PREFIX="$(nf-config --prefix)"
fi

# Prefer C prefix for NETCDF_PATH (provides netcdf.h and libnetcdf)
if [ -z "${NETCDF_PATH:-}" ]; then
  if [ -n "${NETCDF_C_PREFIX}" ]; then
    export NETCDF_PATH="${NETCDF_C_PREFIX}"
  elif [ -n "${NETCDF_F_PREFIX}" ]; then
    export NETCDF_PATH="${NETCDF_F_PREFIX}"
  fi
fi
export NETCDF_ROOT="${NETCDF_PATH}" NETCDF_DIR="${NETCDF_PATH}" NETCDF4_DIR="${NETCDF_PATH}"

# Help CMake find both C and Fortran pieces
if [ -n "${NETCDF_C_PREFIX}" ]; then
  export CMAKE_PREFIX_PATH="${NETCDF_C_PREFIX}:${CMAKE_PREFIX_PATH:-}"
  export PATH="${NETCDF_C_PREFIX}/bin:${PATH}"
fi
if [ -n "${NETCDF_F_PREFIX}" ]; then
  export CMAKE_PREFIX_PATH="${NETCDF_F_PREFIX}:${CMAKE_PREFIX_PATH}"
  export PATH="${NETCDF_F_PREFIX}/bin:${PATH}"
fi

# Prefer MPI compiler wrappers to ensure MPI is linked
MPI_FC=$(command -v mpiifort || command -v mpifort || command -v mpif90 || true)
MPI_CC=$(command -v mpiicc || command -v mpicc || true)
MPI_CXX=$(command -v mpiicpc || command -v mpicxx || command -v mpic++ || true)
if [ -n "${MPI_FC}" ]; then export FC="${MPI_FC}"; fi
if [ -n "${MPI_CC}" ]; then export CC="${MPI_CC}"; fi
if [ -n "${MPI_CXX}" ]; then export CXX="${MPI_CXX}"; fi

# Fallbacks if wrappers are missing
export FC=${FC:-$(command -v ifort || true)}
export F77=${F77:-$FC}
export F90=${F90:-$FC}
export CC=${CC:-$(command -v icc || command -v icx || echo cc)}
export CXX=${CXX:-$(command -v icpc || command -v icpx || echo c++)}

# Ensure pthread is linked for tests using threads
export CFLAGS="${CFLAGS:-} -pthread"
export CXXFLAGS="${CXXFLAGS:-} -pthread"
export LDFLAGS="-pthread ${LDFLAGS:-}"
export CMAKE_EXE_LINKER_FLAGS="${CMAKE_EXE_LINKER_FLAGS:-} -pthread"

# Clean previous CMake cache to force re-detection of compilers 
# Commented out as clean build environment is established
# rm -rf "${OIFS_DIR}/build"

source "${OIFS_DIR}/oifs-config.edit_me.sh"

# Provide launchers that work inside an sbatch allocation (no salloc)
TOTAL_CPUS=$(( SLURM_CPUS_PER_TASK * SLURM_NTASKS ))
export IGT_BUILD_LAUNCHER="srun -n 1 -c ${SLURM_CPUS_PER_TASK}"
export IGT_TEST_LAUNCHER="srun -n 8 -c ${SLURM_CPUS_PER_TASK}"

# Build SCM only, skip tests to save time
"${OIFS_DIR}/scripts/build_test/openifs-test.sh" -b -c -j "${TOTAL_CPUS}" --without-tests --without-ifs-test --with-scmec

