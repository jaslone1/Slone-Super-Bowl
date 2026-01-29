import streamlit as st

st.set_page_config(
    page_title="My Streamlit App",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 Streamlit Starter App")
st.write("This is a basic Streamlit app you can build on.")

# Example input
name = st.text_input("What's your name?")

if name:
    st.success(f"Hello, {name}! 👋")

# Example button
if st.button("Click me"):
    st.balloons()
