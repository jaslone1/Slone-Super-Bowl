import streamlit as st
from db import init_db, get_connection

st.set_page_config(
    page_title="Super Bowl 60",
    layout="centered"
)

init_db()

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

conn = get_connection()
cur = conn.cursor()

# ---------- LOGIN SCREEN ----------
if not st.session_state.logged_in:
    st.title("Super Bowl Party Sign In")

    # Existing users
    cur.execute("SELECT id, name, pin FROM users ORDER BY name")
    users = cur.fetchall()

    if users:
        st.subheader("Returning guest")
        selected = st.selectbox(
            "Select your name",
            ["-- select --"] + [u[1] for u in users]
        )

        if selected != "-- select --":
            pin = st.text_input("Enter your 3-digit code", type="password")

            if st.button("Sign in"):
                user = next(u for u in users if u[1] == selected)
                if pin == user[2]:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.user_name = user[1]
                    st.success(f"Welcome back, {user[1]}!")
                    st.rerun()
                else:
                    st.error("Wrong code")

    st.divider()

    # New users
    st.subheader("New guest")
    name = st.text_input("Your name")
    pin = st.text_input("Choose a 3-digit code", max_chars=3)

    if st.button("Create profile"):
        if not name or len(pin) != 3 or not pin.isdigit():
            st.error("Enter a name and a 3-digit code")
        else:
            try:
                cur.execute(
                    "INSERT INTO users (name, pin) VALUES (?, ?)",
                    (name, pin)
                )
                conn.commit()
                st.success("Profile created! You can sign in now.")
                st.rerun()
            except:
                st.error("That name already exists")

    conn.close()
    st.stop()

# ---------- LOGGED IN ----------
st.title(f"Welcome, {st.session_state.user_name}")

st.write("You are signed in. Next up: RSVP, food, predictions, charts.")

if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.rerun()

conn.close()
