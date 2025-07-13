from flask import Flask, request
import os
from waitress import serve
import json
import cv2
from pymongo import MongoClient, errors
from bson import Binary
from werkzeug.utils import secure_filename
from deepface import DeepFace

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/uploads"

DATASET_PATH = "face_recognition/dataset"
os.makedirs(DATASET_PATH, exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("database", exist_ok=True)

# --------------------
# MongoDB connection
# --------------------
MONGO_URI = "mongodb+srv://GokulV:gokul123@agentic.5vjdklj.mongodb.net/?retryWrites=true&w=majority&appName=Agentic"
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    db_connected = True
    db = client['voting_system']
    files_collection = db['files']
except errors.ServerSelectionTimeoutError as err:
    print("[ERROR] Could not connect to MongoDB:", err)
    db_connected = False
    db = None
    files_collection = None

# --------------------
# Helper: capture face image
# --------------------
def capture_face_image(save_path):
    cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    captured = False
    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face_img = img[y:y+h, x:x+w]
            cv2.imwrite(save_path, face_img)
            captured = True
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.imshow('Capture Face', img)
        if cv2.waitKey(100) & 0xFF == 27 or captured:
            break
    cam.release()
    cv2.destroyAllWindows()
    return captured

# --------------------
# Routes
# --------------------
@app.route('/')
def index():
    return '''
    <html><head><title>Voting System</title><style>
    body { font-family: Arial; background: #f4f4f4; text-align: center; padding: 50px;}
    h2 { color: #4CAF50; }
    a { display: inline-block; margin: 10px; padding: 12px 24px; background: #4CAF50; color: white;
        text-decoration: none; border-radius: 5px; }
    a:hover { background: #45a049; }
    </style></head><body>
    <h2>Voting System</h2>
    <a href="/register">Register</a>
    <a href="/vote">Vote</a>
    <a href="/leaderboard">Leaderboard</a>
    </body></html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        aadhar_file = request.files['aadhar_file']
        voter_file = request.files['voter_file']
        if db_connected:
            files_collection.insert_one({
                "voter_id": voter_id,
                "documents": {
                    "aadhar": Binary(aadhar_file.read()),
                    "aadhar_filename": secure_filename(aadhar_file.filename),
                    "voter_id_doc": Binary(voter_file.read()),
                    "voter_filename": secure_filename(voter_file.filename)
                }
            })
        users_file = 'database/users.json'
        if not os.path.exists(users_file):
            with open(users_file, 'w') as f: json.dump([], f)
        with open(users_file, 'r') as f:
            users = json.load(f)
        users.append({"voter_id": voter_id})
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=4)
        voter_img_path = os.path.join(DATASET_PATH, f"{voter_id}.jpg")
        captured = capture_face_image(voter_img_path)
        if captured:
            return f"<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:green;'>✅ Registered & captured face for {voter_id}.</h3><a href='/'>Home</a></body></html>"
        else:
            return "<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:red;'>❌ Could not capture face. Try again.</h3></body></html>"
    return '''
    <html><head><title>Register</title><style>
    body { font-family: Arial; background: #f4f4f4; padding: 20px;}
    h2 { text-align: center; color: #4CAF50; }
    form { background: white; padding: 20px; margin: auto; width: 400px; border-radius: 8px; box-shadow:0 0 10px rgba(0,0,0,0.1);}
    input, button { width: calc(100% - 20px); padding:10px; margin:8px 0; border:1px solid #ccc; border-radius:4px;}
    button { background: #4CAF50; color: white; cursor:pointer; }
    button:hover { background: #45a049; }
    </style></head><body>
    <h2>Register</h2>
    <form method="POST" enctype="multipart/form-data">
        Voter ID: <input type="text" name="voter_id" required><br>
        Aadhar File: <input type="file" name="aadhar_file" required><br>
        Voter ID File: <input type="file" name="voter_file" required><br>
        <button type="submit">Register</button>
    </form>
    </body></html>
    '''

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        with open('database/users.json', 'r') as f:
            users = json.load(f)
        if not any(u['voter_id'] == voter_id for u in users):
            return "<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:red;'>❌ Not registered. Please register first.</h3></body></html>"
        voted_file = 'database/voted_users.json'
        if not os.path.exists(voted_file):
            with open(voted_file, 'w') as f: json.dump([], f)
        with open(voted_file, 'r') as f:
            voted_users = json.load(f)
        if voter_id in voted_users:
            return "<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:red;'>🛑 You have already voted.</h3></body></html>"
        known_path = os.path.join(DATASET_PATH, f"{voter_id}.jpg")
        if not os.path.exists(known_path):
            return "<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:red;'>😔 No registered face found. Register again.</h3></body></html>"
        verify_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{voter_id}_verify.jpg")
        capture_face_image(verify_path)
        try:
            result = DeepFace.verify(verify_path, known_path, enforce_detection=False)
            if result["verified"]:
                return f'''
                <html><body style='font-family:Arial;background:#f4f4f4;padding:20px;'>
                <h2 style='text-align:center;color:green;'>Face Verified ✅. Cast your vote:</h2>
                <form style='background:white;padding:20px;margin:auto;width:400px;border-radius:8px;box-shadow:0 0 10px rgba(0,0,0,0.1);' method="POST" action="/cast_vote">
                    <input type="hidden" name="voter_id" value="{voter_id}">
                    <input type="radio" name="candidate" value="Alice" required> Alice<br>
                    <input type="radio" name="candidate" value="Bob"> Bob<br>
                    <input type="radio" name="candidate" value="Charlie"> Charlie<br><br>
                    <button type="submit" style='background:#4CAF50;color:white;padding:10px;border:none;border-radius:5px;width:100%;'>Vote</button>
                </form>
                </body></html>'''
            else:
                return "<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:red;'>❌ Face verification failed. Try again.</h3></body></html>"
        except Exception as e:
            return f"<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:red;'>⚠ Error in face verification: {e}</h3></body></html>"
    return '''
    <html><head><title>Vote</title><style>
    body { font-family: Arial; background: #f4f4f4; padding: 20px;}
    h2 { text-align: center; color: #4CAF50;}
    form { background: white; padding: 20px; margin: auto; width: 400px; border-radius: 8px; box-shadow:0 0 10px rgba(0,0,0,0.1);}
    input, button { width: calc(100% - 20px); padding:10px; margin:8px 0; border:1px solid #ccc; border-radius:4px;}
    button { background: #4CAF50; color: white; cursor:pointer; }
    button:hover { background: #45a049; }
    </style></head><body>
    <h2>Enter Voter ID to Vote</h2>
    <form method="POST">
        <input type="text" name="voter_id" required>
        <button type="submit">Verify & Vote</button>
    </form>
    </body></html>
    '''

@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    voter_id = request.form['voter_id']
    candidate = request.form['candidate']
    votes_file = 'database/votes.json'
    if not os.path.exists(votes_file):
        with open(votes_file, 'w') as f: json.dump({"Alice": 0, "Bob": 0, "Charlie": 0}, f)
    with open(votes_file, 'r') as f:
        votes = json.load(f)
    votes[candidate] += 1
    with open(votes_file, 'w') as f:
        json.dump(votes, f, indent=4)
    with open('database/voted_users.json', 'r') as f:
        voted_users = json.load(f)
    voted_users.append(voter_id)
    with open('database/voted_users.json', 'w') as f:
        json.dump(voted_users, f, indent=4)
    return f"<html><body style='font-family:Arial;text-align:center;padding:50px;'><h3 style='color:green;'>✅ Vote recorded for {candidate}. Thank you!</h3><a style='color:#4CAF50;' href='/leaderboard'>View Leaderboard</a></body></html>"

@app.route('/leaderboard')
def leaderboard():
    if not os.path.exists('database/votes.json'):
        return "<html><body style='font-family:Arial;text-align:center;padding:50px;'><h2>No votes yet.</h2></body></html>"
    with open('database/votes.json', 'r') as f:
        votes = json.load(f)
    html = "<html><body style='font-family:Arial;background:#f4f4f4;padding:20px;'><h2 style='text-align:center;color:#4CAF50;'>Leaderboard</h2>"
    for candidate, count in votes.items():
        html += f"<p style='text-align:center;font-size:18px;'>{candidate}: {count} votes</p>"
    html += '<p style="text-align:center;"><a style="color:#4CAF50;" href="/">Home</a></p></body></html>'
    return html

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=5000)
