from flask import Flask, request, send_file, jsonify
from PIL import Image
import piexif
import io

app = Flask(__name__)

@app.route('/exif', methods=['POST'])
def add_exif():
    # Check if file was sent
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image = request.files['image']
    data = request.form

    # Load image into memory
    img = Image.open(image)

    # Create EXIF data
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    exif_dict["0th"][piexif.ImageIFD.Artist] = data.get("Artist", "").encode()
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = data.get("ImageDescription", "").encode()
    exif_dict["0th"][piexif.ImageIFD.Software] = data.get("Software", "").encode()
    exif_dict["0th"][piexif.ImageIFD.Copyright] = data.get("Copyright", "").encode()
    exif_dict["0th"][piexif.ImageIFD.XPTitle] = data.get("Title", "").encode('utf-16le')

    # Inject EXIF and return image
    exif_bytes = piexif.dump(exif_dict)
    output = io.BytesIO()
    img.save(output, format="JPEG", exif=exif_bytes)
    output.seek(0)

    return send_file(output, mimetype='image/jpeg', download_name='exif-image.jpg')
