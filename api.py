from flask import Flask, jsonify, request, send_from_directory
import os
import json

app = Flask(__name__)

# Folder untuk menyimpan latihan
EXERCISES_FOLDER = 'exercises'


def get_exercise_json(exercise_folder):
    """Mencari file .json dalam folder latihan dan mengembalikan isi JSON."""
    try:
        json_file = os.path.join(exercise_folder, f"{os.path.basename(exercise_folder)}.json")
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error reading JSON file in {exercise_folder}: {e}")
        return None


@app.route('/search', methods=['GET'])
def search_exercise():
    # Mendapatkan parameter 'exercise' dari query string
    exercise_query = request.args.get('exercise', '').strip().lower()
    exercises = []

    try:
        # Cek apakah folder latihan ada
        if not os.path.exists(EXERCISES_FOLDER):
            return jsonify({"message": "Exercises folder not found."}), 500

        # Cari folder latihan yang sesuai dengan query
        if exercise_query:
            for folder_name in os.listdir(EXERCISES_FOLDER):
                folder_path = os.path.join(EXERCISES_FOLDER, folder_name)
                # Pastikan folder ini adalah folder dan namanya cocok dengan query
                if os.path.isdir(folder_path) and exercise_query in folder_name.lower():
                    exercises.append(folder_name)

        if exercises:
            return jsonify({"exercises": exercises}), 200
        else:
            return jsonify({"message": "No exercises found"}), 404
    except Exception as e:
        print(f"Error in search_exercise: {e}")
        return jsonify({"message": "Internal server error."}), 500


@app.route('/list_all', methods=['GET'])
def list_all_exercises():
    """Mengembalikan semua folder latihan yang ada di direktori exercises."""
    try:
        # Daftar semua folder di dalam EXERCISES_FOLDER
        folders = [
            folder_name for folder_name in os.listdir(EXERCISES_FOLDER)
            if os.path.isdir(os.path.join(EXERCISES_FOLDER, folder_name))
        ]
        return jsonify({"exercises": folders}), 200
    except Exception as e:
        return jsonify({"message": f"Error occurred: {str(e)}"}), 500


@app.route('/exercises/<exercise_name>', methods=['GET'])
def get_exercise_details(exercise_name):
    # Menangani kasus huruf kapital yang tidak konsisten
    exercise_name = exercise_name.strip().lower()

    try:
        # Menentukan path folder latihan
        exercise_folder = os.path.join(EXERCISES_FOLDER, exercise_name)

        # Memeriksa apakah folder latihan ada
        if os.path.exists(exercise_folder) and os.path.isdir(exercise_folder):
            exercise_details = get_exercise_json(exercise_folder)

            if exercise_details:
                return jsonify(exercise_details), 200
            else:
                return jsonify({"message": "Exercise details not found."}), 404
        else:
            return jsonify({"message": "Exercise not found."}), 404
    except Exception as e:
        print(f"Error in get_exercise_details: {e}")
        return jsonify({"message": "Internal server error."}), 500


@app.route('/exercises/<exercise_name>/images/<image_number>.jpg', methods=['GET'])
def get_exercise_image(exercise_name, image_number):
    """Endpoint untuk mengambil gambar latihan (0.jpg atau 1.jpg)."""
    try:
        # Pastikan nama latihan dan nomor gambar valid
        exercise_name = exercise_name.strip().lower()
        image_name = f"{image_number}.jpg"

        # Menentukan path gambar latihan
        image_path = os.path.join(EXERCISES_FOLDER, exercise_name, image_name)

        # Memeriksa apakah gambar ada
        if os.path.exists(image_path):
            return send_from_directory(os.path.join(EXERCISES_FOLDER, exercise_name), image_name)
        else:
            return jsonify({"message": "Image not found."}), 404
    except Exception as e:
        print(f"Error in get_exercise_image: {e}")
        return jsonify({"message": "Internal server error."}), 500


if __name__ == '__main__':
    # Menjalankan aplikasi Flask
    app.run(debug=True)
