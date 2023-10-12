import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from DataBase import DB_CONFIG


app=FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
if os.path.exists("../BotStorage"):
    app.mount("/BotStorage", StaticFiles(directory="../BotStorage"), name="BotStorage")
else:
    os.mkdir("../BotStorage")
    app.mount("/BotStorage", StaticFiles(directory="../BotStorage"), name="BotStorage")
register_tortoise(
    app,
    config=DB_CONFIG,
    generate_schemas=True
)