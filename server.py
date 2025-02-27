import os
import subprocess
import time
from flask import Flask, jsonify, send_file

app = Flask(__name__)

# HLS output folder
HLS_DIR = "hls"
os.makedirs(HLS_DIR, exist_ok=True)

# Sample playlist (replace with actual M3U file reading)
PLAYLIST = {
    "channel1": "http://example.com/stream1.m3u8",
    "channel2": "http://example.com/stream2.m3u8"
}

# Store active FFmpeg processes
ffmpeg_processes = {}

def start_ffmpeg(channel_name, channel_url):
    """ Start FFmpeg process to restream IPTV channel to HLS """
    output_dir = os.path.join(HLS_DIR, channel_name)
    os.makedirs(output_dir, exist_ok=True)

    output_hls = os.path.join(output_dir, "index.m3u8")

    command = [
        "ffmpeg", "-i", channel_url, "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-strict", "experimental", "-f", "hls",
        "-hls_time", "5", "-hls_list_size", "5", "-hls_flags", "delete_segments",
        "-start_number", "1", output_hls
    ]

    # Stop previous FFmpeg process for this channel (if exists)
    if channel_name in ffmpeg_processes:
        ffmpeg_processes[channel_name].terminate()
        ffmpeg_processes[channel_name].wait()
    
    # Start new FFmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ffmpeg_processes[channel_name] = process

    # Log errors if any
    time.sleep(2)
    stdout, stderr = process.communicate()
    if stderr:
        print(f"FFmpeg Error [{channel_name}]:", stderr.decode())

@app.route("/")
def home():
    return jsonify({"message": "IPTV Restreaming Server Running"})

@app.route("/playlist.m3u")
def get_playlist():
    """ Generate an updated M3U playlist with HLS links """
    playlist_content = "#EXTM3U\n"
    for channel, url in PLAYLIST.items():
        hls_url = f"http://localhost:5000/hls/{channel}/index.m3u8"
        playlist_content += f"#EXTINF:-1,{channel}\n{hls_url}\n"
        start_ffmpeg(channel, url)
    
    playlist_path = os.path.join(HLS_DIR, "playlist.m3u")
    with open(playlist_path, "w") as f:
        f.write(playlist_content)
    
    return send_file(playlist_path, mimetype="application/x-mpegURL")

@app.route("/hls/<channel>/index.m3u8")
def get_hls(channel):
    """ Serve HLS playlist for a specific channel """
    hls_file = os.path.join(HLS_DIR, channel, "index.m3u8")
    if os.path.exists(hls_file):
        return send_file(hls_file, mimetype="application/x-mpegURL")
    return jsonify({"error": "Channel not found"}), 404

@app.route("/stop/<channel>")
def stop_channel(channel):
    """ Stop FFmpeg for a specific channel """
    if channel in ffmpeg_processes:
        ffmpeg_processes[channel].terminate()
        ffmpeg_processes[channel].wait()
        del ffmpeg_processes[channel]
        return jsonify({"message": f"Stopped {channel}"})
    return jsonify({"error": "Channel not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
