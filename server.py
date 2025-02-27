from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Check if FFmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

@app.route("/")
def home():
    return "✅ Flask Restream Server is running!"

@app.route("/restream", methods=["POST"])
def restream():
    data = request.json
    input_url = data.get("source")
    output_url = "rtmp://your-restream-server/live"

    if not input_url:
        return jsonify({"error": "No source URL provided"}), 400

    # FFmpeg restream command
    ffmpeg_command = [
        "ffmpeg", "-i", input_url, "-c:v", "copy", "-c:a", "copy", "-f", "flv", output_url
    ]

    try:
        subprocess.Popen(ffmpeg_command)
        return jsonify({"message": "✅ Restream started!", "output": output_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
