import os
import subprocess
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# 🔹 Directories & Paths
HLS_DIR = "/workspace/hls"
FFMPEG_PATH = "/workspace/ffmpeg"
AFTER_M3U_PATH = "/workspace/after.m3u"
PLAYLIST_URL = "https://your-m3u-source-url.com/playlist.m3u"

# 🔹 Ensure required directories exist
os.makedirs(HLS_DIR, exist_ok=True)

FFMPEG_URL = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"

def setup_ffmpeg():
    if os.path.exists(FFMPEG_PATH):
        print("FFmpeg already installed.")
        return

    print("Downloading FFmpeg...")
    subprocess.run(["wget", "-O", "ffmpeg.tar.xz", FFMPEG_URL], check=True)
    subprocess.run(["tar", "xf", "ffmpeg.tar.xz"], check=True)

    ffmpeg_folder = next((entry for entry in os.listdir() if entry.startswith("ffmpeg-") and os.path.isdir(entry)), None)
    if not ffmpeg_folder:
        raise FileNotFoundError("FFmpeg folder not found after extraction.")

    ffmpeg_binary_path = os.path.join(ffmpeg_folder, "ffmpeg")
    if not os.path.isfile(ffmpeg_binary_path):
        raise FileNotFoundError("FFmpeg binary not found inside extracted folder.")

    subprocess.run(["mv", ffmpeg_binary_path, FFMPEG_PATH], check=True)
    subprocess.run(["chmod", "+x", FFMPEG_PATH], check=True)
    print("FFmpeg setup complete.")

setup_ffmpeg()

# 🔹 Fetch and Parse M3U Playlist
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

# 🔹 Restream Channel to HLS
def restream_to_hls(url, channel_id):
    hls_folder = os.path.join(HLS_DIR, channel_id)
    hls_output = os.path.join(hls_folder, "index.m3u8")

    os.makedirs(hls_folder, exist_ok=True)

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

# 🔹 Generate M3U Playlist & Update after.m3u
@app.route("/playlist", methods=["GET"])
def generate_playlist():
    channels = parse_m3u()
    if not channels:
        return jsonify({"error": "No valid streams found"}), 500

    playlist_content = "#EXTM3U\n"
    hls_links = []

    for i, url in enumerate(channels[:10]):  # Limit to 10 channels
        hls_url = restream_to_hls(url, f"channel_{i}")
        if hls_url:
            entry = f"#EXTINF:-1,Channel {i+1}\n{hls_url}"
            playlist_content += entry + "\n"
            hls_links.append(entry)

    # 🔹 Update after.m3u with the new playlist
    with open(AFTER_M3U_PATH, "w") as after_m3u:
        after_m3u.write("#EXTM3U\n" + "\n".join(hls_links))

    return playlist_content, 200, {"Content-Type": "application/x-mpegURL"}

# 🔹 Health Check Route
@app.route("/", methods=["GET"])
def health_check():
    return "Server is running!", 200

# 🔹 Run Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
