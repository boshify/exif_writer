import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
import io
import traceback
import datetime

app = Flask(__name__)

LOG_FILE = "logs.txt"

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.utcnow().isoformat()} - {message}\n")

@app.route('/exif', methods=['POST'])
def add_exif():
    try:
        log("✅ Received POST /exif")

        # Log form fields
        form_data = request.form.to_dict()
        log("📝 Form data:")
        for key, value in form_data.items():
            log(f"  {key}: {value}")

        # Log file keys
        log(f"📂 Files received: {list(request.files.keys())}")

        if 'image' not in request.files:
            log("❌ No image file found in request")
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        log(f"📄 Image filename: {image_file.filename}")
        log(f"📦 Image content type: {image_file.content_type}")

        # Load and save the image
        img = Image.open(image_file)
        log(f"🖼️ Image format: {img.format}, size: {img.size}, mode: {img.mode}")

        output = io.BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)

        return send_file(output, mimetype='image/jpeg', download_name='exif-image.jpg')

    except Exception as e:
        log("❌ EXCEPTION:")
        log(traceback.format_exc())
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, "r") as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Error reading logs: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    log(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
