from flask import Flask, Response
import subprocess

app = Flask(__name__)

# FFmpeg command to restream the given URL
def restream_channel(url):
    command = [
        "ffmpeg",
        "-i", url,            # Input URL from the playlist
        "-c:v", "copy",       # Copy video codec
        "-c:a", "copy",       # Copy audio codec
        "-f", "mpegts",       # Output format
        "pipe:1"              # Output to the response
    ]
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

# Serve a single channel as an HLS stream
@app.route("/stream/<path:url>")
def stream(url):
    process = restream_channel(url)
    return Response(process.stdout, mimetype="video/mp2t")

@app.route("/")
def home():
    return "IPTV Restreaming Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
