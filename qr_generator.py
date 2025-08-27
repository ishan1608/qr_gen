#!/usr/bin/env python3

import argparse
import sys

import qrcode
from PIL import Image


def generate_qr_code(url, output_file=None, size=10, border=4, logo_path=None):
    """Generate QR code for a given URL with optional logo"""

    if logo_path:
        img = create_qr_with_logo_space(url, size, border, logo_path)
    else:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=border,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

    if output_file is None:
        output_file = "qr_code.png"

    img.save(output_file)
    print(f"QR code saved as {output_file}")


def create_qr_with_logo_space(url, size, border, logo_path):
    """Create QR code with reserved center space for logo"""
    
    # First create a normal QR code to get the module layout
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    # Get module information
    modules = qr.modules
    module_count = len(modules)
    center = module_count // 2
    logo_radius = max(2, module_count // 8)
    
    # Create image manually, skipping center area
    img_size = (module_count * size) + (2 * border * size)
    img = Image.new('RGB', (img_size, img_size), 'white')
    
    # Draw QR modules, skipping logo area
    for row in range(module_count):
        for col in range(module_count):
            if modules[row][col]:  # If module should be black
                # Skip if in logo area
                if (center - logo_radius <= row <= center + logo_radius and 
                    center - logo_radius <= col <= center + logo_radius):
                    continue
                
                # Calculate pixel position
                x = (border * size) + (col * size)
                y = (border * size) + (row * size)
                
                # Draw black square
                for px in range(size):
                    for py in range(size):
                        if x + px < img_size and y + py < img_size:
                            img.putpixel((x + px, y + py), (0, 0, 0))
    
    # Add logo to the reserved center space
    try:
        logo = Image.open(logo_path)
        
        # Calculate logo size and position
        logo_pixel_size = logo_radius * 2 * size
        
        # Calculate true center of the QR code image
        img_center_x = img_size // 2
        img_center_y = img_size // 2
        
        logo = logo.resize((logo_pixel_size, logo_pixel_size), Image.Resampling.LANCZOS)
        
        logo_pos = (img_center_x - logo_pixel_size // 2, 
                   img_center_y - logo_pixel_size // 2)
        
        if logo.mode == 'RGBA':
            img.paste(logo, logo_pos, logo)
        else:
            img.paste(logo, logo_pos)
            
    except Exception as e:
        print(f"Error adding logo: {e}")
    
    return img


def main():
    parser = argparse.ArgumentParser(description="Generate QR code for a URL")
    parser.add_argument("url", help="URL to encode in QR code")
    parser.add_argument("-o", "--output", help="Output file name (default: qr_code.png)")
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
