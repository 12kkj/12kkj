import os
import subprocess
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# 🔹 Directory to store HLS streams
HLS_DIR = "/workspace/hls"
FFMPEG_PATH = "/workspace/ffmpeg"
PLAYLIST_URL = "https://your-m3u-source-url.com/playlist.m3u"

# 🔹 Ensure HLS directory exists
os.makedirs(HLS_DIR, exist_ok=True)

# 🔹 Download & setup FFmpeg
def setup_ffmpeg():
    if not os.path.exists(FFMPEG_PATH):
        print("Downloading FFmpeg...")
        ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
        subprocess.run(["wget", "-O", "ffmpeg.tar.xz", ffmpeg_url], check=True)
        subprocess.run(["tar", "xf", "ffmpeg.tar.xz"], check=True)
        subprocess.run(["mv", "ffmpeg-*/ffmpeg", FFMPEG_PATH], check=True)
        subprocess.run(["chmod", "+x", FFMPEG_PATH], check=True)
        print("FFmpeg installed!")

setup_ffmpeg()

# 🔹 Function to process M3U playlist
def parse_m3u():
    try:
        response = requests.get(PLAYLIST_URL, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()
        streams = [line for line in lines if line.startswith("http")]
        return streams
    except requests.RequestException as e:
        print(f"Error fetching playlist: {e}")
        return []

# 🔹 Function to restream channel to HLS
def restream_to_hls(url, channel_id):
    hls_output = f"{HLS_DIR}/{channel_id}/index.m3u8"
    os.makedirs(f"{HLS_DIR}/{channel_id}", exist_ok=True)

    cmd = [
        FFMPEG_PATH, "-i", url, "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-f", "hls", "-hls_time", "5", "-hls_list_size", "10", "-hls_flags",
        "delete_segments", hls_output
    ]

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"/hls/{channel_id}/index.m3u8"
    except Exception as e:
        print(f"Error restreaming {url}: {e}")
        return None

# 🔹 Flask Route to generate M3U playlist
@app.route("/playlist", methods=["GET"])
def generate_playlist():
    channels = parse_m3u()
    if not channels:
        return jsonify({"error": "No valid streams found"}), 500

    playlist_content = "#EXTM3U\n"
    for i, url in enumerate(channels[:10]):  # Limit to 10 channels
        hls_url = restream_to_hls(url, f"channel_{i}")
        if hls_url:
            playlist_content += f"#EXTINF:-1,Channel {i+1}\n{hls_url}\n"

    return playlist_content, 200, {"Content-Type": "application/x-mpegURL"}

# 🔹 Health Check Route
@app.route("/", methods=["GET"])
def health_check():
    return "Server is running!", 200

# 🔹 Run Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
