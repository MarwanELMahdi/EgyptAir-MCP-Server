import os
import sqlite3

DATABASE_NAME = "database.db"

# Remove old database if it exists
if os.path.exists(DATABASE_NAME):
    os.remove(DATABASE_NAME)

# Create new database
connection = sqlite3.connect(DATABASE_NAME)

# Create tables
with open("schema.sql", "r") as schema_file:
    connection.executescript(schema_file.read())

# Insert seed data
with open("seed.sql", "r") as seed_file:
    connection.executescript(seed_file.read())

connection.commit()
connection.close()

print("Database created successfully.")
print("Sample data inserted successfully.")