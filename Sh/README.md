# OpenIFS 48r1.1 on CSD3 via GitHub + Apptainer (CPU-only)

This repo documents a reproducible way to run OpenIFS 48r1.1 on CSD3 using a container built by GitHub Actions, then converted/pulled into an Apptainer (.sif) image on CSD3.

## What this does

- Builds a Docker/OCI image in GitHub Actions from the provided Dockerfile (toolchain + deps).
- Publishes the image to GHCR (GitHub Container Registry).
- On CSD3, fetches/converts that image to a .sif and uses it as a build & runtime environment.
- OpenIFS executables are built on CSD3 (they are not baked into the image).

## 0) Prerequisites

- A GitHub account with access to this repo.
- CSD3 account with Apptainer available (`apptainer --version`).
- You have OpenIFS 48r1.1 sources (licensed) and can place them on CSD3 storage (e.g. `/scratch/$USER/...`).
- CPU-only: No GPU is used. If you ever want GPUs, use the ampere queue and add `--nv`, but that's out of scope here.

## 1) Build & publish the container (GitHub Actions → GHCR)

**Workflow file** (place at `.github/workflows/docker.yml`):

```yaml
name: build-and-push
on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push
        uses: docker/build-push-action@v6
        with:
          context: ./openifs-48r1/scripts/docker/gcc-docker-48r1.1
          file:    ./openifs-48r1/scripts/docker/gcc-docker-48r1.1/Dockerfile
          platforms: linux/amd64
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/openifs:48r1.1
            ghcr.io/${{ github.repository_owner }}/openifs:latest
```

- Run the workflow (GitHub → Actions → "Run workflow").
- After the first successful push, go to GitHub → Profile → Packages → openifs → Package settings and set Visibility = Public (or keep it private and pull with a PAT, see §3B).

## 2) Get the .sif onto CSD3

You have two equally valid paths; pick one.

### A) Pull directly from GHCR (fastest)
```bash
mkdir -p ~/containers && cd ~/containers

# (If you changed package visibility recently, clear any stale auth)
apptainer cache clean -a || true
rm -f ~/.apptainer/docker-config.json ~/.singularity/docker-config.json
unset APPTAINER_DOCKER_USERNAME APPTAINER_DOCKER_PASSWORD
unset SINGULARITY_DOCKER_USERNAME SINGULARITY_DOCKER_PASSWORD

# Pull the published tag
apptainer pull openifs_48r1.1.sif docker://ghcr.io/<your-username>/openifs:48r1.1
```

### B) (Alt) Convert an OCI tarball artifact

If registry pulls are restricted, add these steps after the build in the workflow:

```yaml
- name: Save image as OCI archive
  run: |
    docker pull ghcr.io/${{ github.repository_owner }}/openifs:48r1.1
    docker save ghcr.io/${{ github.repository_owner }}/openifs:48r1.1 -o openifs_48r1.1.tar

- name: Upload OCI tarball
  uses: actions/upload-artifact@v4
  with:
    name: openifs_48r1.1_oci
    path: openifs_48r1.1.tar
```

Then download the artifact locally and copy to CSD3:

```bash
scp openifs_48r1.1.tar <you>@login-icelake.hpc.cam.ac.uk:~/containers/
cd ~/containers
apptainer build openifs_48r1.1.sif oci-archive://openifs_48r1.1.tar
```

## 3) Build OpenIFS on CSD3

### Architecture Configuration

The container approach uses a custom architecture configuration located at:
`openifs-48r1/arch/container/csd3/gnu/11.2.0/`

This configuration:
- Sets up the containerized build environment with GNU Fortran 11.2.0
- Configures MPI compilers (`mpicc`, `mpicxx`, `mpifort`) from `/usr/local/bin/`
- Sets library paths for NetCDF, HDF5, BLAS/LAPACK in standard container locations
- Includes necessary Fortran flags (`-fallow-argument-mismatch` for GNU 11.x compatibility)

### Build Process

1. **Configure the build environment:**
   ```bash
   cd /path/to/openifs-48r1
   # Edit configuration to use container architecture
   export OIFS_HOST="container"
   export OIFS_PLATFORM="csd3"
   export OIFS_ARCH="./arch/${OIFS_HOST}/${OIFS_PLATFORM}/gnu/11.2.0"
   source ./oifs-config.edit_me.sh
   ```

2. **Run the automated build script:**
   ```bash
   cd /path/to/openifs
   ./build_openifs_container.sh
   ```

