"""
Local test for POST /exif: simulates n8n-style form-data with dummy EXIF and an image.
Run with: python test_local.py
Uses Flask test client (no separate server needed). Requires: flask, piexif, pillow, requests.
"""
import base64
import io
import os
import sys

# Run from project directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PIL import Image as PILImage
except ImportError:
    print("Install Pillow: pip install pillow")
    sys.exit(1)

def make_test_image():
    """Create a small PNG in memory (no external URL)."""
    img = PILImage.new("RGB", (100, 100), color=(200, 100, 150))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), "test-image.png"

def main():
    # Import app after path is set; use test client so no server needed
    from app import app
    client = app.test_client()

    print("Creating test image...")
    image_bytes, filename = make_test_image()
    print(f"  Got {len(image_bytes)} bytes ({filename})")

    # Dummy EXIF like n8n would send (form fields)
    form_fields = {
        "Artist": "GTO Wizard",
        "Title": "GTO Chart Sample - UTG Position",
        "ImageDescription": "A sample GTO chart for UTG position.",
        "Software": "Adobe Photoshop",
        "Copyright": "CC BY 4.0",
    }

    # --- Test 1: Binary response (no Accept: application/json, no format=json)
    print("\n--- Test 1: Binary response (field name 'image') ---")
    data1 = dict(form_fields)
    data1["image"] = (io.BytesIO(image_bytes), filename)
    resp = client.post("/exif", data=data1, content_type="multipart/form-data")
    print(f"  Status: {resp.status_code}")
    print(f"  Content-Type: {resp.headers.get('Content-Type')}")
    if resp.status_code == 200:
        out_path = "out_binary.jpg"
        with open(out_path, "wb") as f:
            f.write(resp.data)
        print(f"  Saved to {out_path} ({len(resp.data)} bytes)")
    else:
        print(f"  Body: {resp.get_data(as_text=True)[:500]}")

    # --- Test 2: JSON response (Accept: application/json)
    print("\n--- Test 2: JSON response (Accept: application/json, field name 'data') ---")
    data2 = dict(form_fields)
    data2["data"] = (io.BytesIO(image_bytes), filename)
    resp2 = client.post("/exif", data=data2, content_type="multipart/form-data", headers={"Accept": "application/json"})
    print(f"  Status: {resp2.status_code}")
    print(f"  Content-Type: {resp2.headers.get('Content-Type')}")
    if resp2.status_code == 200:
        import json
        data_json = json.loads(resp2.get_data(as_text=True))
        print(f"  success: {data_json.get('success')}, filename: {data_json.get('filename')}")
        b64 = data_json.get("image_base64", "")
        if b64:
            out_path2 = "out_json.jpg"
            with open(out_path2, "wb") as f:
                f.write(base64.b64decode(b64))
            print(f"  Decoded image saved to {out_path2} ({len(b64)} base64 chars)")
        else:
            print("  No image_base64 in response")
    else:
        print(f"  Body: {resp2.get_data(as_text=True)[:500]}")

    # --- Test 3: JSON via ?format=json
    print("\n--- Test 3: JSON via ?format=json ---")
    data3 = dict(form_fields)
    data3["image"] = (io.BytesIO(image_bytes), filename)
    resp3 = client.post("/exif?format=json", data=data3, content_type="multipart/form-data")
    print(f"  Status: {resp3.status_code}")
    if resp3.status_code == 200 and "application/json" in (resp3.headers.get("Content-Type") or ""):
        print("  OK: got JSON response")
    else:
        print(f"  Body: {resp3.get_data(as_text=True)[:200]}")

    print("\nDone. Check logs.txt and out_binary.jpg / out_json.jpg.")

if __name__ == "__main__":
    main()
