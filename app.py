import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

import streamlit as st


st.set_page_config(page_title="Lunch Choice", page_icon="❤️", layout="centered")


def get_setting(name: str, default: str = "") -> str:
    """Read from Streamlit secrets, falling back to an environment variable."""
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None

    return str(value) if value else os.getenv(name.upper(), default)


def send_email(subject: str, body: str) -> None:
    host = get_setting("smtp_host")
    port = int(get_setting("smtp_port", "587"))
    username = get_setting("smtp_username")
    password = get_setting("smtp_password")
    sender = get_setting("sender_email", username)
    recipient = get_setting("recipient_email")

    missing = [
        name
        for name, value in {
            "SMTP_HOST": host,
            "SMTP_USERNAME": username,
            "SMTP_PASSWORD": password,
            "SENDER_EMAIL": sender,
            "RECIPIENT_EMAIL": recipient,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Email settings are missing: {', '.join(missing)}")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)

    with smtplib.SMTP(host, port, timeout=20) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


st.title("What's for lunch? ❤️")
st.write("Choose your lunch and send it my way.")

main_courses = ["Rice + Rasam", "Rice + Sambar", "One-pot Rice"]
proteins = ["Chicken", "Egg", "Fish"]
drinks = ["Buttermilk", "Fruit Juice"]

with st.form("lunch_choice"):
    st.subheader("Main Course")
    main_course = st.radio(
        "Choose a main course",
        ["Select an option…", *main_courses],
        label_visibility="collapsed",
    )

    st.subheader("Protein")
    protein = st.radio(
        "Choose a protein",
        ["Select an option…", *proteins],
        label_visibility="collapsed",
    )

    st.subheader("Drink")
    drink = st.radio(
        "Choose a drink",
        ["Select an option…", *drinks],
        label_visibility="collapsed",
    )
    st.caption("Fruit juice is subject to availability.")

    st.subheader("Additional Message")
    additional_message = st.text_area("Anything else you'd like me to know?")

    submitted = st.form_submit_button(
        "Send Lunch Choice", type="primary", use_container_width=True
    )

if submitted and not st.session_state.get("lunch_sent", False):
    if main_course not in main_courses or protein not in proteins or drink not in drinks:
        st.error("Please choose a main course, protein, and drink.")
    else:
        husband_name = get_setting("husband_name", "Your husband")
        submitted_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

        body = (
            "Lunch choice ❤️\n\n"
            f"Main Course: {main_course}\n"
            f"Protein: {protein}\n"
            f"Drink: {drink}\n\n"
            "Additional Message:\n"
            f"{additional_message.strip() or 'None'}\n\n"
            "Submitted at:\n"
            f"{submitted_at}"
        )

        try:
            send_email(f"Lunch choice from {husband_name}", body)
        except Exception:
            st.error(
                st.error(f"Email couldn't be sent: {exc}")
    
        else:
            st.session_state.lunch_sent = True
            st.success("Lunch choice sent! ❤️")
elif st.session_state.get("lunch_sent", False):
    st.success("Lunch choice sent! ❤️")
