import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image, ImageDraw
import os


# ================= DATABASE =================


DB_NAME = "employees.db"


def get_conn():

    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )



def init_db():

    conn = get_conn()

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


    conn.commit()

    conn.close()



# ================= DATABASE FUNCTIONS =================


def add_employee(
        emp_id,
        name,
        designation,
        role,
        email
):

    conn = get_conn()

    cur = conn.cursor()


    cur.execute("""

    INSERT INTO employees
    (
        emp_id,
        name,
        designation,
        role,
        email
    )

    VALUES (?, ?, ?, ?, ?)

    ON CONFLICT(emp_id)

    DO UPDATE SET

        name = excluded.name,
        designation = excluded.designation,
        role = excluded.role,
        email = excluded.email

    """,

    (
        emp_id,
        name,
        designation,
        role,
        email
    ))


    conn.commit()

    conn.close()



def get_employees():

    conn = get_conn()


    df = pd.read_sql(

        """
        SELECT *
        FROM employees
        ORDER BY emp_id

        """,

        conn

    )


    conn.close()


    return df




def get_employee(emp_id):

    conn = get_conn()


    df = pd.read_sql(

        """
        SELECT *
        FROM employees
        WHERE emp_id = ?

        """,

        conn,

        params=(emp_id,)

    )


    conn.close()


    if len(df) > 0:

        return df.iloc[0]


    return None




def delete_employee(emp_id):

    conn = get_conn()

    cur = conn.cursor()


    cur.execute(

        """
        DELETE FROM employees
        WHERE emp_id = ?

        """,

        (emp_id,)

    )


    conn.commit()

    conn.close()



# ================= GREETING IMAGE =================


def create_greeting(
        boss_image,
        employee_image,
        name,
        role
):


    boss = Image.open(
        boss_image
    ).convert("RGB")


    employee = Image.open(
        employee_image
    ).convert("RGB")



    boss.thumbnail((250,300))

    employee.thumbnail((250,300))



    canvas = Image.new(

        "RGB",

        (900,600),

        "white"

    )



    canvas.paste(
        boss,
        (80,150)
    )


    canvas.paste(
        employee,
        (570,150)
    )



    draw = ImageDraw.Draw(canvas)



    message = f"""

Congratulations {name}


Your contribution in {role}

is highly appreciated.


Thank you for your dedication.

"""



    draw.text(

        (300,150),

        message,

        fill="black"

    )



    filename = f"{name}_greeting.png"



    canvas.save(filename)



    return filename



# ================= START APP =================


init_db()



st.title(
    "Employee Recognition Greeting System"
)



menu = st.sidebar.selectbox(

    "Menu",

    [

        "Admin Panel",

        "User Greeting"

    ]

)



# ================= ADMIN =================


if menu == "Admin Panel":


    st.header(
        "Admin Employee Management"
    )



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
        "Email ID"
    )



    if st.button(
        "Save Employee"
    ):


        if emp_id.strip()=="" or name.strip()=="":


            st.error(
                "Employee ID and Name are mandatory"
            )


        else:


            add_employee(

                emp_id,

                name,

                designation,

                role,

                email

            )


            st.success(
                "Employee saved successfully"
            )


            st.rerun()



    st.divider()



    st.subheader(
        "Employee Database"
    )



    df = get_employees()


    st.dataframe(
        df
    )



    if len(df)>0:


        delete_id = st.selectbox(

            "Select Employee to Delete",

            df["emp_id"]

        )


        if st.button(
            "Delete Employee"
        ):


            delete_employee(
                delete_id
            )


            st.warning(
                "Employee deleted"
            )


            st.rerun()



# ================= USER GREETING =================


if menu == "User Greeting":


    st.header(
        "Generate Greeting"
    )



    df = get_employees()



    if len(df)==0:


        st.warning(
            "No employee data available"
        )



    else:


        selected_id = st.selectbox(

            "Select Employee",

            df["emp_id"]

        )



        emp = get_employee(
            selected_id
        )



        st.write(
            "Name:",
            emp["name"]
        )


        st.write(
            "Designation:",
            emp["designation"]
        )


        st.write(
            "Role:",
            emp["role"]
        )


        st.write(
            "Email:",
            emp["email"]
        )



        camera = st.camera_input(
            "Take Selfie"
        )



        upload = st.file_uploader(

            "Upload Photo",

            type=[
                "jpg",
                "jpeg",
                "png"
            ]

        )



        photo = camera if camera else upload



        if photo:


            if st.button(
                "Generate Greeting"
            ):


                boss_photo = "assets/boss_photo.jpg"



                if os.path.exists(
                    boss_photo
                ):


                    result = create_greeting(

                        boss_photo,

                        photo,

                        emp["name"],

                        emp["role"]

                    )


                    st.success(
                        "Greeting Generated"
                    )


                    st.image(
                        result
                    )



                    with open(result,"rb") as file:


                        st.download_button(

                            "Download Greeting",

                            file,

                            file_name=result

                        )


                else:


                    st.error(
                        "Boss photo missing"
                    )