import streamlit as st
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import io
import os
import textwrap


DB_NAME = "employees.db"


# ================= STREAMLIT UI =================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-size: 18px !important;
}


[data-testid="stImage"] {
    width: 100% !important;
}


.block-container {
    max-width: 95% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
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


    cur.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )


    if cur.fetchone() is None:

        cur.execute(
        """
        INSERT INTO users VALUES(?,?,?)
        """,
        ("admin","admin@123","ADMIN")
        )


    conn.commit()
    conn.close()



# ================= LOGIN =================

def login_user(username,password):

    conn=get_connection()

    result=conn.execute(
    """
    SELECT role FROM users
    WHERE username=? AND password=?
    """,
    (username,password)

    ).fetchone()


    conn.close()

    return result



# ================= MESSAGE =================

def generate_message(name,designation,role):

    return f"""

Dear {name},

We truly appreciate your excellent contribution as {designation}.

Your dedication, commitment and consistent efforts in the {role} role have created a positive impact.

Thank you for your continued efforts.

"""



# ================= UPDATED CARD DESIGN ONLY =================


def create_card(boss_photo, employee_photo, name, message):

    card = Image.new(
        "RGB",
        (1200,750),
        "#FAF8F2"
    )

    draw = ImageDraw.Draw(card)


    try:

        title_font = ImageFont.truetype(
            "arialbd.ttf",65
        )

        body_font = ImageFont.truetype(
            "arial.ttf",32
        )

        name_font = ImageFont.truetype(
            "arialbd.ttf",30
        )

        small_font = ImageFont.truetype(
            "arial.ttf",26
        )


    except:

        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        small_font = ImageFont.load_default()



    # BORDER

    draw.rounded_rectangle(
        (15,15,1185,735),
        radius=25,
        outline="#C99A2E",
        width=6
    )



    # TITLE

    title="APPRECIATION NOTE"

    box=draw.textbbox(
        (0,0),
        title,
        font=title_font
    )


    draw.text(
        (
        (1200-(box[2]-box[0]))/2,
        35
        ),
        title,
        font=title_font,
        fill="#162447"
    )



    # PHOTOS

    boss_photo=boss_photo.resize(
        (230,230)
    )


    employee_photo=employee_photo.resize(
        (230,230)
    )



    card.paste(
        boss_photo,
        (70,180)
    )


    card.paste(
        employee_photo,
        (900,180)
    )



    # LEFT TEXT

    draw.multiline_text(
        (70,430),
        "From:\nDr. Damodharen M\nChief Digital Officer",
        font=small_font,
        spacing=8,
        fill="#162447"
    )



    # RIGHT TEXT

    draw.multiline_text(
        (900,430),
        f"To:\n{name}",
        font=name_font,
        spacing=10,
        fill="#162447"
    )



    # MESSAGE CENTER

    clean_message=message.replace(
        "\n",
        " "
    )


    lines=textwrap.wrap(
        clean_message,
        width=34
    )


    y=200


    for line in lines:


        box=draw.textbbox(
            (0,0),
            line,
            font=body_font
        )


        w=box[2]-box[0]


        draw.text(
            (
            (1200-w)/2,
            y
            ),
            line,
            font=body_font,
            fill="#222222"
        )


        y += 45



    return card


# ================= EMPLOYEE MANAGEMENT =================


def employee_management():

    st.subheader("Employee Management")


    option = st.selectbox(
        "Action",
        [
            "Add Employee",
            "View Employees"
        ]
    )


    if option == "Add Employee":


        with st.form("emp"):


            emp_id = st.text_input(
                "Employee ID"
            )


            name = st.text_input(
                "Name"
            )


            designation = st.text_input(
                "Designation"
            )


            role = st.text_input(
                "Role"
            )


            email = st.text_input(
                "Email"
            )


            submit = st.form_submit_button(
                "Save"
            )


            if submit:


                conn=get_connection()


                conn.execute(
                """
                INSERT OR REPLACE INTO employees
                VALUES(?,?,?,?,?)
                """,
                (
                emp_id,
                name,
                designation,
                role,
                email
                )
                )


                conn.commit()

                conn.close()


                st.success(
                    "Employee Saved"
                )


    else:


        conn=get_connection()


        data=conn.execute(
            "SELECT * FROM employees"
        ).fetchall()


        conn.close()


        st.table(data)




