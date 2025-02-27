import os
import subprocess
import time
from flask import Flask, Response

app = Flask(__name__)

# 🔹 Directories & Paths
HLS_DIR = "/workspace/hls"
FFMPEG_PATH = "/workspace/ffmpeg"
FFMPEG_URL = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
PLAYLIST_FILE = "playlist.m3u"

# 🔹 Ensure HLS directory exists
os.makedirs(HLS_DIR, exist_ok=True)

# 🔹 FFmpeg Setup
def setup_ffmpeg():
    if os.path.exists(FFMPEG_PATH):
        print("✅ FFmpeg already installed.")
        return

    print("⏳ Downloading & Installing FFmpeg...")
    subprocess.run(["wget", "-O", "ffmpeg.tar.xz", FFMPEG_URL], check=True)
    subprocess.run(["tar", "xf", "ffmpeg.tar.xz"], check=True)

    ffmpeg_folder = next((d for d in os.listdir() if d.startswith("ffmpeg-") and os.path.isdir(d)), None)
    if not ffmpeg_folder:
        raise FileNotFoundError("⚠️ FFmpeg folder not found!")

    subprocess.run(["mv", os.path.join(ffmpeg_folder, "ffmpeg"), FFMPEG_PATH], check=True)
    subprocess.run(["chmod", "+x", FFMPEG_PATH], check=True)
    print("✅ FFmpeg Installed Successfully!")

setup_ffmpeg()

# 🔹 Load & Parse Playlist
def load_playlist():
    with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def parse_m3u(lines):
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i]
            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                url = lines[i + 1]
                stream_url = restream_channel(url)
                if stream_url:
                    channels.append(f"{extinf}\n{stream_url}")
        i += 1
    return channels

# 🔹 Restream Channel with FFmpeg
def restream_channel(url):
    stream_id = hash(url) % 1000000
    hls_output = f"{HLS_DIR}/channel_{stream_id}.m3u8"

    # 🔹 Run FFmpeg in the background
    ffmpeg_cmd = [
        FFMPEG_PATH, "-i", url, "-c:v", "libx264", "-preset", "veryfast", "-b:v", "1200k",
        "-c:a", "aac", "-b:a", "128k", "-f", "hls", "-hls_time", "6", "-hls_list_size", "5",
        "-hls_flags", "delete_segments", hls_output
    ]

    subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)  # Let FFmpeg start

    # Return the public HLS stream URL
    return f"https://{os.getenv('KOYEB_PUBLIC_DOMAIN')}/hls/channel_{stream_id}.m3u8"

# 🔹 Generate & Serve New M3U Playlist
@app.route("/")
def home():
    return "✅ IPTV Backend Running!"

@app.route("/playlist")
def serve_playlist():
    lines = load_playlist()
    channels = parse_m3u(lines)
    m3u_data = "#EXTM3U\n" + "\n".join(channels)
    return Response(m3u_data, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
