from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

documents = []
users = {}  # simple in-memory user store


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400
    if email in users:
        return jsonify({"msg": "User already exists"}), 409
    users[email] = password
    return jsonify({"msg": "User registered"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if users.get(email) != password:
        return jsonify({"msg": "Invalid credentials"}), 401
    token = create_access_token(identity=email)
    return jsonify(access_token=token), 200


@app.route("/document", methods=["POST"])
@jwt_required()
def create_document():
    user = get_jwt_identity()
    data = request.json
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"msg": "Title and content are required"}), 400

    doc = {
        "id": len(documents) + 1,
        "title": title,
        "content": content,
        "author": user,
    }
    documents.append(doc)
    return jsonify(doc), 201


@app.route("/documents", methods=["GET"])
@jwt_required()
def get_documents():
    user = get_jwt_identity()
    user_docs = [doc for doc in documents if doc["author"] == user]
    return jsonify(user_docs), 200


@app.route("/search", methods=["GET"])
@jwt_required()
def search_documents():
    query = request.args.get("q", "").lower()
    user = get_jwt_identity()
    matches = [
        doc for doc in documents
        if doc["author"] == user and (
            query in doc["title"].lower() or query in doc["content"].lower()
        )
    ]
    return jsonify(matches), 200


@app.route("/document/<int:doc_id>", methods=["PUT"])
@jwt_required()
def update_document(doc_id):
    user = get_jwt_identity()
    for doc in documents:
        if doc["id"] == doc_id and doc["author"] == user:
            data = request.json
            doc["title"] = data.get("title", doc["title"])
            doc["content"] = data.get("content", doc["content"])
            return jsonify(doc), 200
    return jsonify({"msg": "Document not found"}), 404

@app.route("/document/<int:doc_id>", methods=["DELETE"])
@jwt_required()
def delete_document(doc_id):
    user = get_jwt_identity()
    print(f"User trying to delete doc ID: {doc_id}, Current user: {user}")
    print("Current docs in memory:", documents)

    for i, doc in enumerate(documents):
        print(f"Checking document: {doc}")
        if doc["id"] == doc_id and doc["author"] == user:
            del documents[i]
            print(f"Deleted document ID: {doc_id}")
            return jsonify({"msg": "Document deleted"}), 200

    print("Document not found or unauthorized")
    return jsonify({"msg": "Document not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
