from flask import Flask, Response, send_from_directory
import os
import subprocess

app = Flask(__name__)

# HLS storage directory
HLS_DIR = "/app/hls/"
os.makedirs(HLS_DIR, exist_ok=True)

# Load and clean M3U file
def load_playlist():
    with open("playlist.m3u", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

# Parse M3U file and restream channels
def parse_m3u(lines):
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf_line = lines[i].strip()
            
            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                original_url = lines[i + 1].strip()
                hls_url = restream_to_hls(original_url)
                if hls_url:
                    channels.append(f"{extinf_line}\n{hls_url}")
            else:
                print(f"⚠️ Skipping: {extinf_line} (No valid URL found)")
        
        i += 1
    return channels

# Function to restream using FFmpeg
def restream_to_hls(source_url):
    stream_name = source_url.split("/")[-1].split("?")[0].replace(".", "_")
    hls_path = os.path.join(HLS_DIR, f"{stream_name}.m3u8")
    hls_url = f"https://{os.getenv('KOYEB_PUBLIC_DOMAIN')}/hls/{stream_name}.m3u8"

    # Start FFmpeg process
    cmd = [
        "ffmpeg", "-i", source_url,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "hls", "-hls_time", "6", "-hls_list_size", "10",
        "-hls_flags", "delete_segments", hls_path
    ]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return hls_url

# Serve the new M3U playlist
@app.route("/playlist")
def serve_playlist():
    lines = load_playlist()
    channels = parse_m3u(lines)
    return Response("#EXTM3U\n" + "\n".join(channels), mimetype="text/plain")

# Serve HLS streams
@app.route("/hls/<path:filename>")
def serve_hls(filename):
    return send_from_directory(HLS_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
