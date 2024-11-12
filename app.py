from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import string

# Инициализация на Flask приложението
app = Flask(__name__)

# Настройка на база данни с SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Изключване на проследяването на модификации

# Инициализация на SQLAlchemy за работа с базата данни
db = SQLAlchemy(app)

# Създаване на модел за съхранение на оригиналните и съкратените URL
class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Идентификатор на запис
    original_url = db.Column(db.String(500), nullable=False)  # Оригинален URL
    shortened_url = db.Column(db.String(100), unique=True, nullable=False)  # Съкратен URL

# Главен маршрут за началната страница
@app.route("/")
def welcome_page():
    return render_template("UrlShortener.html")

# Маршрут за генериране на съкратен URL
@app.route("/generate_url", methods=["POST"])
def generate_url():
    original_url = request.form.get("url")  # Вземане на оригиналния URL от формата
    custom_short_url = request.form.get("custom_short_url")  # Вземане на потребителски съкратен URL
    slider_length = int(request.form.get("slider_value"))  # Вземане на стойността от плъзгача за дължината на URL

    # Проверка дали е подаден оригинален URL
    if not original_url:
        return redirect(url_for("welcome_page"))  # Пренасочване обратно, ако няма оригинален URL

    # Ако потребителят е предоставил потребителски съкратен URL
    if custom_short_url:
        shortened_url = f"http://localhost:5000/{custom_short_url}"
    else:
        # Генериране на случаен съкратен URL, ако няма потребителски
        random_path = ''.join(random.choices(string.ascii_letters + string.digits, k=slider_length))
        shortened_url = f"http://localhost:5000/{random_path}"

    # Проверка дали URL вече съществува в базата данни
    existing_url = ShortURL.query.filter_by(original_url=original_url).first()
    if existing_url:
        # Ако съществува, използваме съществуващия съкратен URL
        shortened_url = existing_url.shortened_url
    else:
        # Ако не съществува, добавяме нов запис в базата данни
        new_url = ShortURL(original_url=original_url, shortened_url=shortened_url)
        db.session.add(new_url)
        db.session.commit()

    # Връщаме страницата с новия съкратен URL
    return render_template("UrlShortener.html", shortened_url=shortened_url)

# Маршрут за пренасочване от съкратен URL към оригиналния
@app.route("/<shortened_url>")
def redirect_to_original(shortened_url):
    # Търсене на съкратен URL в базата данни
    short_url_record = ShortURL.query.filter_by(shortened_url=f"http://localhost:5000/{shortened_url}").first()
    if short_url_record:
        # Ако има запис, пренасочваме към оригиналния URL
        if short_url_record.original_url == "secret":
            # Ако оригиналният URL е "secret", показваме специална страница
            return render_template("secret.html")
        else:
            return redirect(short_url_record.original_url)
    else:
        # Ако не съществува съкратеното URL, връщаме грешка 404
        return "URL not found", 404

# Нов маршрут за показване на историята на съкратените URL
@app.route('/history')
def history():
    try:
        all_urls = ShortURL.query.all()  # Вземане на всички записи с URL от базата данни
        print("URLs retrieved from database:", all_urls)  # Дебъг линия за проверка
    except Exception as e:
        print("Error retrieving URLs:", e)  # Логване на грешка, ако има проблем
        all_urls = []  # В случай на грешка, върни празен списък

    # Рендериране на историята на съкратените URL
    return render_template('history.html', urls=all_urls)

# Основен блок за стартиране на приложението
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Създаване на всички таблици в базата данни, ако не съществуват

    app.run(debug=True)  # Стартиране на Flask приложението в режим за отстраняване на грешки
