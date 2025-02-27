import os
import subprocess
from flask import Flask, jsonify, request

app = Flask(__name__)

# Function to download FFmpeg if not available
def install_ffmpeg():
    if not os.path.exists("ffmpeg"):
        print("Downloading FFmpeg...")
        os.system("curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz -o ffmpeg.tar.xz")
        os.system("tar -xf ffmpeg.tar.xz --strip-components=1 --wildcards '*/ffmpeg'")
        os.system("rm -f ffmpeg.tar.xz")
        os.system("chmod +x ffmpeg")
        print("FFmpeg installed!")

# Call FFmpeg installer on startup
install_ffmpeg()

# Function to convert IPTV stream to HLS format
def restream_to_hls(original_url, output_file):
    cmd = [
        "./ffmpeg", "-i", original_url, "-c:v", "copy", "-c:a", "aac",
        "-b:a", "128k", "-f", "hls", "-hls_time", "10", "-hls_list_size", "5", output_file
    ]
    
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_file

# Sample IPTV sources
IPTV_SOURCES = {
    "Channel 1": "http://example.com/stream1.ts",
    "Channel 2": "http://example.com/stream2.m3u8",
    "Channel 3": "http://example.com/stream3.mp4",
}

# API Endpoint to generate M3U playlist
@app.route("/playlist", methods=["GET"])
def generate_playlist():
    playlist_content = "#EXTM3U\n"
    
    for name, url in IPTV_SOURCES.items():
        hls_output = f"{name.replace(' ', '_')}.m3u8"
        restream_to_hls(url, hls_output)
        
        playlist_content += f"#EXTINF:-1,{name}\n"
        playlist_content += f"https://nutty-heda-kkkjj-65a305de.koyeb.app/{hls_output}\n"

    return playlist_content, 200, {'Content-Type': 'text/plain'}

# Serve HLS files
@app.route("/<path:filename>", methods=["GET"])
def serve_hls(filename):
    return f"Serving HLS file: {filename}"

# Run Flask App
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

