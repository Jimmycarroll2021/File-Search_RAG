"""Check all uploaded files"""
from app.models import Store, Document
from app.database import db
from app import create_app

app = create_app()

with app.app_context():
    docs = Document.query.order_by(Document.upload_date.desc()).all()
    print(f"Total documents: {len(docs)}\n")

    for d in docs:
        print(f"  [{d.id}] {d.filename}")
        print(f"      Uploaded: {d.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"      Category: {d.category}")
        file_size_kb = round(d.file_size / 1024, 2) if d.file_size else 0
        print(f"      Size: {file_size_kb} KB")
        print()
