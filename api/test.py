from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
    print("Tables dans la base :", [row[0] for row in result])
