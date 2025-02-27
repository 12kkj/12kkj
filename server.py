from flask import Flask, Response
import os
import subprocess

app = Flask(__name__)

# Load M3U/M3U8 playlist from file
def load_playlist():
    filepath = "playlist.m3u"
    if not os.path.exists(filepath):
        print(f"❌ Error: {filepath} not found!")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

# Parse M3U file and extract channel names & URLs
def parse_m3u(lines):
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf_line = lines[i]
            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                url = lines[i + 1]
                hls_url = restream_to_hls(url)  # Convert to HLS
                channels.append(f"{extinf_line}\n{hls_url}")
        i += 1
    return channels

# Convert IPTV source to HLS using FFmpeg
def restream_to_hls(input_url):
    hls_output = f"http://{os.getenv('KOYEB_PUBLIC_DOMAIN')}/hls/{hash(input_url)}.m3u8"
    hls_path = f"/app/hls/{hash(input_url)}.m3u8"

    ffmpeg_command = [
        "ffmpeg", "-i", input_url, "-c:v", "libx264", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k", "-f", "hls", "-hls_time", "10",
        "-hls_list_size", "5", "-hls_flags", "delete_segments", hls_path
    ]

    # Run FFmpeg in background
    subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return hls_output

# Generate the final M3U playlist
def generate_m3u(channels):
    return "#EXTM3U\n" + "\n".join(channels)

@app.route("/")
def home():
    return "✅ IPTV Backend is Running!"

@app.route("/playlist")
def serve_playlist():
    lines = load_playlist()
    channels = parse_m3u(lines)
    return Response(generate_m3u(channels), mimetype="text/plain")

if __name__ == "__main__":
    os.makedirs("/app/hls", exist_ok=True)  # Create HLS folder if not exists
    app.run(host="0.0.0.0", port=5000)
