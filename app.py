import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.route('/exif', methods=['POST'])
def add_exif():
    try:
        print("✅ POST /exif hit!")

        # Log form data
        form_data = request.form.to_dict()
        print("📝 Form data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")

        # Log received files
        print("📂 Files received:", list(request.files.keys()))

        if 'image' not in request.files:
            print("❌ 'image' file not found in request.files")
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        print(f"📄 Image filename: {image_file.filename}")
        print(f"📦 Image content type: {image_file.content_type}")

        # Try loading the image to ensure it's valid
        img = Image.open(image_file)
        print(f"🖼️ Image format: {img.format}, size: {img.size}, mode: {img.mode}")

        # Just return the image unmodified for now
        output = io.BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)

        return send_file(output, mimetype='image/jpeg', download_name='exif-image.jpg')

    except Exception as e:
        print("❌ EXCEPTION:", str(e))
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port)
import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.route('/exif', methods=['POST'])
def add_exif():
    try:
        print("✅ POST /exif hit!")

        # Log form data
        form_data = request.form.to_dict()
        print("📝 Form data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")

        # Log received files
        print("📂 Files received:", list(request.files.keys()))

        if 'image' not in request.files:
            print("❌ 'image' file not found in request.files")
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        print(f"📄 Image filename: {image_file.filename}")
        print(f"📦 Image content type: {image_file.content_type}")

        # Try loading the image to ensure it's valid
        img = Image.open(image_file)
        print(f"🖼️ Image format: {img.format}, size: {img.size}, mode: {img.mode}")

        # Just return the image unmodified for now
        output = io.BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)

        return send_file(output, mimetype='image/jpeg', download_name='exif-image.jpg')

    except Exception as e:
        print("❌ EXCEPTION:", str(e))
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port)
