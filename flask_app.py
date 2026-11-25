from flask import Flask, render_template_string, request

app = Flask(__name__)

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>ЛР 6 — Flask модуль</title>
    <style>
        body { font-family: Segoe UI, Arial, sans-serif; margin: 36px; max-width: 740px; color: #222; }
        .box { background: #f8f9fa; padding: 16px; border-radius: 6px; margin-bottom: 24px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #d0d7de; padding: 8px 12px; text-align: left; }
        th { background-color: #eef2f6; }
        .reply { margin-top: 12px; color: #0969da; font-weight: 600; }
    </style>
</head>
<body>
    <div class="box">
        <h1>Приветственная форма</h1>
        <form method="post">
            <label for="visitor_name">Ваше имя:</label>
            <input type="text" id="visitor_name" name="visitor_name" placeholder="Например, Иван" required>
            <button type="submit">Отправить</button>
        </form>
        {% if reply_text %}
            <p class="reply">{{ reply_text }}</p>
        {% endif %}
    </div>

    <h2>Список дисциплин</h2>
    <table>
        <thead>
            <tr>
                <th>Код</th>
                <th>Дисциплина</th>
                <th>Семестр</th>
                <th>Формат</th>
            </tr>
        </thead>
        <tbody>
            {% for item in subjects %}
            <tr>
                <td>{{ item.code }}</td>
                <td>{{ item.title }}</td>
                <td>{{ item.semester }}</td>
                <td>{{ item.exam_type }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

SUBJECTS = [
    {"code": "MTP-1", "title": "Методы и технологии программирования", "semester": 5, "exam_type": "Зачёт"},
    {"code": "DB-2", "title": "Базы данных и СУБД", "semester": 5, "exam_type": "Экзамен"},
    {"code": "WEB-3", "title": "Веб-технологии", "semester": 6, "exam_type": "Диф. зачёт"},
]


@app.route("/", methods=["GET", "POST"])
def home():
    reply_text = None
    if request.method == "POST":
        raw_name = request.form.get("visitor_name", "").strip()
        if raw_name:
            reply_text = f"Здравствуйте, {raw_name}! Форма успешно обработана."
    return render_template_string(PAGE_TEMPLATE, reply_text=reply_text, subjects=SUBJECTS)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)