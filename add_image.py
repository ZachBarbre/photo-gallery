#!/usr/bin/env python3
"""
Script to copy an image file to the images folder, add its filename to index.html,
and push changes to GitHub for GitHub Pages publishing
Usage: python add_image.py <image_file_path> [commit_message]
"""

import os
import sys
import shutil
import re
import subprocess


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


def run_git_command(command, error_message="Git command failed"):
    """
    Run a git command and return the result
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}")
        print(f"Details: {e.stderr}")
        return False, e.stderr


def check_git_repo():
    """
    Check if we're in a git repository
    """
    success, _ = run_git_command(
        "git rev-parse --git-dir",
        "Not a git repository. Please initialize git first with 'git init'"
    )
    return success


def commit_and_push_changes(image_filename, commit_message=None):
    """
    Commit changes and push to GitHub
    """
    if not check_git_repo():
        return False

    # Default commit message if none provided
    if not commit_message:
        commit_message = f"Add image: {image_filename}"

    print("\n📤 Publishing to GitHub...")

    # Add the files
    print("  → Adding files to git...")
    success, _ = run_git_command(
        f"git add images/{image_filename} index.html",
        "Failed to add files to git"
    )
    if not success:
        return False

    # Commit the changes
    print(f"  → Committing changes...")
    success, _ = run_git_command(
        f'git commit -m "{commit_message}"',
        "Failed to commit changes"
    )
    if not success:
        # Check if there were no changes to commit
        success, output = run_git_command("git status --porcelain", "")
        if not output.strip():
            print("  ℹ No changes to commit (file may already be in repository)")
        return False

    # Push to GitHub
    print("  → Pushing to GitHub...")
    success, _ = run_git_command(
        "git push",
        "Failed to push to GitHub. Make sure you have a remote repository set up."
    )

    if success:
        print("\n✅ Successfully published to GitHub!")
        print("   Your GitHub Pages site will update shortly.")
        return True
    else:
        print("\nℹ️  Changes committed locally but not pushed.")
        print("   Run 'git push' manually or check your remote repository settings.")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python add_image.py <image_file_path> [commit_message]")
        print("\nExample:")
        print("  python add_image.py photo.jpg")
        print("  python add_image.py photo.jpg 'Add vacation photo'")
        sys.exit(1)

    image_path = sys.argv[1]
    commit_message = sys.argv[2] if len(sys.argv) > 2 else None

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
    else:
        print("Failed to update index.html")
        sys.exit(1)

    # Commit and push to GitHub
    commit_and_push_changes(image_filename, commit_message)


if __name__ == "__main__":
    main()
