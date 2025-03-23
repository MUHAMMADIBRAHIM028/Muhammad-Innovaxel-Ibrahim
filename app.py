from datetime import datetime
from flask import Flask, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import string


from validators import is_valid_url
import logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
description = db.Column(db.String(256), nullable=True)

class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(6), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    access_count = db.Column(db.Integer, default=0)
   
    def __repr__(self):
        return f'<ShortURL {self.short_code}>'

with app.app_context():
    db.create_all()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/shorten', methods=['POST'])
def create_short_url():
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format'}), 400


    # URL validation using the function imported from validators.py
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400

    if not is_valid_url(original_url):  # This is where the refactored validation happens
        return jsonify({'error': 'Invalid URL'}), 400

    short_code = generate_short_code()
    while ShortURL.query.filter_by(short_code=short_code).first() is not None:
        short_code = generate_short_code()

    new_url = ShortURL(original_url=original_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        'id': new_url.id,
        'url': new_url.original_url,
        'shortCode': new_url.short_code,
        'createdAt': new_url.created_at.isoformat(),
        'updatedAt': new_url.updated_at.isoformat()
    }), 201

# Other routes...

