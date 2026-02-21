#!/bin/bash

# Build script for Cognito WASM version
# Usage: ./build.sh

echo "Building Cognito for Web (WASM)..."

# Create a clean build source directory
rm -rf web_build_src
mkdir -p web_build_src

# Copy necessary files
echo "Copying files..."
cp main.py web_build_src/
cp requirements.txt web_build_src/
cp neodgm_code.ttf web_build_src/
if [ -d "sounds" ]; then
    cp -r sounds web_build_src/
fi

# Run pygbag build
# We use --disable-sound-format-error because we are using WAV files
# which pygbag complains about (preferring OGG), but they work in most contexts.
echo "Running pygbag..."
pygbag --build --disable-sound-format-error web_build_src

# Move build artifacts to ./web_build
echo "Finalizing build..."
rm -rf web_build
if [ -d "web_build_src/build/web" ]; then
    mv web_build_src/build/web web_build
    echo "Build successful! Artifacts are in ./web_build/"
else
    echo "Build failed! Check output."
    exit 1
fi

# Cleanup
rm -rf web_build_src

echo "Done."
