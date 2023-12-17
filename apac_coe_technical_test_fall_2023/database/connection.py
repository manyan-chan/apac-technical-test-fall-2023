from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apac_coe_technical_test_fall_2023.settings import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USERNAME,
)

# Create engine and session

# engine = create_engine("mysql+pymysql://root:secret@db:3306/techtest")
engine = create_engine(
    f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)
Session = sessionmaker(bind=engine)
