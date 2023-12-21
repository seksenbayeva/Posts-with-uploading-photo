from flask import Flask, flash, request, redirect, render_template,  url_for
import json, os
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Загрузка данных из JSON-файла
with open('data.json', 'r') as file:
    try:
        users = json.load(file)
    except Exception as e:
        print(f"Error loading data from JSON file: {e}")
        users = []

UPLOAD_FOLDER = 'static/uploaded_images'  # Папка для сохранения загруженных изображений
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Список профилей
@app.route('/')
def main():
    return render_template('main.html', users=users)

# Профиль пользователя
@app.route('/profile/<int:user_id>')
def open_main(user_id):
    user = next((user for user in users if user["id"] == user_id), None)
    if user:
        return render_template('open_main.html', user=user)
    return "Пользователь не найден", 404

# Создание профиля

@app.route('/create_feed', methods=['GET', 'POST'])
def create_feed():
    if request.method == 'POST':
        new_user = {
            "id": len(users) + 1,
            "name": request.form['name'],
            "number": request.form['number'],
            "about": request.form['about'],
            "photo_path": None  # Путь к фотографии, который будет сохранен
        }

        # Обработка загруженной фотографии
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                photo.save(photo_path)
                new_user["photo_path"] = photo_path  # Сохранение пути к фотографии в профиле пользователя

        users.append(new_user)
        
        with open('data.json', 'w') as file:
            json.dump(users, file)
        
        return redirect(url_for('main'))
    
    return render_template('create_feed.html')


# Редактирование профиля
@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_feed(user_id):
    user = next((user for user in users if user["id"] == user_id), None)
    if user:
        if request.method == 'POST':
            user["name"] = request.form['name']
            user["number"] = request.form['number']
            user["about"] = request.form['about']

            # Обновление загруженной фотографии, если пользователь загрузил новую
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename != '':
                    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                    photo.save(photo_path)
                    user["photo_path"] = photo_path  # Обновление пути к фотографии в профиле пользователя

            with open('data.json', 'w') as file:
                json.dump(users, file)

            return redirect(url_for('open_main', user_id=user_id))
        return render_template('edit_feed.html', user=user)
    return "Пользователь не найден", 404


# Удаление профиля
@app.route('/delete_profile/<int:user_id>')
def delete_feed(user_id):
    global users
    users = [user for user in users if user["id"] != user_id]
    
    with open('data.json', 'w') as file:
        json.dump(users, file)
    
    return redirect(url_for('main'))


@app.route('/create_feed', methods=['GET', 'POST'])
def edit_or_create_feed(user_id=None):
    if user_id is not None:
        user = next((user for user in users if user["id"] == user_id), None)
        if not user:
            return "Пользователь не найден", 404
    else:
        user = None

    if request.method == 'POST':
        name = request.form.get('name')
        number = request.form.get('number')
        about = request.form.get('about')

        if not (name and number and about):
            flash('Пожалуйста, заполните все поля.', 'error')
            return redirect(url_for('main'))

        if user:
            user["name"] = name
            user["number"] = number
            user["about"] = about
            flash('Профиль успешно отредактирован.', 'success')
        else:
            new_user = {
                "id": len(users) + 1,
                "name": name,
                "number": number,
                "about": about
            }
            users.append(new_user)
            flash('Профиль успешно создан.', 'success')

        with open('data.json', 'w') as file:
            json.dump(users, file)

        return redirect(url_for('main'))

    return render_template('edit_feed.html', user=user)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file:
        filename = secure_filename(file.filename)
        # Получаем путь к изображению
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Заменяем обратные слэши на прямые
        path = path.replace('\\', '/')
        
        # Сохраняем изображение
        file.save(path)
        return 'Image uploaded successfully'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)

