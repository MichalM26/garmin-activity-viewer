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
        maks_rata = dostepne_srodki * 0.4
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

        st.subheader("📥 Oferty kredytów gotówkowych – aktualizacja z Google Sheet")
        try:
            sheet_url = "https://docs.google.com/spreadsheets/d/1W701LA55B4K92wy565E7tueE8ptmwMKGUQtzGzZzV1w/export?format=csv"
            df_banki = pd.read_csv(sheet_url)
            st.success("Oferty załadowane z Google Sheet")
            st.dataframe(df_banki, use_container_width=True)
        except Exception as e:
            st.error(f"Błąd ładowania arkusza: {e}")

        st.markdown("""
---
### 🧭 Dlaczego warto zacząć od nowa po 40-tce?

Masz doświadczenie, którego młodsze pokolenie nie ma. 
Masz świadomość czasu i odpowiedzialność za swój kierunek. 
Masz mniej złudzeń, a więcej odwagi.

Nie zaczynasz od zera — zaczynasz **z przewagą**.
To nie jest za późno. To jest **właśnie moment**.
""")

    st.header("📊 Analiza sensowności budowy drugiego domu")
    with st.form("budowa_domu"):
        koszt_budowy = st.number_input("Szacunkowy koszt budowy (zł)", min_value=0.0, step=10000.0)
        wartosc_rynkowa = st.number_input("Przewidywana wartość rynkowa domu po budowie (zł)", min_value=0.0, step=10000.0)
        koszt_utrzymania_domu = st.number_input("Miesięczny koszt utrzymania domu w Piotrkowie (zł)", min_value=0.0, step=100.0)
        wykorzystanie = st.selectbox("Jak planujesz wykorzystać dom?", ["Zamieszkanie", "Wynajem", "Pustostan"])
        czynsz = 0
        if wykorzystanie == "Wynajem":
            czynsz = st.number_input("Szacowany miesięczny czynsz najmu (zł)", min_value=0.0, step=100.0)

        submit_budowa = st.form_submit_button("Sprawdź opłacalność")

    if submit_budowa:
        if wykorzystanie == "Wynajem" and czynsz > 0:
            zwrot_lat = round(koszt_budowy / ((czynsz - koszt_utrzymania_domu) * 12), 2) if (czynsz - koszt_utrzymania_domu) > 0 else float('inf')
            st.info(f"Zwrot z inwestycji przez wynajem: {zwrot_lat} lat")
        roznica = wartosc_rynkowa - koszt_budowy
        if roznica > 0:
            st.success(f"Opłaca się: wartość domu przewyższa koszt budowy o {roznica:,.2f} zł")
        else:
            st.warning(f"Nieopłacalne: wartość domu jest niższa niż koszt budowy o {abs(roznica):,.2f} zł")

        if wykorzystanie == "Pustostan":
            roczny_koszt = koszt_utrzymania_domu * 12
            st.error(f"Dom jako pustostan będzie Cię kosztował około {roczny_koszt:,.2f} zł rocznie")
