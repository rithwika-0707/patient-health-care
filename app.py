from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)


# ==============================
# DATABASE
# ==============================

def get_db():
    conn = sqlite3.connect("patient.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# REGISTER / SAVE PATIENT
# ==============================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    phone = data.get("phone")
    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")

    if not phone or not name or not age or not gender:

        return jsonify({
            "success": False,
            "message": "Please enter all patient details."
        }), 400

    conn = get_db()

    try:

        conn.execute("""
            INSERT INTO patients
            (phone, name, age, gender)
            VALUES (?, ?, ?, ?)
        """, (phone, name, age, gender))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Patient registered successfully."
        })

    except sqlite3.IntegrityError:

        # If phone already exists, update the details
        conn.execute("""
            UPDATE patients
            SET name = ?, age = ?, gender = ?
            WHERE phone = ?
        """, (name, age, gender, phone))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Patient information updated successfully."
        })

    finally:

        conn.close()


# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    phone = data.get("phone")

    if not phone:

        return jsonify({
            "success": False,
            "message": "Please enter your phone number."
        }), 400

    conn = get_db()

    patient = conn.execute("""
        SELECT *
        FROM patients
        WHERE phone = ?
    """, (phone,)).fetchone()

    conn.close()

    if patient:

        return jsonify({

            "success": True,

            "patient": {

                "id": patient["id"],

                "phone": patient["phone"],

                "name": patient["name"],

                "age": patient["age"],

                "gender": patient["gender"]

            }

        })

    else:

        return jsonify({

            "success": False,

            "message": "Patient not found. Please register first."

        }), 404


# ==============================
# START FLASK
# ==============================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)