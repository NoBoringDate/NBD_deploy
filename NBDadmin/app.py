import uvicorn
from NBDapp import app
import os

if __name__ == "__main__":
    uvicorn.run("app:app",
                host='0.0.0.0',
                port=int(os.environ.get('APP_PORT')),
                workers=4,
                reload=True)
