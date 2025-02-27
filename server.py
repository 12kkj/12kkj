from flask import Flask, Response, request, jsonify, send_file
import subprocess
import os

app = Flask(__name__)

# Directory for storing HLS output
HLS_OUTPUT_FOLDER = "hls_output"
os.makedirs(HLS_OUTPUT_FOLDER, exist_ok=True)

# Store active streams
active_streams = {}

# Function to start FFmpeg HLS restreaming
def start_ffmpeg(channel_name, channel_url):
    output_hls = f"{HLS_OUTPUT_FOLDER}/{channel_name}.m3u8"

    # Check if the stream is already running
    if channel_name in active_streams:
        return output_hls

    command = [
        "ffmpeg", "-i", channel_url, "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-strict", "experimental", "-f", "hls",
        "-hls_time", "5", "-hls_list_size", "5", "-hls_flags", "delete_segments",
        "-start_number", "1", output_hls
    ]

    # Start the process and store reference
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    active_streams[channel_name] = process

    return output_hls

# Load and parse the original M3U playlist
def load_playlist():
    playlist_path = "playlist.m3u"
    if not os.path.exists(playlist_path):
        return []

    with open(playlist_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

# Convert original M3U to new M3U with permanent HLS links
def generate_m3u():
    lines = load_playlist()
    new_channels = []
    i = 0

    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf_line = lines[i]

            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                original_url = lines[i + 1].strip()
                channel_name = f"channel{i//2}"

                # Start FFmpeg restream for each channel
                start_ffmpeg(channel_name, original_url)

                # Create new permanent streaming URL
                new_url = f"https://{request.host}/hls/{channel_name}.m3u8"
                new_channels.append(f"{extinf_line}\n{new_url}")

        i += 1

    return "#EXTM3U\n" + "\n".join(new_channels)

# Routes
@app.route("/")
def home():
    return "IPTV HLS Restreaming Service is Running!"

@app.route("/playlist")
def serve_playlist():
    return Response(generate_m3u(), mimetype="text/plain")

@app.route("/hls/<channel_name>.m3u8")
def serve_hls(channel_name):
    hls_path = f"{HLS_OUTPUT_FOLDER}/{channel_name}.m3u8"
    if os.path.exists(hls_path):
        return send_file(hls_path, mimetype="application/vnd.apple.mpegurl")
    return "Channel not found", 404

@app.route("/start_stream/<channel_name>/<path:channel_url>")
def start_stream(channel_name, channel_url):
    output_hls = start_ffmpeg(channel_name, channel_url)
    return jsonify({"message": "Streaming started", "url": f"https://{request.host}/hls/{channel_name}.m3u8"})

@app.route("/stop_stream/<channel_name>")
def stop_stream(channel_name):
    if channel_name in active_streams:
        active_streams[channel_name].terminate()
        del active_streams[channel_name]
        return jsonify({"message": f"Stream {channel_name} stopped."})
    return jsonify({"error": "Stream not found."}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
