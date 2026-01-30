import streamlit as st
from db import init_db, get_connection

st.set_page_config(
    page_title="Super Bowl 60",
    layout="centered"
)

init_db()

# ---------- SESSION STATE ----------
for key in ["logged_in", "user_id", "user_name"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "logged_in" else False

conn = get_connection()
cur = conn.cursor()

# ---------- LOGIN ----------
if not st.session_state.logged_in:
    st.title("🏈 Super Bowl Party Sign In")

    cur.execute("SELECT id, name, pin FROM users ORDER BY name")
    users = cur.fetchall()

    if users:
        st.subheader("Returning guest")
        selected = st.selectbox(
            "Select your name",
            ["-- select --"] + [u[1] for u in users]
        )

        if selected != "-- select --":
            pin = st.text_input("3-digit code", type="password")

            if st.button("Sign in"):
                user = next(u for u in users if u[1] == selected)
                if pin == user[2]:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.user_name = user[1]
                    st.rerun()
                else:
                    st.error("Wrong code")

    st.divider()

    st.subheader("New guest")
    name = st.text_input("Your name")
    pin = st.text_input("Choose a 3-digit code", max_chars=3)

    if st.button("Create profile"):
        if not name or not pin.isdigit() or len(pin) != 3:
            st.error("Enter a name and a 3-digit code")
        else:
            try:
                cur.execute(
                    "INSERT INTO users (name, pin) VALUES (?, ?)",
                    (name, pin)
                )
                conn.commit()
                st.success("Profile created — sign in above")
                st.rerun()
            except:
                st.error("That name already exists")

    conn.close()
    st.stop()

# ---------- MAIN APP ----------
st.title(f"🎉 Welcome, {st.session_state.user_name}")

user_id = st.session_state.user_id

# ---------- RSVP + FOOD ----------
st.header("📋 RSVP & Food")

cur.execute("SELECT attending, food FROM rsvp WHERE user_id = ?", (user_id,))
row = cur.fetchone()

attending_default = bool(row[0]) if row else False
food_default = row[1] if row else ""

attending = st.checkbox("I am attending", value=attending_default)
food = st.text_input("What food are you bringing?", value=food_default)

if st.button("Save RSVP"):
    cur.execute("DELETE FROM rsvp WHERE user_id = ?", (user_id,))
    cur.execute(
        "INSERT INTO rsvp (user_id, attending, food) VALUES (?, ?, ?)",
        (user_id, int(attending), food)
    )
    conn.commit()
    st.success("RSVP saved!")

# ---------- PREDICTIONS ----------
st.header("🔮 Game Predictions")

cur.execute(
    "SELECT winner, total_points FROM predictions WHERE user_id = ?",
    (user_id,)
)
row = cur.fetchone()

winner_default = row[0] if row else "Chiefs"
points_default = row[1] if row else 40

winner = st.selectbox(
    "Who will win?",
    ["Chiefs", "49ers"],
    index=["Chiefs", "49ers"].index(winner_default)
)

points = st.number_input(
    "Total points scored",
    min_value=0,
    value=points_default
)

if st.button("Save Prediction"):
    cur.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    cur.execute(
        "INSERT INTO predictions (user_id, winner, total_points) VALUES (?, ?, ?)",
        (user_id, winner, points)
    )
    conn.commit()
    st.success("Prediction saved!")

# ---------- GUEST LIST ----------
st.header("🍕 Who’s Coming")

cur.execute("""
SELECT users.name, rsvp.food
FROM users
JOIN rsvp ON users.id = rsvp.user_id
WHERE rsvp.attending = 1
ORDER BY users.name
""")

guests = cur.fetchall()

if guests:
    for name, food in guests:
        st.write(f"**{name}** — {food or 'No food listed'}")
else:
    st.write("No RSVPs yet.")

# ---------- LOG OUT ----------
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.rerun()

conn.close()
