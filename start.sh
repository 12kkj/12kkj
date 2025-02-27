#!/bin/bash

# Define FFmpeg folder
FFMPEG_DIR="ffmpeg"

# Check if FFmpeg exists
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ FFmpeg not found. Downloading now..."
    wget -O ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    tar -xf ffmpeg.tar.xz
    mv ffmpeg-*-static $FFMPEG_DIR
    rm ffmpeg.tar.xz
    export PATH=$PWD/$FFMPEG_DIR:$PATH
    echo "✅ FFmpeg installed successfully!"
else
    echo "✅ FFmpeg is already installed."
fi

# Export FFmpeg path
export PATH=$PWD/$FFMPEG_DIR:$PATH

# Install Python dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Start Flask server
echo "🚀 Starting Flask Restream Server..."
python3 server.py
