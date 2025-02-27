from flask import Flask, Response, send_file
import os
import subprocess

app = Flask(__name__)

# Path to the original playlist file
PLAYLIST_FILE = "playlist.m3u"

# Path to the generated playlist with restreamed links
OUTPUT_PLAYLIST = "after.m3u"

# HLS output directory
HLS_DIR = "hls"
os.makedirs(HLS_DIR, exist_ok=True)


def load_playlist():
    """Load and clean the M3U file from disk."""
    if not os.path.exists(PLAYLIST_FILE):
        return []
    with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # Remove blank lines
    return lines


def parse_m3u(lines):
    """Parse the M3U file and extract channels with URLs."""
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf_line = lines[i].strip()

            if i + 1 < len(lines) and not lines[i + 1].startswith("#EXTINF"):
                original_url = lines[i + 1].strip()
                stream_id = f"channel_{i//2}"
                hls_output = f"{HLS_DIR}/{stream_id}.m3u8"

                # Start FFmpeg restreaming
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-i", original_url,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-f", "hls",
                    "-hls_time", "10",
                    "-hls_list_size", "5",
                    "-hls_flags", "delete_segments",
                    hls_output
                ]
                subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Create the new entry with the restreamed link
                restreamed_url = f"{request.host_url}hls/{stream_id}.m3u8"
                channels.append(f"{extinf_line}\n{restreamed_url}")

        i += 1
    return channels


@app.route("/")
def home():
    return "IPTV Restreaming Server is Running!"


@app.route("/playlist")
def serve_playlist():
    """Serve the dynamically generated playlist."""
    lines = load_playlist()
    channels = parse_m3u(lines)

    # Save the new playlist
    with open(OUTPUT_PLAYLIST, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join(channels))

    return Response("#EXTM3U\n" + "\n".join(channels), mimetype="text/plain")


@app.route("/hls/<path:filename>")
def serve_hls(filename):
    """Serve HLS .m3u8 files."""
    hls_path = os.path.join(HLS_DIR, filename)
    if os.path.exists(hls_path):
        return send_file(hls_path)
    return "File not found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