The build script automatically:
- Sets up the environment variables
- Runs the configure step inside the container
- Builds both single precision (SP) and double precision (DP) executables
- Creates the following executables:
  - `build/bin/ifsMASTER.DP` - Main OpenIFS model (double precision)
  - `build/bin/ifsMASTER.SP` - Main OpenIFS model (single precision)
  - `build/bin/MASTER_scm.DP` - Single Column Model (double precision)
  - `build/bin/MASTER_scm.SP` - Single Column Model (single precision)

### Manual Build (Alternative)

If you prefer manual control:

```bash
cd /path/to/openifs-48r1

# Configure
apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
    /path/to/containers/openifs_48r1.1.sif \
    bash -c "cd $(pwd) && source ./oifs-config.edit_me.sh && ./scripts/build_test/openifs-test.sh -c"

# Build
apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
    /path/to/containers/openifs_48r1.1.sif \
    bash -c "cd $(pwd) && source ./oifs-config.edit_me.sh && ./scripts/build_test/openifs-test.sh -b -j 8"
```

## 4) Running OpenIFS

### Basic Usage

```bash
# Source the OpenIFS environment
source /path/to/openifs-48r1/oifs-config.edit_me.sh

# Run inside the container
apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
    /path/to/containers/openifs_48r1.1.sif \
    /path/to/openifs-48r1/build/bin/ifsMASTER.DP [options]
```

### Single Column Model

```bash
# Run SCM
apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
    /path/to/containers/openifs_48r1.1.sif \
    /path/to/openifs-48r1/build/bin/MASTER_scm.DP [options]
```

## 5) Key Advantages of Container Approach

✅ **Reproducible Environment:** Same toolchain across different systems  
✅ **No Module Conflicts:** Isolated from system dependencies  
✅ **Portable:** Container can be shared and used on other HPC systems  
✅ **Version Controlled:** Container images are versioned and stored in GHCR  
✅ **CI/CD Ready:** Automated builds via GitHub Actions  
✅ **Dependency Management:** All scientific libraries pre-installed and tested  

## 6) Container Contents

The container includes:
- **Base:** Debian 11 (bullseye)
- **Compilers:** GNU GCC/GFortran 11.2.0
- **MPI:** OpenMPI with full Fortran support
- **Scientific Libraries:**
  - NetCDF C and Fortran (latest stable)
  - HDF5 (parallel support)
  - BLAS/LAPACK (optimized)
  - CMake 3.21+
- **Build Tools:** Git, Make, pkg-config
- **Python Environment:** Python 3.9 with scientific packages

## 7) Troubleshooting

### Common Issues

1. **Architecture not found:**
   - Ensure `OIFS_ARCH` points to `./arch/container/csd3/gnu/11.2.0`
   - Check that the symlink in `source/arch` points to the correct location

2. **Compiler not found:**
   - Verify container has `/usr/local/bin/mpicc`, `/usr/local/bin/mpifort`
   - Check that architecture files use full paths to compilers

3. **Library linking errors:**
   - Ensure NetCDF, HDF5 paths are correctly set in `final.cmake`
   - Verify pkg-config can find the libraries inside the container

### Verification Commands

```bash
# Check container contents
apptainer exec /path/to/containers/openifs_48r1.1.sif which mpifort
apptainer exec /path/to/containers/openifs_48r1.1.sif pkg-config --list-all | grep netcdf

# Test build environment
apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
    /path/to/containers/openifs_48r1.1.sif \
    bash -c "cd /path/to/openifs-48r1 && source ./arch/container/csd3/gnu/11.2.0/env.sh"
```

## 8) File Structure

```
openifs-48r1/
├── arch/container/csd3/gnu/11.2.0/
│   ├── env.sh              # Environment setup for container
│   ├── final.cmake         # CMake configuration for container
│   └── modulefile.in       # Module file template
├── build/
│   └── bin/
│       ├── ifsMASTER.DP    # Main model executable
│       ├── ifsMASTER.SP    # Single precision executable
│       ├── MASTER_scm.DP   # SCM executable
│       └── MASTER_scm.SP   # SCM single precision
├── oifs-config.edit_me.sh  # Main configuration file
└── scripts/build_test/
    └── openifs-test.sh     # Official build script

containers/
└── openifs_48r1.1.sif     # Apptainer container

build_openifs_container.sh # Automated build script
```

---

**Success Indicators:**
- ✅ Container builds and publishes to GHCR
- ✅ Apptainer can pull/convert the container on CSD3
- ✅ OpenIFS builds successfully inside the container
- ✅ Executables are created in `build/bin/`
- ✅ Basic executable test runs without immediate crash

**Next Steps:** Configure OpenIFS experiments, input data, and run atmospheric simulations or SCM cases for your research.