import streamlit as st

# Titel der App
st.title("Meine erste Streamlit-App 🚀")

# Text-Eingabefeld
name = st.text_input("Wie heißt du?", "Max Mustermann")

# Schieberegler
alter = st.slider("Wie alt bist du?", 0, 100, 25)

# Checkbox
happy = st.checkbox("Bist du glücklich?")

# Button
if st.button("Bestätigen"):
    st.write(f"Hallo {name}! Du bist {alter} Jahre alt.")
    if happy:
        st.balloons()  # Feiere mit Ballons, wenn die Checkbox aktiviert ist
    else:
        st.warning("Schade, dass du nicht glücklich bist! 😢")

# Anzeige der Daten (aktualisiert sich automatisch)
st.write("---")
st.write("**Aktuelle Daten:**")
st.write(f"- Name: {name}")
st.write(f"- Alter: {alter}")
st.write(f"- Glücklich: {'Ja' if happy else 'Nein'}")