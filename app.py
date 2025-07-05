from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import time
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'pictures'
ARCHIVE_FOLDER = 'pictures/archived'
THUMBNAIL_FOLDER = 'thumbnails'
ARCHIVED_THUMBNAIL_FOLDER = 'pictures/archived/thumbnails'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ARCHIVE_FOLDER'] = ARCHIVE_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER

def move_to_archive_background():
    time.sleep(2)
    upload_folder = app.config['UPLOAD_FOLDER']
    archive_folder = app.config['ARCHIVE_FOLDER']

    for filename in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, filename)
        if os.path.isfile(file_path):
            # Move original image
            os.rename(file_path, os.path.join(archive_folder, filename))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/archived')
def archived():
    return render_template('archived.html')

THUMBNAIL_SIZE = (512, 512)

def save_file_background(file, filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    try:
        image = Image.open(filepath)
        image.thumbnail(THUMBNAIL_SIZE)
        thumbnail_filename = os.path.splitext(filename)[0] + ".webp"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
        image.save(thumbnail_path, "WEBP")
    except Exception as e:
        print(f"Error generating thumbnail for {filename}: {e}")

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return 'No file part', 400
    files = request.files.getlist('files')
    for file in files:
        if file.filename == '':
            continue
        if file:
            filename = file.filename
            # Generate thumbnail synchronously to ensure it's ready before page reload
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                image = Image.open(filepath)
                # Rotate image if width is greater than height
                if image.width > image.height:
                    image = image.rotate(90, expand=True)
                image.thumbnail(THUMBNAIL_SIZE)
                thumbnail_filename = os.path.splitext(filename)[0] + ".webp"
                thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
                image.save(thumbnail_path, "WEBP")
            except Exception as e:
                print(f"Error generating thumbnail for {filename}: {e}")
    return '', 200

@app.route('/pictures')
def list_pictures():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)) and f != 'archived']
    images_data = []
    for filename in image_files:
        original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        thumbnail_filename = os.path.splitext(filename)[0] + ".webp"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)

        if not os.path.exists(thumbnail_path):
            try:
                image = Image.open(original_filepath)
                image.thumbnail(THUMBNAIL_SIZE)
                image.save(thumbnail_path, "WEBP")
            except Exception as e:
                print(f"Error generating thumbnail for {filename}: {e}")
                continue # Skip this image if thumbnail generation fails
        images_data.append({'original_filename': filename, 'thumbnail_filename': thumbnail_filename})
    return jsonify(images_data)

@app.route('/archived_pictures')
def list_archived_pictures():
    image_files = os.listdir(app.config['ARCHIVE_FOLDER'])
    images_data = []
    for filename in image_files:
        original_filepath = os.path.join(app.config['ARCHIVE_FOLDER'], filename)
        thumbnail_filename = os.path.splitext(filename)[0] + ".webp"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)

        if not os.path.exists(thumbnail_path):
            try:
                image = Image.open(original_filepath)
                image.thumbnail(THUMBNAIL_SIZE)
                image.save(thumbnail_path, "WEBP")
            except Exception as e:
                print(f"Error generating thumbnail for archived {filename}: {e}")
                continue # Skip this image if thumbnail generation fails
        images_data.append({'original_filename': filename, 'thumbnail_filename': thumbnail_filename})
    return jsonify(images_data)

@app.route('/pictures/<path:filename>')
def get_picture(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/archived_pictures/<path:filename>')
def get_archived_picture(filename):
    return send_from_directory(app.config['ARCHIVE_FOLDER'], filename)

@app.route('/thumbnails/<path:filename>')
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/archived_thumbnails/<path:filename>')
def get_archived_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/delete-all', methods=['DELETE'])
def delete_all_pictures():
    thread = threading.Thread(target=move_to_archive_background)
    thread.start()
    return '', 204

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_picture(filename):
    try:
        source_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        destination_path = os.path.join(app.config['ARCHIVE_FOLDER'], filename)
        os.rename(source_path, destination_path)
        return '', 204
    except FileNotFoundError:
        return 'File not found', 404

@app.route('/rotate/<filename>', methods=['POST'])
def rotate_picture(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return 'File not found', 404

        image = Image.open(filepath)
        rotated_image = image.rotate(-90, expand=True)
        rotated_image.save(filepath) # Overwrite original image

        # Regenerate thumbnail
        thumbnail_filename = os.path.splitext(filename)[0] + ".webp"
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
        rotated_image.thumbnail(THUMBNAIL_SIZE)
        rotated_image.save(thumbnail_path, "WEBP")

        return '', 200
    except Exception as e:
        print(f"Error rotating image {filename}: {e}")
        return f'Error rotating image: {e}', 500

@app.route('/move_from_archive', methods=['POST'])
def move_from_archive():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': 'No filename provided'}), 400

    try:
        source_path = os.path.join(app.config['ARCHIVE_FOLDER'], filename)
        destination_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.rename(source_path, destination_path)
        return jsonify({'success': True, 'message': f'{filename} moved back to main pictures.'}), 200
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'File not found in archive'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

