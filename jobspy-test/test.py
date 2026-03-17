from db import get_connection

print("Running DB test...")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT DATABASE() as db_name")
print("Connected DB:", cursor.fetchone())

cursor.execute("SELECT COUNT(*) as total FROM jobs")
print("Total rows in jobs table:", cursor.fetchone())

cursor.close()
conn.close()

print("Done.")
