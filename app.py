import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
import piexif
import io
import traceback
import datetime

app = Flask(__name__)
LOG_FILE = "logs.txt"

# Logging helper (file + stdout so Railway deploy logs show everything)
def log(message):
    timestamp = datetime.datetime.utcnow().isoformat()
    line = f"{timestamp} - {message}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    # Railway captures stdout; use ASCII-safe message for console
    safe = message.encode("ascii", "replace").decode("ascii")
    print(f"[exif] {timestamp} - {safe}", flush=True)

@app.route('/exif', methods=['POST'])
def add_exif():
    try:
        log("Received POST /exif")
        log(f"Content-Type: {request.headers.get('Content-Type', '')}")
        log(f"Accept: {request.headers.get('Accept', '')}")

        form_data = request.form.to_dict()
        log(f"Form keys: {list(form_data.keys())}")
        for key, value in form_data.items():
            s = str(value) if value is not None else ""
            log(f"  {key}: {s[:80]}..." if len(s) > 80 else f"  {key}: {s}")

        log(f"File keys: {list(request.files.keys())}")

        image_file = request.files.get("image") or request.files.get("data")
        if not image_file or not (getattr(image_file, "filename", None) or "").strip():
            log("No image file (need form field 'image' or 'data' with filename)")
            return jsonify({"error": "No image file provided. Use form field 'image' or 'data'."}), 400

        log(f"Image filename: {image_file.filename}")
        log(f"Image content-type: {image_file.content_type}")

        img = Image.open(image_file).convert("RGB")
        log(f"Opened image: format={img.format}, size={img.size}, mode={img.mode}")

        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        exif_dict["0th"][piexif.ImageIFD.Artist] = form_data.get("Artist", "").encode()
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = form_data.get("ImageDescription", "").encode()
        exif_dict["0th"][piexif.ImageIFD.Software] = form_data.get("Software", "").encode()
        exif_dict["0th"][piexif.ImageIFD.Copyright] = form_data.get("Copyright", "").encode()
        exif_dict["0th"][piexif.ImageIFD.XPTitle] = form_data.get("Title", "").encode("utf-16le")
        log("EXIF built: Artist, Title, ImageDescription, Software, Copyright")

        exif_bytes = piexif.dump(exif_dict)
        output = io.BytesIO()
        img.save(output, format="JPEG", exif=exif_bytes)
        output.seek(0)
        size = output.getbuffer().nbytes
        log(f"EXIF injected, JPEG size={size} bytes, returning binary file")
        return send_file(output, mimetype="image/jpeg", download_name="exif-image.jpg")

    except Exception as e:
        log(f"EXCEPTION: {e}")
        log(traceback.format_exc())
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return f"Error reading logs: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    log(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
