#!/usr/bin/env python3

import os
import sys
import shutil
import re


def add_image_to_html(image_filename, html_file='index.html'):
    """
    Add image filename to the const images array in index.html
    """
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return False

    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find the const images = [...]; declaration
    pattern = r'(const\s+images\s*=\s*\[)(.*?)(\];)'

    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print("Error: Could not find 'const images = [...];' in index.html")
        return False

    # Extract the current array content
    array_content = match.group(2).strip()

    # Build the new array content
    if array_content and not array_content.endswith(','):
        # If there's existing content without trailing comma, add comma
        if array_content.strip():
            new_array_content = f'{array_content},\n      "{image_filename}"'
        else:
            new_array_content = f'\n      "{image_filename}"\n      '
    else:
        # Empty array or already has trailing comma
        if array_content:
            new_array_content = f'{array_content}\n      "{image_filename}"'
        else:
            new_array_content = f'\n      "{image_filename}"\n      '

    # Replace the old array with the new one
    new_content = re.sub(
        pattern,
        f'\\1{new_array_content}\\3',
        content,
        flags=re.DOTALL
    )

    # Write back to the file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python update.py <image_file_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    # Check if the image file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        sys.exit(1)

    # Create images folder if it doesn't exist
    images_folder = 'images'
    os.makedirs(images_folder, exist_ok=True)

    # Get the image filename
    image_filename = os.path.basename(image_path)

    # Destination path
    destination = os.path.join(images_folder, image_filename)

    # Copy the image
    try:
        shutil.copy2(image_path, destination)
        print(f"✓ Copied '{image_filename}' to '{images_folder}/' folder")
    except Exception as e:
        print(f"Error copying file: {e}")
        sys.exit(1)

    # Update index.html
    if add_image_to_html(image_filename):
        print(f"✓ Added '{image_filename}' to index.html")
        print("\nDone! Your image has been added successfully.")
    else:
        print("Failed to update index.html")
        sys.exit(1)


if __name__ == "__main__":
    main()
