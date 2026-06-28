import streamlit as st
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import io
import os
import textwrap


DB_NAME = "employees.db"

# ================= UI FONT (SAFE ONLY IMPROVEMENT) =================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 18px !important;
}

h1 {
    font-size: 40px !important;
}

h2 {
    font-size: 30px !important;
}

.stButton button {
    font-size: 16px !important;
    padding: 8px 16px !important;
}
</style>
""", unsafe_allow_html=True)


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

Your dedication, commitment and consistent efforts in the {role} role have created a positive impact.

Thank you for your continued efforts.
"""


# ================= CARD =================

def create_card(boss_photo, employee_photo, name, message):

    card = Image.new("RGB", (1400, 900), "white")
    draw = ImageDraw.Draw(card)

    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        text_font = ImageFont.truetype("arial.ttf", 34)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    draw.text((380, 50), "APPRECIATION NOTE", font=title_font, fill="black")

    boss_photo = boss_photo.resize((250, 250))
    employee_photo = employee_photo.resize((250, 250))

    card.paste(boss_photo, (100, 250))
    card.paste(employee_photo, (1050, 250))

    draw.multiline_text(
        (420, 250),
        textwrap.fill(message, 35),
        font=text_font,
        spacing=12,
        fill="black"
    )

    draw.text(
        (120, 600),
        "From:\nManagement Team",
        font=text_font,
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


# ================= GREETING GENERATOR (FIXED PHOTO FLOW) =================

def greeting_generator():

    st.subheader("Greeting Generator")

    emp_id = st.text_input("Enter Employee ID")

    if emp_id:

        conn = get_connection()
        employee = conn.execute("""
            SELECT name,designation,role
            FROM employees
            WHERE emp_id=?
        """, (emp_id,)).fetchone()
        conn.close()

        if employee:

            name, designation, role = employee

            st.success(f"Employee Found: {name}")
            st.write("Designation:", designation)
            st.write("Role:", role)

            # ================= PHOTO FLOW FIX =================

            photo_option = st.radio(
                "Choose Photo Option",
                ["Upload Photo", "Take Selfie"]
            )

            final_photo = None

            if photo_option == "Upload Photo":

                final_photo = st.file_uploader(
                    "Upload Photo",
                    type=["jpg", "jpeg", "png"]
                )

            else:

                st.info("Take selfie and confirm before using it")

                camera_photo = st.camera_input("Take Selfie")

                if camera_photo:

                    st.image(camera_photo, caption="Preview")

                    confirm = st.checkbox("Confirm this photo")

                    if confirm:
                        final_photo = camera_photo
                    else:
                        st.warning("Uncheck and retake if needed")

            # ================= CARD GENERATION =================

            if final_photo:

                if st.button("Generate Greeting Card"):

                    boss_path = os.path.join("assets", "boss_photo.jpg")

                    if not os.path.exists(boss_path):
                        st.error("boss_photo.jpg missing in assets")
                        return

                    boss = Image.open(boss_path)
                    employee_photo = Image.open(final_photo)

                    card = create_card(
                        boss,
                        employee_photo,
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