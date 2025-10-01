import psycopg2
import os # Use environment variables or enter a connection string directly

db_url = "postgresql://neondb_owner:"
conn = None
cur = None

try:
  # Connect to the database
  conn = psycopg2.connect(db_url)

#   conn = psycopg2.connect(
#     host="wisoft.io",
#     port="10012",
#     dbname="grafana",
#     user="grafana",
#     # password="github update blank space"  
#   )

  # Create cursor object
  cur = conn.cursor()

  # Execute SQL queries
  cur.execute("SELECT version();")
  db_version = cur.fetchone()
  print(f"PostgreSQL Database version: {db_version}")

  # Commit changes (required after INSERT, UPDATE, DELETE)
  # conn.commit()

except (Exception, psycopg2.DatabaseError) as error:
  print(f"Database Error: {error}")
finally:
  if cur is not None:
    cur.close()
  if conn is not None:
    conn.close()
    print("PostgreSQL unconnection to database.")