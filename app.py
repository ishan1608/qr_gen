import io

import qrcode
from PIL import Image
from flask import Flask, request, send_file, jsonify, send_from_directory

app = Flask(__name__)


def generate_qr_code_image(url, border, logo):
    """Generate QR code with optional logo overlay using error correction"""

    # Create QR code with high error correction for logo compatibility
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        # box_size=size,
        border=border,
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Generate complete QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    if not logo:
        return img

    # Calculate logo size (up to 30% of QR code for Level H error correction)
    qr_width, qr_height = img.size
    logo_size = min(qr_width, qr_height) // 4  # Conservative 25% coverage

    # Resize logo
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Calculate center position
    logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

    # Convert images to RGB to avoid alpha channel issues
    img = img.convert('RGB')
    if logo.mode == 'RGBA':
        # Create white background for logo to ensure clean overlay
        logo_bg = Image.new('RGB', (logo_size, logo_size), 'white')
        logo_bg.paste(logo, (0, 0), logo)  # Use alpha as mask
        img.paste(logo_bg, logo_pos)
    else:
        logo = logo.convert('RGB')
        img.paste(logo, logo_pos)

    return img


@app.route('/generate', methods=['POST'])
def generate_qr_form():
    """Generate QR code from form data"""
    # Get URL from form data (mandatory)
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    border = int(request.form.get('border', 1))

    # Check for logo file in form
    logo = None
    if 'logo' in request.files:
        logo_file = request.files['logo']
        if logo_file.filename != '':
            try:
                logo = Image.open(logo_file.stream)
            except Exception as e:
                return jsonify({'error': f'Invalid logo image: {str(e)}'}), 400

    # Generate QR code
    qr_img = generate_qr_code_image(url, border, logo)

    # Save to BytesIO buffer
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return send_file(
        img_buffer,
        mimetype='image/png',
        as_attachment=False,
        download_name='qr_code.png'
    )


@app.route('/')
def index():
    """Serve test HTML page"""
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
