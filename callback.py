import streamlit as st

st.header("Callback Example")

if 'counter' not in st.session_state:
    st.session_state.counter = 0

def decrement():
    st.session_state.counter -= 1

def increment():
    st.session_state.counter += 1

def set_device_status():
    pass
# Create a button that will increment the counter
incrementer = st.button("Increment", key="btn_increment", on_click=increment)

# Create a button that will decrement the counter
decrementer = st.button("Decrement", key="btn_decrement", on_click=decrement)

st.write(f"Counter: {st.session_state.counter}")

