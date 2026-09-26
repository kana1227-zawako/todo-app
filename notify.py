import os
import json
from datetime import datetime, timedelta
import base64
import gspread
import requests
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):


    service_account_info = json.loads(
        base64.b64decode(
            os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        ).decode("utf-8")
    )   

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )
else:
    creds = Credentials.from_service_account_file(
        "drive-upload-505005-c3b65ed15024.json",
        scopes=SCOPES
    )

gc = gspread.authorize(creds)
spreadsheet = gc.open("TODO リスト")
sheet = spreadsheet.sheet1

tomorrow = (datetime.now() + timedelta(days=1)).date()

todos = sheet.get_all_records()

for todo in todos:
    due_date = todo["期日"]

    if not due_date:
        continue

    due_date = datetime.strptime(
        due_date.replace("/", "-"),
        "%Y-%m-%d"
    ).date()

    if due_date == tomorrow and todo["完了"] != "完了":
        message = (
            f"明日が期日のTodoがあります。\n"
            f"【{todo['タイトル']}】\n"
            f"{todo['内容']}\n"
            f"重要度：{todo['重要度']}"
        )

        url = "https://api.line.me/v2/bot/message/push"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_TOKEN}"
        }

        data = {
            "to": LINE_USER_ID,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        response = requests.post(
            url,
            headers=headers,
            json=data
        )

        print("LINE送信結果:", response.status_code)