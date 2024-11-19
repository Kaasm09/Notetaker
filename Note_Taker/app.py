import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from HTR.htr import inference
import numpy as np
import cv2

from helpers import login_required, flash_message
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['DEBUG'] = True
Session(app)
con = sqlite3.connect("notetaker.db", check_same_thread=False)
db = con.cursor()



@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session["username"])

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        # error handling
        if not username:
            return flash_message("Please input a username", "register")
        if not password:
            return flash_message("Please input a password", "register")
        if not confirm:
            return flash_message("Please confirm your password", "register")
        if not password == confirm:
            return flash_message("These password do not match", "register")
        if len(db.execute("SELECT * FROM users WHERE username = ?", username)) > 0:
            return flash_message("This username is already in use", "register")
        
        db.execute("INSERT into users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        row = db.execute("SELECT hash, id FROM users WHERE username = ?", [username])
        # error handling
        if not username:
            return flash_message("Please input a username", "login")
        if not password:
            return flash_message("Please input a password", "login")
        if row.count() != 1:
            return flash_message("The username you entered does not exist", "login")
        if not check_password_hash(row[0]["hash"], password):
            return flash_message("The username or password your entered is incorrect", "login")
        session["user_id"] = row[0]["id"]
        session["username"] = username
        return redirect(url_for("index"))
    
@app.route("/New_Note", methods=["GET", "POST"])
@login_required
def new_note():
    if request.method == "GET":
        return render_template("new_note.html")
    else:
        try:
            data = request.json
        except:
            print('error')
        try:
            image_data = data["image_data"]
            canvas_height = data["canvas_height"]
            canvas_width = data["canvas_width"]
            image_data = np.uint8(np.array(image_data).reshape(canvas_height, canvas_width, 4))
            black_indices = np.all(image_data == [0, 0, 0, 0], axis=-1)
            image_data[black_indices] = [255, 255, 255, 255]
            image_data = cv2.cvtColor(image_data, cv2.COLOR_RGBA2BGR)
            text = inference(image_data)
            print('sending response')
            return jsonify({ "text" : text})
        except:
            textarea_data = data["textarea_data"]
            canvas_data = data["canvas_data"]
            canvas_name = data["canvas_name"]
            db.execute("INSERT into notes (user_id, textareas, canvas) VALUES (?, ?, ?)", session["user_id"], str(textarea_data), str(canvas_data))
            return jsonify({'hello': 'hello'})  


@app.route("/Load_Note", methods=["GET", "POST"])
@login_required
def load_note():
    if request.method == "GET":
        return render_template("new_note.html", names=db.execute("SELECT names FROM notes"))
    else:
        try:
            data = request.json
        except:
            print('error')

if __name__ == "__main__":
    app.run(debug=True)