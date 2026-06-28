import streamlit as st
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import io
import os
import textwrap


DB_NAME = "employees.db"


# ================= DATABASE =================

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        emp_id TEXT PRIMARY KEY,
        name TEXT,
        designation TEXT,
        role TEXT,
        email TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("SELECT * FROM users WHERE username=?", ("admin",))

    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO users VALUES(?,?,?)
        """, ("admin", "admin@123", "ADMIN"))

    conn.commit()
    conn.close()


# ================= LOGIN =================

def login_user(username, password):

    conn = get_connection()

    result = conn.execute("""
        SELECT role FROM users
        WHERE username=? AND password=?
    """, (username, password)).fetchone()

    conn.close()

    return result


# ================= MESSAGE =================

def generate_message(name, designation, role):

    return f"""
Dear {name},

We truly appreciate your excellent contribution as {designation}.

Your dedication, commitment and consistent efforts in the {role} role
have created a positive impact.

Your valuable contribution and support are highly appreciated.

Thank you for your continued efforts.
"""


# ================= CARD DESIGN =================

def create_card(boss_photo, employee_photo, name, message):

    card = Image.new("RGB", (1400, 900), "white")
    draw = ImageDraw.Draw(card)

    # Fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 50)
        text_font = ImageFont.truetype("arial.ttf", 30)
        small_font = ImageFont.truetype("arial.ttf", 26)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # ================= BORDER DESIGN =================
    border_color = (0, 102, 204)
    draw.rectangle([(10, 10), (1390, 890)], outline=border_color, width=8)
    draw.rectangle([(25, 25), (1375, 875)], outline=(200, 200, 200), width=2)

    # Title
    draw.text((500, 40), "Appreciation Note", font=title_font, fill="black")

    # Resize images
    boss_photo = boss_photo.resize((250, 250))
    employee_photo = employee_photo.resize((250, 250))

    # Paste images
    card.paste(boss_photo, (100, 250))
    card.paste(employee_photo, (1050, 250))

    # Message box
    wrapped_text = textwrap.fill(message, 45)
    draw.multiline_text((400, 250), wrapped_text, font=text_font, spacing=10, fill="black")

    # Signature (UPDATED)
    draw.text(
        (100, 650),
        "From:\nDr. Damodharen M\nChief Digital Officer",
        font=small_font,
        fill="black"
    )

    return card


# ================= EMPLOYEE MANAGEMENT =================

def employee_management():

    st.subheader("Employee Management")

    option = st.selectbox("Action", ["Add Employee", "View Employees"])

    if option == "Add Employee":

        with st.form("emp"):

            emp_id = st.text_input("Employee ID")
            name = st.text_input("Name")
            designation = st.text_input("Designation")
            role = st.text_input("Role")
            email = st.text_input("Email")

            submit = st.form_submit_button("Save")

            if submit:

                conn = get_connection()

                conn.execute("""
                    INSERT OR REPLACE INTO employees VALUES(?,?,?,?,?)
                """, (emp_id, name, designation, role, email))

                conn.commit()
                conn.close()

                st.success("Employee Saved")

    else:

        conn = get_connection()
        data = conn.execute("SELECT * FROM employees").fetchall()
        conn.close()

        st.table(data)


# ================= USER MANAGEMENT =================

def user_management():

    st.subheader("User Management")

    username = st.text_input("Username")
    password = st.text_input("Password")

    role = st.selectbox("Role", ["USER", "ADMIN"])

    if st.button("Create User"):

        conn = get_connection()

        conn.execute("""
            INSERT OR REPLACE INTO users VALUES(?,?,?)
        """, (username, password, role))

        conn.commit()
        conn.close()

        st.success("User Created")

    if st.checkbox("View Users"):

        conn = get_connection()
        data = conn.execute("SELECT * FROM users").fetchall()
        conn.close()

        st.table(data)


# ================= GREETING GENERATOR =================

def greeting_generator():

    st.subheader("Greeting Generator")

    emp_id = st.text_input("Enter Employee ID")

    if emp_id:

        conn = get_connection()

        employee = conn.execute("""
            SELECT name, designation, role
            FROM employees
            WHERE emp_id=?
        """, (emp_id,)).fetchone()

        conn.close()

        if employee:

            name, designation, role = employee

            st.success(f"Employee Found: {name}")
            st.write("Designation:", designation)
            st.write("Role:", role)

            # ================= FIX: ONLY ONE OPTION =================
            photo_option = st.radio(
                "Select Photo Source",
                ["Upload Photo", "Take Selfie"]
            )

            final_photo = None

            if photo_option == "Upload Photo":
                final_photo = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

            else:
                final_photo = st.camera_input("Capture Selfie")

            if final_photo:

                if st.button("Generate Greeting Card"):

                    boss_path = os.path.join("assets", "boss_photo.jpg")

                    if not os.path.exists(boss_path):
                        st.error("boss_photo.jpg missing in assets folder")
                        return

                    boss = Image.open(boss_path)
                    employee_img = Image.open(final_photo)

                    card = create_card(
                        boss,
                        employee_img,
                        name,
                        generate_message(name, designation, role)
                    )

                    st.image(card)

                    buffer = io.BytesIO()
                    card.save(buffer, format="PNG")

                    st.download_button(
                        "Download Greeting Card",
                        buffer.getvalue(),
                        "greeting.png",
                        "image/png"
                    )

        else:
            st.error("Employee not found")


# ================= MAIN =================

create_tables()

st.set_page_config(
    page_title="Employee Recognition V2",
    layout="wide"
)

if "login" not in st.session_state:
    st.session_state.login = False


if not st.session_state.login:

    st.title("Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):

        result = login_user(u, p)

        if result:
            st.session_state.login = True
            st.session_state.role = result[0]
            st.rerun()

        else:
            st.error("Invalid Login")

else:

    if st.sidebar.button("Logout"):
        st.session_state.login = False
        st.rerun()

    if st.session_state.role == "ADMIN":

        t1, t2, t3 = st.tabs([
            "Employee Management",
            "User Management",
            "Greeting Generator"
        ])

        with t1:
            employee_management()

        with t2:
            user_management()

        with t3:
            greeting_generator()

    else:
        greeting_generator()