from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from DataBase import DB_CONFIG


app=FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="templates/static"), name="static")
register_tortoise(
    app,
    config=DB_CONFIG,
    generate_schemas=True
)