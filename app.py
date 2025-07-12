import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
import piexif
import io
import traceback
import datetime

app = Flask(__name__)
LOG_FILE = "logs.txt"

# Logging helper
def log(message):
    timestamp = datetime.datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")

@app.route('/exif', methods=['POST'])
def add_exif():
    try:
        log("✅ Received POST /exif")

        # Log form data
        form_data = request.form.to_dict()
        log("📝 Form data:")
        for key, value in form_data.items():
            log(f"  {key}: {value}")

        # Log file keys
        log(f"📂 Files received: {list(request.files.keys())}")

        if 'image' not in request.files:
            log("❌ No 'image' file found in request.files")
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        log(f"📄 Image filename: {image_file.filename}")
        log(f"📦 Image content type: {image_file.content_type}")

        # Open and convert to RGB if needed (PNG etc.)
        img = Image.open(image_file).convert("RGB")
        log(f"🖼️ Image format: {img.format}, size: {img.size}, mode: {img.mode}")

        # Build EXIF metadata
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        exif_dict["0th"][piexif.ImageIFD.Artist] = form_data.get("Artist", "").encode()
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = form_data.get("ImageDescription", "").encode()
        exif_dict["0th"][piexif.ImageIFD.Software] = form_data.get("Software", "").encode()
        exif_dict["0th"][piexif.ImageIFD.Copyright] = form_data.get("Copyright", "").encode()
        exif_dict["0th"][piexif.ImageIFD.XPTitle] = form_data.get("Title", "").encode('utf-16le')

        # Inject EXIF
        exif_bytes = piexif.dump(exif_dict)
        output = io.BytesIO()
        img.save(output, format="JPEG", exif=exif_bytes)
        output.seek(0)

        log("✅ EXIF embedded and image returned successfully")
        return send_file(output, mimetype='image/jpeg', download_name='exif-image.jpg')

    except Exception as e:
        log("❌ EXCEPTION:")
        log(traceback.format_exc())
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return f"Error reading logs: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    log(f"🚀 Starting server on port {port}")
    app.run(host="0.0.0.0", port=port)
