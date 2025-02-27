from flask import Flask, Response, request
import subprocess
import re

app = Flask(__name__)

# Load and clean M3U file from disk
def load_playlist():
    with open("playlist.m3u", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # Remove blank lines
    return lines

# Parse M3U file and extract channels with URLs
def parse_m3u(lines):
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf_line = lines[i].strip()

            # Ensure there is a next line (URL) and it's not another #EXTINF
            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                original_url = lines[i + 1].strip()
                
                # Generate a restreamed URL through our Flask proxy
                restream_url = f"https://{request.host}/stream?url={original_url}"
                
                channels.append(f"{extinf_line}\n{restream_url}")
            else:
                print(f"⚠️ Skipping: {extinf_line} (No valid URL found)")
        
        i += 1
    return channels

# Generate an updated M3U playlist
def generate_m3u(channels):
    return "#EXTM3U\n" + "\n".join(channels)

# Route to generate restreamed playlist
@app.route("/playlist")
def serve_playlist():
    lines = load_playlist()
    channels = parse_m3u(lines)
    return Response(generate_m3u(channels), mimetype="text/plain")

# FFmpeg-powered restreaming
@app.route("/stream")
def restream():
    original_url = request.args.get("url")
    if not original_url:
        return "Error: No URL provided", 400

    # Start FFmpeg process for restreaming
    ffmpeg_command = [
        "ffmpeg", "-i", original_url, "-c:v", "copy", "-c:a", "aac",
        "-f", "hls", "-hls_time", "5", "-hls_list_size", "10", "pipe:1"
    ]
    
    return Response(subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout, mimetype="application/vnd.apple.mpegurl")

@app.route("/")
def home():
    return "IPTV Restreaming Backend is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
