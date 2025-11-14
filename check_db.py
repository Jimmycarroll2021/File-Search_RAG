import sqlite3

conn = sqlite3.connect('instance/app.db')
cursor = conn.cursor()

print('Stores in database:')
cursor.execute('SELECT name, gemini_store_id FROM stores')
stores = cursor.fetchall()
for store in stores:
    print(f'  - {store[0]}: {store[1]}')

print('\nDocuments in database:')
cursor.execute('SELECT filename, category, gemini_file_id FROM documents')
docs = cursor.fetchall()
for doc in docs:
    print(f'  - {doc[0]} (category: {doc[1]}, gemini_id: {doc[2]})')

conn.close()
