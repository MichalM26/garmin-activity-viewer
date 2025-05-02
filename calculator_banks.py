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

st.set_page_config(page_title="Garmin Activity Viewer")
st.title("Garmin Activity Viewer")

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

        st.subheader("🏦 Przykładowe oferty kredytów gotówkowych (maj 2025)")
        banki = [
            {"Bank": "Citi Handlowy", "Kwota": "150 000 zł", "RRSO": "10,35%", "Oprocentowanie": "9,89%", "Prowizja": "0%"},
            {"Bank": "Alior Bank", "Kwota": "250 000 zł", "RRSO": "10,36%", "Oprocentowanie": "9,90%", "Prowizja": "0%"},
            {"Bank": "BNP Paribas", "Kwota": "230 000 zł", "RRSO": "10,43%", "Oprocentowanie": "9,95%", "Prowizja": "0%"},
            {"Bank": "Santander Consumer Bank", "Kwota": "300 000 zł", "RRSO": "10,46%", "Oprocentowanie": "9,99%", "Prowizja": "0%"},
            {"Bank": "Bank Pekao", "Kwota": "250 000 zł", "RRSO": "10,99%", "Oprocentowanie": "10,47%", "Prowizja": "0%"},
            {"Bank": "VeloBank", "Kwota": "300 000 zł", "RRSO": "11,41%", "Oprocentowanie": "10,85%", "Prowizja": "0%"},
            {"Bank": "Kasa Stefczyka", "Kwota": "100 000 zł", "RRSO": "11,46%", "Oprocentowanie": "10,90%", "Prowizja": "0%"},
            {"Bank": "PKO BP", "Kwota": "300 000 zł", "RRSO": "11,56%", "Oprocentowanie": "10,99%", "Prowizja": "0%"},
            {"Bank": "Raiffeisen Digital Bank", "Kwota": "150 000 zł", "RRSO": "11,99%", "Oprocentowanie": "11,38%", "Prowizja": "0%"},
            {"Bank": "Santander Bank Polska", "Kwota": "300 000 zł", "RRSO": "12,67%", "Oprocentowanie": "11,99%", "Prowizja": "0%"},
        ]
        df_banki = pd.DataFrame(banki)
        st.dataframe(df_banki, use_container_width=True)
