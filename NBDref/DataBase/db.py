from tortoise import Tortoise, run_async
import os

#"default": "postgres://gen_user:9u3gwsbtl9@92.53.105.63:5432/default_db""default":"postgres://gen_user:sif0yatup6@89.223.71.152:5432/default_db"

#realize load from env
DB_CONFIG = {
    "connections": {"default": {
        'engine': 'tortoise.backends.asyncpg',
        "credentials": {
                    "database": os.environ.get('DB_NAME'),
                    "host": os.environ.get('DB_URL'),
                    "password": os.environ.get('DB_PASS'),
                    "port": os.environ.get('DB_PORT'),
                    "user": os.environ.get('DB_USER'),
                    }
    }},
    "apps": {
        "models": {
            "models": ["DataBase.Models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
 
#create tables if tables not exist
async def create_connection():
    await Tortoise.init(config=DB_CONFIG)
    await Tortoise.generate_schemas(safe=True) 
