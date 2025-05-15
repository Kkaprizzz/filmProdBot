from threading import Thread
import asyncio
from flask import Flask, request, jsonify
import database
import handlers as hnd  # твой файл с ботом
from handlers import dp, bot  # импорт диспетчера и бота из handlers

app = Flask(__name__)

@app.route('/newfilmRequest', methods=['POST'])
def api():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data.get('code')
    title = data.get('title')
    description = data.get('description')
    image_url = data.get('image_url')

    database.add_movie(code, title, description, image_url)
    return jsonify({'message': 'Film added successfully'}), 200

@app.route('/removefilmRequest', methods=['POST'])
def remove_film():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data.get('code')
    database.delete_movie(code)
    return jsonify({'message': 'Film removed successfully'}), 200

@app.route('/showfilmsRequest', methods=['GET'])
def show_films():
    films = database.show_all_movies()
    return jsonify(films), 200

@app.route('/newpostRequest', methods=['POST'])
def new_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    text = data.get('text')
    image_url = data.get('image_url')
    url = data.get('urls')

    asyncio.run(hnd.process_post(text, image_url, url))
    return jsonify({'message': 'Post added successfully'}), 200

@app.route("/showUsersRequest", methods=["GET"])
def show_users():
    users = database.show_all_users()
    return jsonify(users), 200

@app.route("/editFilmTitleRequest", methods=["POST"])
def edit_film_title():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data.get('code')
    title = data.get('title')

    database.editFilmTitle(code, title)
    return jsonify({'message': 'Film title updated successfully'}), 200

@app.route("/editFilmDescriptionRequest", methods=["POST"])
def edit_film_description():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data.get('code')
    description = data.get('description')

    database.editFilmDescription(code, description)
    return jsonify({'message': 'Film description updated successfully'}), 200

@app.route("/editFilmImageRequest", methods=["POST"])
def edit_film_image():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    code = data.get('code')
    image_url = data.get('image_url')

    database.editFilmImage(code, image_url)
    return jsonify({'message': 'Film image updated successfully'}), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000)  # или другой порт, который нужен

def run_bot():
    asyncio.run(dp.start_polling(bot, skip_updates=True))

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # В основном потоке запускаем бота
    run_bot()
