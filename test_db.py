from app import app, db, Image

with app.app_context():
    images = Image.query.all()
    print("Total images in DB:", len(images))
    for i in images:
        print(i.id, i.category, i.url, i.user_id)
