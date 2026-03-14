from flask import Flask, request, g
import sqlite3

app = Flask(__name__)
DATABASE = "learno_ai.db"

# ----- Database helper functions -----
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT,
            question TEXT
        )
    """)
    db.commit()

# ----- Subjects & Notes -----
subjects = ["Math","Physics","Biology","History","Chemistry","English"]

notes_db = {
    "math":"Math studies numbers, algebra, geometry and problem solving.",
    "physics":"Physics explains motion, force, energy and the laws of the universe.",
    "biology":"Biology studies living organisms, cells, plants and the human body.",
    "history":"History studies past civilizations and important world events.",
    "chemistry":"Chemistry studies atoms, molecules and chemical reactions.",
    "english":"English focuses on grammar, vocabulary, literature and communication."
}

quiz_db = {
    "math":"Quiz: What is 12 + 8 ?",
    "physics":"Quiz: What force pulls objects to Earth?",
    "biology":"Quiz: What is the basic unit of life?",
    "history":"Quiz: Which civilization built pyramids?",
    "chemistry":"Quiz: What is H2O commonly called?",
    "english":"Quiz: What is a noun?"
}

# ----- AI Agent -----
def ai_agent(question):
    q = question.lower()
    for subject in notes_db:
        if subject in q:
            return f"AI Explanation:\n{notes_db[subject]}\n\n{quiz_db[subject]}"
    return "AI Agent Response: I can help with Math, Physics, Biology, History, Chemistry and English."

# ----- Routes -----
@app.route("/")
def home():
    subject_cards = "".join([f"<div class='card'>{s}</div>" for s in subjects])
    html = f"""
    <html>
    <head>
    <title>Learno AI</title>
    <style>
        body {{ font-family:Arial; margin:0; background:#eef2ff; text-align:center; }}
        header {{ background:linear-gradient(90deg,#6a5cff,#3fd0d4); color:white; padding:40px; }}
        input {{ padding:10px; width:300px; }}
        button {{ padding:10px 20px; background:#4CAF50; color:white; border:none; border-radius:8px; cursor:pointer; }}
        .subjects {{ display:grid; grid-template-columns:repeat(3,1fr); gap:20px; padding:30px; }}
        .card {{ background:white; padding:20px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1); }}
        .premium {{ background:orange; color:white; padding:30px; margin:30px; border-radius:15px; }}
    </style>
    </head>
    <body>
    <header>
        <h1>Learno AI</h1>
        <p>Ask • Learn • Master</p>
        <form action="/ask" method="post">
            <input name="question" placeholder="Ask Learno AI">
            <input name="email" placeholder="Enter your email">
            <button type="submit">Ask AI</button>
        </form>
    </header>
    <h2>Subjects</h2>
    <div class="subjects">{subject_cards}</div>
    <h2>Premium Upgrade</h2>
    <div class="premium">
        <p>AI explanations • Notes • Quizzes</p>
        <p>Price: ₹100 / month</p>
        <p>UPI Payment: yourupi@bank</p>
    </div>
    </body>
    </html>
    """
    return html

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    email = request.form["email"]
    
    db = get_db()
    cursor = db.cursor()
    
    # Save student email
    cursor.execute("INSERT OR IGNORE INTO students(email) VALUES(?)", (email,))
    # Save question
    cursor.execute("INSERT INTO questions(student_email, question) VALUES(?,?)", (email, question))
    db.commit()
    
    answer = ai_agent(question)
    return f"""
    <h2>Your Question</h2>
    <p>{question}</p>
    <h2>Learno AI Agent Answer</h2>
    <p>{answer}</p>
    <a href='/'>Ask another question</a>
    """

# ----- Run App -----
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
