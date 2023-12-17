from sqlalchemy import text

from apac_coe_technical_test_fall_2023.database.connection import Session


def test_connection():
    session = Session()
    session.execute(text("SELECT 1"))
    session.close()
