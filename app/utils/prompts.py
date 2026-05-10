def workout_prompt(age, height, weight, goal, experience, workout_type, diet, calories, protein):
    return f"""
You are an expert coach.

Create a plan using THESE exact numbers:

Calories Target: {calories}
Protein Target: {protein} grams

User:
Age {age}
Height {height}
Weight {weight}
Goal {goal}
Experience {experience}
Workout {workout_type}
Diet {diet}

Give:

1. Calories Target
2. Protein Target
3. Full 3-Day Workout Plan
4. 1-Day Diet Plan
5. 3 Tips

Do NOT change calories or protein numbers.
Keep concise.
"""