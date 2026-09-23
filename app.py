from flask import Flask, request, redirect, render_template_string
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

creds = Credentials.from_service_account_file(
    "drive-upload-505005-560d7c156396.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)
spreadsheet = gc.open("TODO リスト")
sheet = spreadsheet.sheet1

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>TODOリスト</title>
</head>
<body>

    <h1>TODOリスト</h1>

    <form method="POST" action="/add">
        <p>
            <input type="text" name="title" placeholder="タイトル" required>
        </p>

        <p>
            <input type="text" name="content" placeholder="内容">
        </p>

        <p>
            <input type="date" name="due_date">
        </p>

        <button type="submit">追加</button>
    </form>

    <h2>Todo一覧</h2>

    <ul>
        {% for todo in todos %}
            <li>

                {% if todo[4] == "完了" %}

                    <s>
                        <strong>{{ todo[0] }}</strong>
                        ：{{ todo[1] }}

                        {% if todo[2] %}
                            （{{ todo[2] }}）
                        {% endif %}

                        {% if todo[3] %}
                            【期日：{{ todo[3] }}】
                        {% endif %}
                    </s>

                    <strong>【完了】</strong>

                    <form method="POST"
                          action="/incomplete/{{ todo[0] }}"
                          style="display:inline;">
                        <button type="submit">未完了に戻す</button>
                    </form>

                    <form method="POST"
                          action="/delete/{{ todo[0] }}"
                          style="display:inline;">
                        <button type="submit">削除</button>
                    </form>

                {% else %}

                    <strong>{{ todo[0] }}</strong>
                    ：{{ todo[1] }}

                    {% if todo[2] %}
                        （{{ todo[2] }}）
                    {% endif %}

                    {% if todo[3] %}
                        【期日：{{ todo[3] }}】
                    {% endif %}

                    <form method="POST"
                          action="/complete/{{ todo[0] }}"
                          style="display:inline;">
                        <button type="submit">完了</button>
                    </form>

                    <form method="POST"
                          action="/delete/{{ todo[0] }}"
                          style="display:inline;">
                        <button type="submit">削除</button>
                    </form>

                {% endif %}

            </li>
        {% endfor %}
    </ul>

</body>
</html>
"""


@app.route("/")
def index():
    todos = sheet.get_all_values()[1:]

    for todo in todos:
        while len(todo) < 5:
            todo.append("")

        if todo[4] == "":
            todo[4] = "未完了"

    return render_template_string(HTML, todos=todos)


@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    content = request.form["content"]
    due_date = request.form["due_date"]

    existing_ids = sheet.col_values(1)[1:]

    numbers = []

    for value in existing_ids:
        try:
            numbers.append(int(value))
        except ValueError:
            pass

    next_id = max(numbers, default=0) + 1

    sheet.append_row([
        next_id,
        title,
        content,
        due_date,
        "未完了"
    ])

    return redirect("/")


@app.route("/complete/<int:todo_id>", methods=["POST"])
def complete(todo_id):
    ids = sheet.col_values(1)

    for row_number, value in enumerate(ids, start=1):
        if value == str(todo_id):
            sheet.update_cell(row_number, 5, "完了")
            break

    return redirect("/")


@app.route("/incomplete/<int:todo_id>", methods=["POST"])
def incomplete(todo_id):
    ids = sheet.col_values(1)

    for row_number, value in enumerate(ids, start=1):
        if value == str(todo_id):
            sheet.update_cell(row_number, 5, "未完了")
            break

    return redirect("/")


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    ids = sheet.col_values(1)

    for row_number, value in enumerate(ids, start=1):
        if value == str(todo_id):
            sheet.delete_rows(row_number)
            break

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)