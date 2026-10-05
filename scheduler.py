from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def reminder_job():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT user_id
    FROM current_question
    WHERE datetime(sent_at)
      <= datetime('now','-30 minutes')
    """)

    users = cur.fetchall()

    for row in users:
        user_id = row[0]

        # LINE push message
        print(
            f"{user_id}へリマインド送信"
        )

    conn.close()


def inactive_job():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT user_id
    FROM users
    WHERE datetime(last_activity)
      <= datetime('now','-12 hours')
    """)

    users = cur.fetchall()

    for row in users:

        user_id = row[0]

        cur.execute("""
        SELECT *
        FROM current_question
        WHERE user_id=?
        """, (user_id,))

        if not cur.fetchone():

            send_question(user_id)

    conn.close()


scheduler.add_job(
    reminder_job,
    "interval",
    minutes=30
)

scheduler.add_job(
    inactive_job,
    "interval",
    minutes=30
)

scheduler.start()
