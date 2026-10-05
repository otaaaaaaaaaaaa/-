import csv
import random
from datetime import datetime

from fastapi import FastAPI, Request

from database import init_db, get_connection

app = FastAPI()

init_db()

questions = []

with open("questions.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        questions.append(row)
