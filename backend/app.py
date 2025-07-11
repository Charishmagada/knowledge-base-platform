from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Document
from pytz import timezone
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configurations
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///knowledge.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
jwt = JWTManager(app)

# ----------------------------------
# DB Create
# ----------------------------------
with app.app_context():
    db.create_all()

# ----------------------------------
# Register
# ----------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 409

    hashed_pw = generate_password_hash(password)
    user = User(email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Registered successfully"}), 201

# ----------------------------------
# Login
# ----------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.email)
    return jsonify(access_token=access_token), 200

# ----------------------------------
# Create Document
# ----------------------------------
@app.route("/document", methods=["POST"])
@jwt_required()
def create_document():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    data = request.json
    title = data.get("title")
    content = data.get("content")
    is_public = data.get("is_public", False)

    if not title or not content:
        return jsonify({"msg": "Title and content are required"}), 400

    doc = Document(title=title, content=content, is_public=is_public, author_id=user.id)
    db.session.add(doc)
    db.session.commit()
    return jsonify({"msg": "Document created"}), 201

# ----------------------------------
# Get Documents
# ----------------------------------
@app.route("/documents", methods=["GET"])
@jwt_required()
def get_documents():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    docs = Document.query.filter_by(author_id=user.id).all()

    ist = timezone('Asia/Kolkata')

    return jsonify([
        {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "is_public": doc.is_public,
            "created_at": doc.created_at.astimezone(ist).strftime("%Y-%m-%d %I:%M:%S %p") if doc.created_at else None,
            "updated_at": doc.updated_at.astimezone(ist).strftime("%Y-%m-%d %I:%M:%S %p") if doc.updated_at else None,
            "author": user.email
        }
        for doc in docs
    ]), 200

# ----------------------------------
# Search Documents
# ----------------------------------
@app.route("/search", methods=["GET"])
@jwt_required()
def search_documents():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    query = request.args.get("q", "")

    docs = Document.query.filter(
        Document.author_id == user.id,
        Document.title.ilike(f"%{query}%")
    ).all()

    ist = timezone('Asia/Kolkata')

    return jsonify([
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "author": user.email,
            "created_at": d.created_at.astimezone(ist).strftime("%Y-%m-%d %I:%M:%S %p") if d.created_at else None,
            "updated_at": d.updated_at.astimezone(ist).strftime("%Y-%m-%d %I:%M:%S %p") if d.updated_at else None,
            "is_public": d.is_public
        }
        for d in docs
    ]), 200

# ----------------------------------
# Update Document
# ----------------------------------
@app.route("/document/<int:doc_id>", methods=["PUT"])
@jwt_required()
def update_document(doc_id):
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    doc = Document.query.filter_by(id=doc_id, author_id=user.id).first()
    if not doc:
        return jsonify({"msg": "Document not found"}), 404

    data = request.json
    doc.title = data.get("title", doc.title)
    doc.content = data.get("content", doc.content)
    doc.is_public = data.get("is_public", doc.is_public)
    db.session.commit()

    return jsonify({"msg": "Document updated"}), 200

# ----------------------------------
# Delete Document
# ----------------------------------
@app.route("/document/<int:doc_id>", methods=["DELETE"])
@jwt_required()
def delete_document(doc_id):
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    doc = Document.query.filter_by(id=doc_id, author_id=user.id).first()
    if not doc:
        return jsonify({"msg": "Document not found"}), 404

    db.session.delete(doc)
    db.session.commit()
    return jsonify({"msg": "Document deleted"}), 200

# ----------------------------------
# Root Health Check
# ----------------------------------
@app.route("/", methods=["GET"])
def home():
    return "Flask backend is running", 200

if __name__ == "__main__":
    app.run(debug=True)
