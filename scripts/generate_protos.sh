#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

echo "Compiling Protobufs..."

# Ensure we are in the root 'aerolock' directory
if [ ! -d "proto" ] || [ ! -d "shared" ]; then
  echo "Error: Please run this script from the root aerolock/ directory."
  exit 1
fi

# Create the target directory and __init__.py if they don't exist
mkdir -p shared/aerolock_common/generated
touch shared/aerolock_common/generated/__init__.py

# Run the protoc compiler (using the poetry env from the shared folder)
cd shared
poetry run python -m grpc_tools.protoc \
    -I ../proto/ \
    --python_out=./aerolock_common/generated \
    --pyi_out=./aerolock_common/generated \
    --grpc_python_out=./aerolock_common/generated \
    ../proto/*.proto

# Fix the broken relative imports in the generated Python files (Standard Python gRPC workaround)
sed -i -E 's/^import ([a-zA-Z0-9_]+_pb2) as ([a-zA-Z0-9_]+__pb2)$/from . import \1 as \2/' aerolock_common/generated/*_pb2.py
sed -i -E 's/^import.*_pb2/from . \0/' aerolock_common/generated/*_pb2_grpc.py

echo "✅ Protobufs compiled successfully!"