from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from web_app.views import router as web_app_router

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="web_app/static"), name="static")
# Register web_app router
app.include_router(web_app_router)
