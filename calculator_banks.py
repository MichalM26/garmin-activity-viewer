import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import io
import smtplib
from email.message import EmailMessage
from matplotlib.backends.backend_pdf import PdfPages

# --- Uwierzytelnianie ---
USERNAME = "user"
PASSWORD = "pass123"

st.set_page_config(page_title="Zdolnosc kredytowa"
st.title("Zdolnosc Kredytowa")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔒 Zaloguj się")
    username_input = st.text_input("Nazwa użytkownika")
    password_input = st.text_input("Hasło", type="password")
    if st.button("Zaloguj"):
        if username_input == USERNAME and password_input == PASSWORD:
            st.session_state.authenticated = True
            st.success("Zalogowano pomyślnie!")
        else:
            st.error("Nieprawidłowa nazwa użytkownika lub hasło")

if st.session_state.authenticated:
    st.header("🧮 Kalkulator zdolności kredytowej")
    with st.form("kredyt_form"):
        dochod = st.number_input("Miesięczny dochód netto (zł)", min_value=0.0, step=100.0)
        wydatki = st.number_input("Miesięczne stałe wydatki (czynsz, rachunki itd.) (zł)", min_value=0.0, step=100.0)
        raty = st.number_input("Raty innych kredytów (zł)", min_value=0.0, step=100.0)
        wiek = st.number_input("Wiek (lata)", min_value=18, max_value=75, step=1)
        okres = st.slider("Okres spłaty (w latach)", 5, 35, 25)
        submit_kredyt = st.form_submit_button("Oblicz zdolność kredytową")

    if submit_kredyt:
        dostepne_srodki = dochod - wydatki - raty
        maks_rata = dostepne_srodki * 0.4  # założenie: maks 40% dochodu netto na ratę
        oprocentowanie = 0.08
        mies_rata = maks_rata
        n = okres * 12
        zdolnosc = mies_rata * ((1 + oprocentowanie/12)**n - 1) / ((oprocentowanie/12) * (1 + oprocentowanie/12)**n)

        st.success(f"Szacunkowa zdolność kredytowa: {zdolnosc:,.2f} zł")
        if zdolnosc < 100000:
            st.warning("Zdolność niska – możliwe tylko małe kredyty")
        elif zdolnosc < 300000:
            st.info("Zdolność umiarkowana")
        else:
            st.success("Zdolność wysoka – potencjalna zdolność hipoteczna")
