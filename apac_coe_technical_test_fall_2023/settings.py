import os

import dotenv

dotenv.load_dotenv(".env.local")
SECRET_KEY = os.environ["SECRET_KEY"]
APP_USERNAME = os.environ["APP_USERNAME"]
APP_PASSWORD = os.environ["APP_PASSWORD"]
DATABASE_USERNAME = os.environ["DATABASE_USERNAME"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_PORT = os.environ["DATABASE_PORT"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
