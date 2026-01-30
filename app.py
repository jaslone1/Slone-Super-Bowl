import streamlit as st
from db import init_db, get_connection

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Super Bowl 60",
    layout="centered"
)

# ---------- INITIALIZE ----------
init_db()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None


# ---------- HELPER FUNCTIONS ----------
def authenticate_user(username, pin):
    """Verify user credentials and log them in."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, pin FROM users WHERE name = ?", (username,))
    user = cur.fetchone()
    conn.close()
    
    if user and pin == user[2]:
        st.session_state.logged_in = True
        st.session_state.user_id = user[0]
        st.session_state.user_name = user[1]
        return True
    return False


def create_user(name, pin):
    """Create a new user profile."""
    if not name or not pin.isdigit() or len(pin) != 3:
        return False, "Enter a name and a 3-digit code"
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, pin) VALUES (?, ?)", (name, pin))
        conn.commit()
        conn.close()
        return True, "Profile created — sign in above"
    except:
        return False, "That name already exists"


def logout():
    """Clear session state and log out user."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None


def get_user_rsvp(user_id):
    """Fetch user's RSVP data."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT attending, food FROM rsvp WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return bool(row[0]), row[1]
    return False, ""


def save_rsvp(user_id, attending, food):
    """Save user's RSVP."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM rsvp WHERE user_id = ?", (user_id,))
    cur.execute(
        "INSERT INTO rsvp (user_id, attending, food) VALUES (?, ?, ?)",
        (user_id, int(attending), food)
    )
    conn.commit()
    conn.close()


def get_user_prediction(user_id):
    """Fetch user's prediction data."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT winner, total_points FROM predictions WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()
    
    if row:
        return row[0], row[1]
    return "Chiefs", 40


def save_prediction(user_id, winner, points):
    """Save user's game prediction."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    cur.execute(
        "INSERT INTO predictions (user_id, winner, total_points) VALUES (?, ?, ?)",
        (user_id, winner, points)
    )
    conn.commit()
    conn.close()


def get_attending_guests():
    """Fetch list of guests who are attending."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT users.name, rsvp.food
        FROM users
        JOIN rsvp ON users.id = rsvp.user_id
        WHERE rsvp.attending = 1
        ORDER BY users.name
    """)
    guests = cur.fetchall()
    conn.close()
    return guests


# ---------- LOGIN PAGE ----------
def show_login_page():
    """Display login and registration interface."""
    st.title("🏈 Super Bowl Party Sign In")
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, pin FROM users ORDER BY name")
    users = cur.fetchall()
    conn.close()

    # Returning guest login
    if users:
        st.subheader("Returning guest")
        selected = st.selectbox(
            "Select your name",
            ["-- select --"] + [u[1] for u in users]
        )

        if selected != "-- select --":
            pin = st.text_input("3-digit code", type="password", key="login_pin")

            if st.button("Sign in"):
                if authenticate_user(selected, pin):
                    st.rerun()
                else:
                    st.error("Wrong code")

    st.divider()

    # New guest registration
    st.subheader("New guest")
    name = st.text_input("Your name")
    pin = st.text_input("Choose a 3-digit code", max_chars=3, key="register_pin")

    if st.button("Create profile"):
        success, message = create_user(name, pin)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)


# ---------- MAIN APP ----------
def show_main_app():
    """Display main app interface for logged-in users."""
    st.title(f"🎉 Welcome, {st.session_state.user_name}")
    
    user_id = st.session_state.user_id

    # RSVP Section
    st.header("📋 RSVP & Food")
    
    attending_default, food_default = get_user_rsvp(user_id)
    
    attending = st.checkbox("I am attending", value=attending_default)
    food = st.text_input("What food are you bringing?", value=food_default)

    if st.button("Save RSVP"):
        save_rsvp(user_id, attending, food)
        st.success("RSVP saved!")

    # Predictions Section
    st.header("🔮 Game Predictions")
    
    winner_default, points_default = get_user_prediction(user_id)
    
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
        save_prediction(user_id, winner, points)
        st.success("Prediction saved!")

    # Guest List Section
    st.header("🍕 Who's Coming")
    
    guests = get_attending_guests()

    if guests:
        for name, food in guests:
            st.write(f"**{name}** — {food or 'No food listed'}")
    else:
        st.write("No RSVPs yet.")

    # Logout
    st.divider()
    if st.button("Log out"):
        logout()
        st.rerun()


# ---------- MAIN ----------
if __name__ == "__main__":
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()
