import sqlite3

from config import DATABASE_PATH


def get_connection():
    """
    Create and return a SQLite connection.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection