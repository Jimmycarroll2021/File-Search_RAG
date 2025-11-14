"""Query database directly"""
import sqlite3

db_path = 'instance/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables in database: {tables}\n")

if tables:
    # Get all documents
    try:
        cursor.execute("""
            SELECT id, filename, category, upload_date,
                   ROUND(CAST(file_size AS REAL) / 1024, 2) as size_kb
            FROM documents
            ORDER BY upload_date DESC
        """)

        docs = cursor.fetchall()

        print(f"Total documents in database: {len(docs)}\n")
        print("="*80)

        for doc in docs:
            doc_id, filename, category, upload_date, size_kb = doc
            print(f"[{doc_id}] {filename}")
            print(f"    Category: {category}")
            print(f"    Size: {size_kb} KB")
            print(f"    Uploaded: {upload_date}")
            print()
    except sqlite3.OperationalError as e:
        print(f"Error querying documents: {e}")
else:
    print("Database is empty - no tables found!")
    print("Run: python init_db.py")

conn.close()
