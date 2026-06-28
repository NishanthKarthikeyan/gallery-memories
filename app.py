from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api
import datetime
import os
import uuid
import zipfile
import io

app = Flask(__name__)
CORS(app)
from dotenv import load_dotenv
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret')
if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/snapvault.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snapvault.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

APP_TITLE = "SnapVault — Family Memories"

# Cloudinary Configuration
cloudinary.config(
  cloud_name = "dza7ugm28",
  api_key = "993526995564523",
  api_secret = "y8cF4Q8doECvTCYtp7gVdX7S8ug",
  secure = True
)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user')

class Image(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20))
    desc = db.Column(db.String(500))
    fav = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(500))  # Comma-separated
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class ImageForm(FlaskForm):
    desc = TextAreaField('Description')
    date = StringField('Date (DD-MM-YYYY)')
    tags = StringField('Tags (comma-separated)')
    submit = SubmitField('Save')

# Create database
with app.app_context():
    db.create_all()
    # Create default user if not exists
    if not User.query.filter_by(username='nishanth').first():
        hashed_password = generate_password_hash('knh@2005')
        default_user = User(username='nishanth', password_hash=hashed_password)
        db.session.add(default_user)
        db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', app_title=APP_TITLE)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# API Routes
@app.route('/sync', methods=['GET'])
@login_required
def sync_from_cloudinary():
    try:
        result = cloudinary.Search().expression("folder:family_vault/*").max_results(500).execute()
        added_count = 0
        for resource in result.get('resources', []):
            url = resource.get('secure_url')
            if not Image.query.filter_by(url=url).first():
                public_id = resource.get('public_id', '')
                parts = public_id.split('/')
                category = parts[1] if len(parts) > 2 else 'others'
                new_image = Image(
                    url=url,
                    category=category,
                    date=resource.get('created_at', '').split('T')[0],
                    desc="Synced from Cloudinary",
                    user_id=current_user.id
                )
                db.session.add(new_image)
                added_count += 1
        db.session.commit()
        return jsonify({"status": "success", "message": f"Synced {added_count} new images", "total": Image.query.count()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images', methods=['GET'])
@login_required
def get_images():
    images = Image.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "_id": img.id,
        "url": img.url,
        "category": img.category,
        "date": img.date,
        "desc": img.desc,
        "fav": img.fav,
        "tags": img.tags
    } for img in images])

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    files = request.files.getlist('file')
    category = request.form.get('category', 'others')
    desc = request.form.get('desc', 'Family Moment')
    date = request.form.get('date', datetime.datetime.now().strftime("%d-%m-%Y"))
    tags = request.form.get('tags', '')
    
    uploaded_images = []
    
    try:
        for file in files:
            if file.filename == '':
                continue
            upload_result = cloudinary.uploader.upload(file, folder=f"family_vault/{category}")
            new_image = Image(
                url=upload_result.get("secure_url"),
                category=category,
                date=date,
                desc=desc,
                tags=tags,
                user_id=current_user.id
            )
            db.session.add(new_image)
            db.session.commit()
            uploaded_images.append({
                "_id": new_image.id,
                "url": new_image.url,
                "category": new_image.category,
                "date": new_image.date,
                "desc": new_image.desc,
                "fav": new_image.fav,
                "tags": new_image.tags
            })
        return jsonify(uploaded_images)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete/<id>', methods=['DELETE'])
@login_required
def delete_image(id):
    img = Image.query.filter_by(id=id, user_id=current_user.id).first()
    if img:
        db.session.delete(img)
        db.session.commit()
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Not found"}), 404

@app.route('/update/<id>', methods=['PUT'])
@login_required
def update_memory(id):
    img = Image.query.filter_by(id=id, user_id=current_user.id).first()
    if img:
        updates = request.json
        img.desc = updates.get('desc', img.desc)
        img.date = updates.get('date', img.date)
        img.fav = updates.get('fav', img.fav)
        img.tags = updates.get('tags', img.tags)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Not found"}), 404

@app.route('/search', methods=['GET'])
@login_required
def search_images():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    fav = request.args.get('fav', '')
    images = Image.query.filter_by(user_id=current_user.id)
    if query:
        images = images.filter(db.or_(Image.desc.contains(query), Image.tags.contains(query)))
    if category:
        images = images.filter_by(category=category)
    if fav == 'true':
        images = images.filter_by(fav=True)
    return jsonify([{
        "_id": img.id,
        "url": img.url,
        "category": img.category,
        "date": img.date,
        "desc": img.desc,
        "fav": img.fav,
        "tags": img.tags
    } for img in images])

@app.route('/export', methods=['GET'])
@login_required
def export_images():
    category = request.args.get('category', '')
    images = Image.query.filter_by(user_id=current_user.id)
    if category:
        images = images.filter_by(category=category)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for img in images:
            # For simplicity, just add URLs or download images
            zip_file.writestr(f"{img.id}.txt", f"URL: {img.url}\nDesc: {img.desc}\nDate: {img.date}\nTags: {img.tags}")
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='export.zip', mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
