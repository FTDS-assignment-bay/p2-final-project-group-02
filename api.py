from flask import Flask, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

# Folder utama tempat latihan disimpan
EXERCISE_FOLDER = './exercises'

# Route untuk melihat semua latihan
@app.route('/exercises', methods=['GET'])
def get_all_exercises():
    # Daftar latihan yang ada di dalam folder exercises
    exercises = []

    # Loop melalui folder exercises dan ambil nama folder
    for folder_name in os.listdir(EXERCISE_FOLDER):
        exercise_folder = os.path.join(EXERCISE_FOLDER, folder_name)

        # Pastikan yang ditemukan adalah folder, bukan file
        if os.path.isdir(exercise_folder):
            exercises.append(folder_name)

    # Mengembalikan daftar nama latihan
    return jsonify({'exercises': exercises})

@app.route('/exercise/<exercise_name>', methods=['GET'])
def get_exercise(exercise_name):
    # Path to the exercise folder for images
    exercise_folder = os.path.join(EXERCISE_FOLDER, exercise_name)

    # Check if the folder exists
    if not os.path.exists(exercise_folder):
        return jsonify({'error': 'Exercise not found'}), 404

    # Check for the corresponding JSON file for description
    json_file_path = os.path.join(EXERCISE_FOLDER, f'{exercise_name}.json')
    if not os.path.exists(json_file_path):
        return jsonify({'error': 'Exercise description not found'}), 404

    # Load the exercise description from the JSON file
    with open(json_file_path, 'r') as f:
        description = json.load(f)

    # Gather images from the exercise folder
    images = []
    for filename in os.listdir(exercise_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            images.append(f"/exercises/{exercise_name}/{filename}")

    # Prepare the response JSON
    response = {
        'name': exercise_name,
        'images': images,
        'description': description
    }

    return jsonify(response)

@app.route('/exercises/<exercise_name>/<filename>')
def get_exercise_image(exercise_name, filename):
    # Serve image files from the exercises folder
    return send_from_directory(os.path.join(EXERCISE_FOLDER, exercise_name), filename)

if __name__ == '__main__':
    app.run(debug=True)
