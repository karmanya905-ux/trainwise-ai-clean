from flask import Flask, render_template, request, redirect, session
from app.ai.ollama_client import generate_workout
from ai.ollama_client import generate_workout, ask_coach
from database import init_db
from flask import redirect
from weight_service import add_weight, get_weights
from flask import send_file
from reportlab.pdfgen import canvas
import io
from sklearn.linear_model import LinearRegression
import numpy as np
import os

app = Flask(__name__)
app.secret_key = "fitgen_secret_key"

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    bmi = None
    maintenance = None
    goal_calories = None
    protein = None

    if request.method == "POST":
        age = int(request.form.get("age"))
        height = float(request.form.get("height"))
        weight = float(request.form.get("weight"))
        goal = request.form.get("goal")
        experience = request.form.get("experience")
        workout_type = request.form.get("workout_type")
        diet = request.form.get("diet")
	
        session["weight"] = weight
        session["goal"] = goal
        session["diet"] = diet
        session["experience"] = experience
        session["workout_type"] = workout_type
        session["height"] = height
        session["age"] = age

        bmi = round(weight / ((height / 100) ** 2), 1)

        maintenance = int(weight * 33)

        if goal == "fat loss":
            goal_calories = maintenance - 400
        elif goal == "muscle gain":
            goal_calories = maintenance + 250
        else:
            goal_calories = maintenance

        protein = int(weight * 2)

        result = generate_workout(
            age, height, weight, goal,
            experience, workout_type, diet,
            goal_calories, protein
        )

    return render_template(
        "index.html",
        result=result,
        bmi=bmi,
        maintenance=maintenance,
        goal_calories=goal_calories,
        protein=protein
    )


@app.route("/tracker", methods=["GET", "POST"])
def tracker():

    if request.method == "POST":
        weight = float(request.form.get("weight"))
        add_weight(weight)
        return redirect("/tracker")

    rows = get_weights()

    dates = [row[0][:10] for row in rows]
    weights = [row[1] for row in rows]

    start_weight = None
    current_weight = None
    change = None
    status = None
    badge = None
    predicted_weight = None

    if len(weights) > 0:
        start_weight = weights[0]
        current_weight = weights[-1]
        change = round(current_weight - start_weight, 1)

        if change < -0.5:
            status = "Good progress 🔥"
        elif change < 0:
            status = "Slow steady progress ✅"
        elif change == 0:
            status = "Stable ⚖️"
        else:
            status = "Weight increased 📈"
        if len(weights) >= 7:
            badge = "🔥 Consistency Warrior"

        if change is not None and change < -2:
            badge = "🏆 Fat Loss Machine"

        elif change is not None and change < -0.5:
            badge = "📉 Progress Starter"
        
        if len(weights) >= 3:
            X = np.array(range(len(weights))).reshape(-1, 1)
            y = np.array(weights)

            model = LinearRegression()
            model.fit(X, y)

            next_day = np.array([[len(weights)]])
            predicted_weight = round(model.predict(next_day)[0], 1)

    return render_template(
        "tracker.html",
        dates=dates,
        weights=weights,
        rows=rows,
        start_weight=start_weight,
        current_weight=current_weight,
        change=change,
        status=status,
        badge = badge,
        predicted_weight=predicted_weight
    )

@app.route("/coach", methods=["GET", "POST"])
def coach():

    answer = None

    if request.method == "POST":
        question = request.form.get("question")

        profile = f"""
User Profile:
Age: {session.get('age')}
Height: {session.get('height')} cm
Weight: {session.get('weight')} kg
Goal: {session.get('goal')}
Experience: {session.get('experience')}
Workout Type: {session.get('workout_type')}
Diet: {session.get('diet')}
"""

        answer = ask_coach(profile + "\nUser Question: " + question)

    return render_template("coach.html", answer=answer)
@app.route("/mealplanner", methods=["GET", "POST"])
def mealplanner():

    meal_plan = None

    if request.method == "POST":
        goal = request.form.get("goal")
        calories = request.form.get("calories")
        diet = request.form.get("diet")
        meals = request.form.get("meals")

        prompt = f"""
Create a personalized fitness meal plan.

User details:
Goal: {goal}
Calories target: {calories}
Diet: {diet}
Meals per day: {meals}

Generate:
- breakfast
- lunch
- dinner
- snacks
- approximate macros

Keep practical and concise.
"""

        meal_plan = ask_coach(prompt)

    return render_template("mealplanner.html", meal_plan=meal_plan)


@app.route("/download-plan")
def download_plan():

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(100, 800, "TrainWise AI Fitness Plan")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 760, f"Goal: {session.get('goal')}")
    pdf.drawString(100, 735, f"Weight: {session.get('weight')} kg")
    pdf.drawString(100, 710, f"Diet: {session.get('diet')}")
    pdf.drawString(100, 685, f"Workout Type: {session.get('workout_type')}")

    pdf.drawString(100, 640, "Generated by TrainWise AI")

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="trainwise_plan.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