# ================= USER MANAGEMENT =================


def user_management():


    st.subheader(
        "User Management"
    )


    username=st.text_input(
        "Username"
    )


    password=st.text_input(
        "Password"
    )


    role=st.selectbox(
        "Role",
        [
        "USER",
        "ADMIN"
        ]
    )



    if st.button(
        "Create User"
    ):


        conn=get_connection()


        conn.execute(
        """
        INSERT OR REPLACE INTO users
        VALUES(?,?,?)
        """,
        (
        username,
        password,
        role
        )
        )


        conn.commit()

        conn.close()


        st.success(
            "User Created"
        )



    if st.checkbox(
        "View Users"
    ):


        conn=get_connection()


        data=conn.execute(
            "SELECT * FROM users"
        ).fetchall()


        conn.close()


        st.table(data)




# ================= GREETING GENERATOR =================


def greeting_generator():


    st.subheader(
        "Greeting Generator"
    )



    emp_id=st.text_input(
        "Enter Employee ID"
    )



    if emp_id:


        conn=get_connection()


        employee=conn.execute(
        """
        SELECT name,designation,role
        FROM employees
        WHERE emp_id=?
        """,
        (emp_id,)
        ).fetchone()


        conn.close()



        if employee:


            name,designation,role=employee



            st.success(
                f"Employee Found: {name}"
            )


            st.write(
                "Designation:",
                designation
            )


            st.write(
                "Role:",
                role
            )



            photo_option=st.radio(
                "Choose Photo Option",
                [
                "Upload Photo",
                "Take Selfie"
                ]
            )



            final_photo=None



            if photo_option=="Upload Photo":


                final_photo=st.file_uploader(
                    "Upload Photo",
                    type=[
                    "jpg",
                    "jpeg",
                    "png"
                    ]
                )


            else:


                camera_photo=st.camera_input(
                    "Take Selfie"
                )


                if camera_photo:


                    st.image(
                        camera_photo,
                        caption="Preview"
                    )


                    confirm=st.checkbox(
                        "Confirm this photo"
                    )


                    if confirm:


                        final_photo=camera_photo





            if final_photo:


                if st.button(
                    "Generate Greeting Card"
                ):



                    boss_path=os.path.join(
                        "assets",
                        "boss_photo.jpg"
                    )



                    if not os.path.exists(
                        boss_path
                    ):


                        st.error(
                            "boss_photo.jpg missing in assets"
                        )

                        return




                    boss=Image.open(
                        boss_path
                    )



                    employee_photo=Image.open(
                        final_photo
                    )



                    card=create_card(
                        boss,
                        employee_photo,
                        name,
                        generate_message(
                            name,
                            designation,
                            role
                        )
                    )



                    st.markdown(
                    """
                    <style>
                    .card-container img {
                        max-width: none !important;
                        width: 1200px !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                    )


                    st.markdown(
                    '<div class="card-container">',
                    unsafe_allow_html=True
                    )


                    st.image(
                    card,
                    width=1200
                    )


                    st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                    )



                    buffer=io.BytesIO()


                    card.save(
                        buffer,
                        format="PNG"
                    )



                    st.download_button(
                        "Download Greeting Card",
                        buffer.getvalue(),
                        "greeting.png",
                        "image/png"
                    )



        else:


            st.error(
                "Employee not found"
            )





# ================= MAIN =================


create_tables()



if "login" not in st.session_state:

    st.session_state.login=False




if not st.session_state.login:



    st.title(
        "Login"
    )


    u=st.text_input(
        "Username"
    )


    p=st.text_input(
        "Password",
        type="password"
    )



    if st.button(
        "Login"
    ):



        result=login_user(
            u,
            p
        )



        if result:


            st.session_state.login=True

            st.session_state.role=result[0]

            st.rerun()



        else:


            st.error(
                "Invalid Login"
            )





else:



    if st.sidebar.button(
        "Logout"
    ):


        st.session_state.login=False

        st.rerun()




    if st.session_state.role=="ADMIN":



        t1,t2,t3=st.tabs(
            [
            "Employee Management",
            "User Management",
            "Greeting Generator"
            ]
        )



        with t1:

            employee_management()



        with t2:

            user_management()



        with t3:

            greeting_generator()




    else:


        greeting_generator()