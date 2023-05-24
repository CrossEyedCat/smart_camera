import psycopg2
conn = psycopg2.connect(
    host="ep-misty-fire-374016.eu-central-1.aws.neon.tech",
    database="neondb",
    user="gabyfollow",
    password="e3iJTC6bMFxq")
cur = conn.cursor()

cur.execute('SELECT count(*) FROM visitors')
info = cur.fetchall()
print(info)
conn.close()