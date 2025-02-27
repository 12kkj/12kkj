from flask import Flask, Response

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
                url = lines[i + 1].strip()
                channels.append(f"{extinf_line}\n{url}")
            else:
                print(f"⚠️ Skipping: {extinf_line} (No valid URL found)")
        
        i += 1
    return channels

# Generate a valid M3U playlist
def generate_m3u(channels):
    return "#EXTM3U\n" + "\n".join(channels)

@app.route("/")
def home():
    return "IPTV Backend is Running!"

@app.route("/playlist")
def serve_playlist():
    lines = load_playlist()
    channels = parse_m3u(lines)

    

    return Response(generate_m3u(channels), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
