from flask import Flask, Response
import subprocess

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
            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                original_url = lines[i + 1].strip()
                new_url = f"https://nutty-heda-kkkjj-65a305de.koyeb.app/stream/{i}"  # Generate new stream URL
                channels.append(f"{extinf_line}\n{new_url}")
        i += 1
    return channels

# FFmpeg restream function
def restream_channel(channel_id):
    lines = load_playlist()
    channels = parse_m3u(lines)
    
    # Find the original URL for the given channel_id
    original_urls = [line.split("\n")[1] for line in channels if "\n" in line]
    if channel_id >= len(original_urls):
        return "Invalid Channel ID", 404
    
    original_url = original_urls[channel_id]

    command = [
        "ffmpeg",
        "-i", original_url,  # Input original stream
        "-c:v", "copy",       # Copy video codec
        "-c:a", "copy",       # Copy audio codec
        "-f", "mpegts",       # Output format
        "pipe:1"              # Send to response
    ]
    
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

# Serve a single channel as a restreamed stream
@app.route("/stream/<int:channel_id>")
def stream(channel_id):
    process = restream_channel(channel_id)
    return Response(process.stdout, mimetype="video/mp2t")

# Serve the new playlist with updated URLs
@app.route("/after.m3u")
def serve_after_m3u():
    lines = load_playlist()
    channels = parse_m3u(lines)
    return Response("#EXTM3U\n" + "\n".join(channels), mimetype="text/plain")

@app.route("/")
def home():
    return "IPTV Restreaming Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
