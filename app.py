from datetime import datetime
from flask import Flask, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import validators
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    data = request.get_json()
    original_url = data.get('url')

    if not original_url:
        return jsonify({'error': 'URL is required'}), 400

    if not validators.url(original_url):
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

@app.route('/shorten/<short_code>', methods=['GET'])
def get_short_url(short_code):
    url_entry = ShortURL.query.filter_by(short_code=short_code).first()
    if not url_entry:
        return jsonify({'error': 'Short URL not found'}), 404

    return jsonify({
        'id': url_entry.id,
        'url': url_entry.original_url,
        'shortCode': url_entry.short_code,
        'createdAt': url_entry.created_at.isoformat(),
        'updatedAt': url_entry.updated_at.isoformat()
    }), 200

@app.route('/shorten/<short_code>', methods=['PUT'])
def update_short_url(short_code):
    url_entry = ShortURL.query.filter_by(short_code=short_code).first()
    if not url_entry:
        return jsonify({'error': 'Short URL not found'}), 404

    data = request.get_json()
    new_url = data.get('url')

    if not new_url:
        return jsonify({'error': 'URL is required'}), 400

    if not validators.url(new_url):
        return jsonify({'error': 'Invalid URL'}), 400

    url_entry.original_url = new_url
    url_entry.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'id': url_entry.id,
        'url': url_entry.original_url,
        'shortCode': url_entry.short_code,
        'createdAt': url_entry.created_at.isoformat(),
        'updatedAt': url_entry.updated_at.isoformat()
    }), 200

@app.route('/shorten/<short_code>', methods=['DELETE'])
def delete_short_url(short_code):
    url_entry = ShortURL.query.filter_by(short_code=short_code).first()
    if not url_entry:
        return jsonify({'error': 'Short URL not found'}), 404

    db.session.delete(url_entry)
    db.session.commit()
    return '', 204

@app.route('/shorten/<short_code>/stats', methods=['GET'])
def get_stats(short_code):
    url_entry = ShortURL.query.filter_by(short_code=short_code).first()
    if not url_entry:
        return jsonify({'error': 'Short URL not found'}), 404

    return jsonify({
        'id': url_entry.id,
        'url': url_entry.original_url,
        'shortCode': url_entry.short_code,
        'createdAt': url_entry.created_at.isoformat(),
        'updatedAt': url_entry.updated_at.isoformat(),
        'accessCount': url_entry.access_count
    }), 200

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url_entry = ShortURL.query.filter_by(short_code=short_code).first()
    if not url_entry:
        return jsonify({'error': 'Short URL not found'}), 404

    url_entry.access_count += 1
    db.session.commit()
    return redirect(url_entry.original_url, code=301)

if __name__ == '__main__':
    app.run(debug=True)
