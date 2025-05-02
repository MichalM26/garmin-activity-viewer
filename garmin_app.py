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
    uploaded_file = st.file_uploader("Wczytaj plik CSV z aktywnościami", type="csv")

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df = df[df['Distance'] != '--']
            df['Distance'] = df['Distance'].astype(float)
            df['Calories'] = pd.to_numeric(df['Calories'], errors='coerce')
            df['Date'] = pd.to_datetime(df['Date'])

            total_activities = len(df)
            total_distance = df['Distance'].sum()
            total_calories = df['Calories'].sum()

            st.subheader("📊 Statystyki")
            st.write(f"**Liczba aktywności:** {total_activities}")
            st.write(f"**Suma dystansu:** {total_distance:.2f} km")
            st.write(f"**Suma kalorii:** {int(total_calories)} kcal")

            st.subheader("📈 Typy aktywności")
            fig1, ax1 = plt.subplots()
            df['Activity Type'].value_counts().plot(kind='bar', ax=ax1, title='Typy aktywności')
            ax1.set_ylabel('Liczba')
            st.pyplot(fig1)

            st.subheader("📉 Dystans tygodniowo")
            df['Week'] = df['Date'].dt.to_period('W').astype(str)
            weekly = df.groupby('Week')['Distance'].sum()
            fig2, ax2 = plt.subplots()
            weekly.plot(kind='line', ax=ax2, title='Dystans tygodniowo')
            ax2.set_ylabel('km')
            ax2.tick_params(axis='x', rotation=45)
            st.pyplot(fig2)

            # Generowanie PDF
            pdf_buffer = io.BytesIO()
            with PdfPages(pdf_buffer) as pdf:
                fig_stats, ax = plt.subplots(figsize=(8.27, 11.69))
                ax.axis('off')
                ax.text(0.05, 0.95, "Garmin - Podsumowanie aktywności", fontsize=16, weight='bold')
                stats_text = (
                    f"Liczba aktywności: {total_activities}\n"
                    f"Suma dystansu: {total_distance:.2f} km\n"
                    f"Suma kalorii: {int(total_calories)} kcal"
                )
                ax.text(0.05, 0.85, stats_text, fontsize=12, verticalalignment='top')
                pdf.savefig(fig_stats)
                plt.close(fig_stats)

                pdf.savefig(fig1)
                pdf.savefig(fig2)

            pdf_buffer.seek(0)

            # Pobieranie PDF
            st.download_button(
                label="📥 Pobierz PDF",
                data=pdf_buffer,
                file_name="raport_garmin.pdf",
                mime="application/pdf"
            )

            # Wysyłka e-mailem
            st.subheader("✉️ Wyślij raport PDF e-mailem")
            sender_email = st.text_input("Twój adres e-mail (nadawca)")
            sender_password = st.text_input("Hasło aplikacji (lub SMTP)", type="password")
            recipient_email = st.text_input("Adres e-mail odbiorcy")
            if st.button("Wyślij PDF e-mailem"):
                try:
                    msg = EmailMessage()
                    msg['Subject'] = 'Raport Garmin'
                    msg['From'] = sender_email
                    msg['To'] = recipient_email
                    msg.set_content('W załączniku znajduje się raport PDF z aktywności Garmin.')

                    # Dodanie załącznika
                    msg.add_attachment(pdf_buffer.getvalue(), maintype='application', subtype='pdf', filename='raport_garmin.pdf')

                    # Wysyłka SMTP (Gmail przykładowo)
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(sender_email, sender_password)
                        smtp.send_message(msg)

                    st.success("E-mail został wysłany!")
                except Exception as e:
                    st.error(f"Błąd podczas wysyłania e-maila: {e}")

        except Exception as e:
            st.error(f"Wystąpił błąd: {e}")
