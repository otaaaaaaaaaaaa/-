from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/callback")
async def callback(request: Request):
    return "OK"
