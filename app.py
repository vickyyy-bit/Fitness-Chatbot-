from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from chatbot import get_chatbot_response
from auth import register_user, authenticate_user, reset_password 
from database import init_db, save_workout_preferences, get_user_id  
import json
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize the database
init_db()

# Load workouts from JSON
def load_workouts():
    with open("workouts.json", "r") as file:
        return json.load(file)

# Login Route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if authenticate_user(username, password):  
            session["user_id"] = get_user_id(username) 
            flash("Login successful!", "success")
            return redirect(url_for("workout_suggestion"))
        else:
            flash("Invalid credentials, try again.", "error")

    return render_template("index.html")

# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        re_password = request.form.get("re_password")

        if password != re_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("signup"))

        if register_user(username, email, password):  
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username or email already exists!", "error")

    return render_template("signup.html")

# Forgot Password Route
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        if reset_password(email):  
            flash("Password reset link sent!", "success")
        else:
            flash("Email not found!", "error")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")

@app.route("/workout_suggestion", methods=["GET", "POST"])
def workout_suggestion():
    if "user_id" not in session:
        flash("You must log in first!", "error")
        return redirect(url_for("login"))

    workouts = load_workouts()

    if request.method == "POST":
        goal = request.form.get("goal")
        target_muscle = request.form.get("target_muscle")
        location = request.form.get("location")

        # Debugging: Print form data
        print(f"Goal: {goal}, Target Muscle: {target_muscle}, Location: {location}")

        # Validate that all required fields are provided
        if not goal or not target_muscle or not location:
            flash("Please fill out all fields.", "error")
            return redirect(url_for("workout_suggestion"))

        # Save preferences to database
        user_id = session["user_id"]
        save_workout_preferences(user_id, goal, target_muscle, location)

        # Fetch workouts based on user preferences
        try:
            workout_list = workouts[location][goal][target_muscle]
            return render_template("workout_suggestion.html", workouts=workout_list, goal=goal, target_muscle=target_muscle, location=location)
        except KeyError:
            flash("No workouts found for the selected preferences.", "error")
            return render_template("workout_suggestion.html")

    return render_template("workout_suggestion.html")

# Chatbot Route
@app.route("/chatbot", methods=["GET"])
def chatbot():
    if "user_id" not in session:
        flash("You must log in first!", "error")
        return redirect(url_for("login"))
    return render_template("chatbot.html")

# Send Message to Chatbot API
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    chatbot_response = get_chatbot_response(user_message)
    return jsonify({"response": chatbot_response})

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)