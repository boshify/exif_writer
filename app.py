import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
import piexif
import io

app = Flask(__name__)

@app.route('/exif', methods=['POST'])
def add_exif():
    try:
        print("✅ Received POST request at /exif")

        # Log form data and files for debugging
        print("📝 Form fields:", request.form.to_dict())
        print("📂 Files received:", request.files)

        if 'image' not in request.files:
            print("❌ No image file found in request")
            return jsonify({"error": "No image file provided"}), 400

        image = request.files['image']
        data = request.form

        # Load image into memory
        img = Image.open(image)

        # Build EXIF dictionary
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        exif_dict["0th"][piexif.ImageIFD.Artist] = data.get("Artist", "").encode()
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = data.get("ImageDescription", "").encode()
        exif_dict["0th"][piexif.ImageIFD.Software] = data.get("Software", "").encode()
        exif_dict["0th"][piexif.ImageIFD.Copyright] = data.get("Copyright", "").encode()
        exif_dict["0th"][piexif.ImageIFD.XPTitle] = data.get("Title", "").encode('utf-16le')

        # Inject EXIF into image
        exif_bytes = piexif.dump(exif_dict)
        output = io.BytesIO()
        img.save(output, format="JPEG", exif=exif_bytes)
        output.seek(0)

        print("✅ EXIF data written and image processed successfully")

        return send_file(output, mimetype='image/jpeg', download_name='exif-image.jpg')

    except Exception as e:
        print("❌ Exception occurred:", str(e))
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting EXIF service on port {port}")
    app.run(host="0.0.0.0", port=port)
