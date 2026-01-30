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
        "SELECT winner, total_points, first_play, first_commercial FROM predictions WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()
    
    if row:
        return (
            row[0] or "Seahawks",
            row[1] or 40,
            row[2] or "Run",
            row[3] or ""
        )
    return "Seahawks", 40, "Run", ""


def save_prediction(user_id, winner, points, first_play, first_commercial):
    """Save user's game prediction."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    cur.execute(
        "INSERT INTO predictions (user_id, winner, total_points, first_play, first_commercial) VALUES (?, ?, ?, ?, ?)",
        (user_id, winner, points, first_play, first_commercial)
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


def get_all_predictions():
    """Fetch all user predictions for admin view."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT users.name, predictions.winner, predictions.total_points, 
               predictions.first_play, predictions.first_commercial
        FROM users
        LEFT JOIN predictions ON users.id = predictions.user_id
        ORDER BY users.name
    """)
    predictions = cur.fetchall()
    conn.close()
    return predictions


def get_all_users():
    """Fetch all users for admin management."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, pin FROM users ORDER BY name")
    users = cur.fetchall()
    conn.close()
    return users


def reset_user_pin(user_id, new_pin):
    """Reset a user's PIN."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET pin = ? WHERE id = ?", (new_pin, user_id))
    conn.commit()
    conn.close()


# ---------- LOGIN PAGE ----------
def show_login_page():
    """Display login and registration interface."""
    st.title("🏈 Super Bowl Party Sign In")
    
    # Selection: Login or RSVP
    choice = st.radio(
        "What would you like to do?",
        ["Login", "RSVP (New Guest)"],
        horizontal=True
    )
    
    st.divider()
    
    if choice == "Login":
        # Returning guest login
        st.subheader("Welcome back!")
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, pin FROM users ORDER BY name")
        users = cur.fetchall()
        conn.close()
        
        if not users:
            st.info("No users yet. Select 'RSVP (New Guest)' above to create your profile.")
        else:
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
    
    else:  # RSVP (New Guest)
        st.subheader("Create your profile")
        
        name = st.text_input("Your name")
        pin = st.text_input("Choose a 3-digit code", max_chars=3, key="register_pin")

        if st.button("Create profile"):
            success, message = create_user(name, pin)
            if success:
                st.success(message)
                # Automatically log them in
                if authenticate_user(name, pin):
                    st.rerun()
            else:
                st.error(message)


# ---------- MAIN APP ----------
def show_main_app():
    """Display main app interface for logged-in users."""
    st.title(f"🎉 Welcome, {st.session_state.user_name}")
    
    # Add custom CSS to make tabs sticky
    st.markdown("""
        <style>
        /* Make tabs sticky at top */
        .stTabs [data-baseweb="tab-list"] {
            position: sticky;
            top: 0;
            background-color: white;
            z-index: 999;
            padding: 10px 0;
            border-bottom: 2px solid #f0f0f0;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .stTabs [data-baseweb="tab-list"] {
                background-color: #0e1117;
                border-bottom: 2px solid #262730;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user_id
    user_name = st.session_state.user_name

    # Create tabs - show Admin tab only for Jared
    if user_name == "Jared":
        tab1, tab2, tab3 = st.tabs(["📋 My Info", "🍕 Guest List", "🔐 Admin"])
    else:
        tab1, tab2 = st.tabs(["📋 My Info", "🍕 Guest List"])
        tab3 = None  # No admin tab for non-Jared users

    # Tab 1: RSVP & Predictions
    with tab1:
        # RSVP Section
        st.header("RSVP & Food")
        
        attending_default, food_default = get_user_rsvp(user_id)
        
        attending = st.checkbox("I am attending", value=attending_default)
        food = st.text_input("What food are you bringing?", value=food_default)

        if st.button("Save RSVP"):
            save_rsvp(user_id, attending, food)
            st.success("RSVP saved!")

        st.divider()

        # Predictions Section
        st.header("Game Predictions")
        
        winner_default, points_default, first_play_default, first_commercial_default = get_user_prediction(user_id)
        
        winner = st.selectbox(
            "Who will win?",
            ["Seahawks", "Patriots"],
            index=["Seahawks", "Patriots"].index(winner_default) if winner_default in ["Seahawks", "Patriots"] else 0
        )

        points = st.number_input(
            "Total points scored",
            min_value=0,
            value=points_default
        )

        first_play = st.selectbox(
            "What will the first play be?",
            ["Run", "Pass", "Kick"],
            index=["Run", "Pass", "Kick"].index(first_play_default) if first_play_default in ["Run", "Pass", "Kick"] else 0
        )

        first_commercial = st.text_input(
            "What company will the first commercial be for?",
            value=first_commercial_default or "",
            placeholder="e.g., Budweiser, Toyota, Apple..."
        )

        if st.button("Save Predictions"):
            save_prediction(user_id, winner, points, first_play, first_commercial)
            st.success("Predictions saved!")

    # Tab 2: Guest List
    with tab2:
        st.header("Who's Coming")
        
        guests = get_attending_guests()

        if guests:
            for name, food in guests:
                st.write(f"**{name}** — {food or 'No food listed'}")
        else:
            st.write("No RSVPs yet.")
    
    # Tab 3: Admin View (only for Jared)
    if tab3 is not None:
        with tab3:
            st.header("Admin Panel")
            
            # Sub-sections with expanders
            with st.expander("📊 View All Predictions", expanded=True):
                predictions = get_all_predictions()
                
                if predictions:
                    for name, winner, points, first_play, first_commercial in predictions:
                        st.write("---")
                        st.write(f"**{name}**")
                        if winner:
                            st.write(f"- Winner: {winner}")
                            st.write(f"- Total Points: {points}")
                            st.write(f"- First Play: {first_play or 'Not set'}")
                            st.write(f"- First Commercial: {first_commercial or 'Not set'}")
                        else:
                            st.write("_No predictions yet_")
                else:
                    st.write("No predictions yet.")
            
            with st.expander("👥 Manage Users"):
                users = get_all_users()
                
                if users:
                    st.subheader("Reset User PIN")
                    
                    user_to_reset = st.selectbox(
                        "Select user",
                        [u[1] for u in users],
                        key="reset_user_select"
                    )
                    
                    new_pin = st.text_input(
                        "New 3-digit PIN",
                        max_chars=3,
                        key="new_pin_input"
                    )
                    
                    if st.button("Reset PIN"):
                        if new_pin and new_pin.isdigit() and len(new_pin) == 3:
                            user = next(u for u in users if u[1] == user_to_reset)
                            reset_user_pin(user[0], new_pin)
                            st.success(f"PIN reset for {user_to_reset}")
                        else:
                            st.error("Enter a valid 3-digit PIN")
                    
                    st.divider()
                    st.subheader("All Users")
                    for user_id, name, pin in users:
                        st.write(f"**{name}** - PIN: {pin}")
                else:
                    st.write("No users yet.")

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
