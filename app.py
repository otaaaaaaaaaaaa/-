import csv
import random
from datetime import datetime

from fastapi import FastAPI, Request

from database import init_db, get_connection

app = FastAPI()

@app.post("/callback")
async def callback(request: Request):
    return "OK"

init_db()

questions = []


with open("questions.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        questions.append(row)


def send_question(user_id):

    q = random.choice(questions)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT OR REPLACE INTO current_question
    (user_id, question_id)
    VALUES (?,?)
    """, (user_id, q["id"]))

    conn.commit()
    conn.close()

    return q["question"]


def check_answer(user_id, answer):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT question_id
    FROM current_question
    WHERE user_id = ?
    """, (user_id,))

    row = cur.fetchone()

    if not row:
        return "先に問題を受け取ってください"

    qid = row[0]

    question = next(
        q for q in questions
        if int(q["id"]) == qid
    )

    correct = (
        answer.strip()
        == question["answer"].strip()
    )

    cur.execute("""
    INSERT INTO answers
    (user_id,question_id,correct)
    VALUES (?,?,?)
    """, (
        user_id,
        qid,
        1 if correct else 0
    ))

    if correct:

        cur.execute("""
        INSERT OR IGNORE INTO users
        (user_id)
        VALUES (?)
        """, (user_id,))

        cur.execute("""
        UPDATE users
        SET total_score = total_score + 1,
            last_activity=CURRENT_TIMESTAMP
        WHERE user_id=?
        """, (user_id,))

    cur.execute("""
    DELETE FROM current_question
    WHERE user_id=?
    """, (user_id,))

    conn.commit()
    conn.close()

    if correct:
        return f"⭕正解\n\n{question['explanation']}"

    return (
        f"❌不正解\n"
        f"正解:{question['answer']}\n\n"
        f"{question['explanation']}"
    )


def get_mypage(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        COUNT(*),
        SUM(correct)
    FROM answers
    WHERE user_id=?
    """, (user_id,))

    total, correct = cur.fetchone()

    total = total or 0
    correct = correct or 0

    wrong = total - correct

    accuracy = (
        round(correct / total * 100, 1)
        if total > 0 else 0
    )

    cur.execute("""
    SELECT total_score
    FROM users
    WHERE user_id=?
    """, (user_id,))

    row = cur.fetchone()

    score = row[0] if row else 0

    conn.close()

    return f"""
📊マイページ

✅正解数: {correct}
❌不正解数: {wrong}
📚解答数: {total}
🎯正答率: {accuracy}%
🏆総合得点: {score}
"""


def get_ranking():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        user_id,
        total_score
    FROM users
    ORDER BY total_score DESC
    LIMIT 10
    """)

    data = cur.fetchall()

    conn.close()

    text = "🏆総合ランキング\n\n"

    for i, row in enumerate(data, start=1):
        text += f"{i}位 {row[0]} {row[1]}pt\n"

    return text


