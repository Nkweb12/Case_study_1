import streamlit as st
from queries import get_users, add_user, delete_user


def render():
    st.write("# Nutzerverwaltung")

    users = get_users()

    st.write("## Neuer Nutzer")
    with st.form("add_user_form"):
        user_id = st.text_input("User-ID / E-Mail")
        name = st.text_input("Name")
        submit = st.form_submit_button("Anlegen")

    if submit:
        if not user_id or not name:
            st.error("Bitte alle Felder ausfüllen.")
        elif any(u["id"] == user_id for u in users):
            st.error("User existiert bereits.")
        else:
            add_user(user_id.strip(), name.strip())
            st.success("Nutzer angelegt.")
            st.rerun()

    st.write("## Bestehende Nutzer")
    for u in users:
        col1, col2 = st.columns([3, 1])
        col1.write(f'{u["name"]} ({u["id"]})')
        if col2.button("❌ Löschen", key=f'del_{u["id"]}'):
            delete_user(u["id"])
            st.rerun()
