import argparse
import sys

import qrcode
from PIL import Image


def generate_qr_code(url, output_file, size, border, logo_path):
    """Generate QR code with optional logo overlay using error correction"""

    # Create QR code with high error correction for logo compatibility
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Generate complete QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    if not logo_path:
        img.save(output_file)
        print(f"QR code saved as {output_file}")
        return img

    logo = Image.open(logo_path)

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

    img.save(output_file)
    print(f"QR code saved as {output_file}")
    return img


def main():
    parser = argparse.ArgumentParser(description="Generate QR code for a URL")
    parser.add_argument("url", help="URL to encode in QR code")
    parser.add_argument("-o", "--output", default="qr_code.png", help="Output file name (default: qr_code.png)")
    parser.add_argument("-s", "--size", type=int, default=10, help="Box size (default: 10)")
    parser.add_argument("-b", "--border", type=int, default=4, help="Border size (default: 4)")
    parser.add_argument("-l", "--logo", help="Path to logo image to place in center")

    args = parser.parse_args()

    try:
        generate_qr_code(args.url, args.output, args.size, args.border, args.logo)
    except Exception as e:
        print(f"Error generating QR code: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
