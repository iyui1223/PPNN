#!/bin/bash
#
# Build script for OpenIFS using Apptainer container
# 
# Usage: ./build_openifs_container.sh
#

set -e  # Exit on error

# Configuration
CONTAINER_PATH="/home/yi260/rds/hpc-work/containers/openifs_48r1.1.sif"
OPENIFS_ROOT="/home/yi260/rds/hpc-work/openifs/openifs-48r1"
BUILD_THREADS=8

echo "=================================================="
echo "OpenIFS Container Build Script"
echo "=================================================="
echo "Container: $CONTAINER_PATH"
echo "OpenIFS Root: $OPENIFS_ROOT"
echo "Build Threads: $BUILD_THREADS"
echo ""

# Check if container exists
if [ ! -f "$CONTAINER_PATH" ]; then
    echo "ERROR: Container not found at $CONTAINER_PATH"
    exit 1
fi

# Check if OpenIFS directory exists
if [ ! -d "$OPENIFS_ROOT" ]; then
    echo "ERROR: OpenIFS directory not found at $OPENIFS_ROOT"
    exit 1
fi

# Change to OpenIFS directory
cd "$OPENIFS_ROOT"

echo "Step 1: Setting up environment..."
# Source the configuration file
source ./oifs-config.edit_me.sh

echo ""
echo "Step 2: Running configure/create step in container..."
# Run the configure step inside the container
apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
    "$CONTAINER_PATH" \
    bash -c "cd $OPENIFS_ROOT && source ./oifs-config.edit_me.sh && ./scripts/build_test/openifs-test.sh -c"

echo ""
echo "Step 3: Running build step in container..."
# Run the build step inside the container
apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
    "$CONTAINER_PATH" \
    bash -c "cd $OPENIFS_ROOT && source ./oifs-config.edit_me.sh && ./scripts/build_test/openifs-test.sh -b -j $BUILD_THREADS"

echo ""
echo "Step 4: Checking build results..."
if [ -f "$OPENIFS_ROOT/build/bin/ifsMASTER.DP" ]; then
    echo "SUCCESS: OpenIFS executable built successfully!"
    echo "Location: $OPENIFS_ROOT/build/bin/ifsMASTER.DP"
    
    # Show file info
    echo ""
    echo "Executable details:"
    ls -la "$OPENIFS_ROOT/build/bin/ifsMASTER.DP"
    
    # Test if it runs (basic check)
    echo ""
    echo "Testing executable (help output):"
    apptainer exec --bind /home/yi260/rds/hpc-work:/home/yi260/rds/hpc-work \
        "$CONTAINER_PATH" \
        "$OPENIFS_ROOT/build/bin/ifsMASTER.DP" --help || echo "Note: Help might not be available, but executable exists"
        
else
    echo "ERROR: Build failed - executable not found"
    echo "Check the log file: $OPENIFS_ROOT/oifs_test_log.txt"
    exit 1
fi

echo ""
echo "=================================================="
echo "Build completed successfully!"
echo ""
echo "To run OpenIFS experiments:"
echo "1. Use the container: apptainer exec $CONTAINER_PATH"
echo "2. Source the config: source $OPENIFS_ROOT/oifs-config.edit_me.sh"
echo "3. Use the executable: $OPENIFS_ROOT/build/bin/ifsMASTER.DP"
echo "=================================================="
