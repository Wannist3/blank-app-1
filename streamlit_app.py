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

import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# Titel und Beschreibung
st.title("🌍 Globale Temperaturdaten (Berkeley Earth)")
st.markdown("""
Diese App visualisiert die [globalen Temperaturdaten](https://berkeleyearth.org/data/) von Berkeley Earth.
Die Daten zeigen monatliche Anomalien (Abweichungen vom Durchschnitt 1951–1980) sowie Jahresdurchschnittswerte.
""")

# Datenquelle
DATA_URL = "https://berkeley-earth-temperature.s3.us-west-1.amazonaws.com/Global/Land_and_Ocean_complete.txt"

@st.cache_data  # Daten cachen, um Ladezeiten zu minimieren
def load_data():
    try:
        response = requests.get(DATA_URL, timeout=30)
        response.raise_for_status()

        df_raw = pd.read_csv(
            StringIO(response.text),
            sep=r'\s+',
            engine='python',
            comment='%',
            header=None,
            usecols=[0, 1, 2],
            names=['Jahr', 'Monat', 'Temperatur-Anomalie (°C)']
        )
        df_raw = df_raw.dropna(subset=['Jahr', 'Monat', 'Temperatur-Anomalie (°C)'])
        df_raw['Jahr'] = df_raw['Jahr'].astype(int)
        df_raw['Monat'] = df_raw['Monat'].astype(int)
        df_raw['Temperatur-Anomalie (°C)'] = df_raw['Temperatur-Anomalie (°C)'].astype(float)

        df_yearly = df_raw.groupby('Jahr')['Temperatur-Anomalie (°C)'].mean().reset_index()
        return df_raw, df_yearly
    except Exception as exc:
        return None, None

# Daten laden
df, df_yearly = load_data()
if df is None or df_yearly is None:
    st.error("Die Temperaturdaten konnten nicht geladen werden. Bitte überprüfe die Netzwerkverbindung oder probiere es später erneut.")
    st.stop()

# Sidebar für Filter
st.sidebar.header("Filter")
year_range = st.sidebar.slider(
    "Jahresbereich auswählen:",
    min_value=int(df['Jahr'].min()),
    max_value=int(df['Jahr'].max()),
    value=(1900, int(df['Jahr'].max()))
)

show_monthly = st.sidebar.checkbox("Monatliche Daten anzeigen", False)
show_rolling_avg = st.sidebar.checkbox("7-Jahres-Gleitender Durchschnitt", True)

# Daten filtern
df_filtered = df[(df['Jahr'] >= year_range[0]) & (df['Jahr'] <= year_range[1])]
df_yearly_filtered = df_yearly[(df_yearly['Jahr'] >= year_range[0]) & (df_yearly['Jahr'] <= year_range[1])]

# Plot erstellen
st.subheader("Globale Temperatur-Anomalien (1850–heute)")

if show_monthly:
    fig = px.line(
        df_filtered,
        x='Jahr',
        y='Temperatur-Anomalie (°C)',
        title="Monatliche Temperatur-Anomalien",
        labels={'Temperatur-Anomalie (°C)': 'Anomalie (°C)'}
    )
    std_values = df_filtered['Temperatur-Anomalie (°C)'].std()
    mean_values = df_filtered['Temperatur-Anomalie (°C)'].mean()
    x_values = df_filtered['Jahr']
else:
    fig = px.line(
        df_yearly_filtered,
        x='Jahr',
        y='Temperatur-Anomalie (°C)',
        title="Jährliche Durchschnittstemperatur-Anomalien",
        labels={'Temperatur-Anomalie (°C)': 'Anomalie (°C)'}
    )
    std_values = df_yearly_filtered['Temperatur-Anomalie (°C)'].std()
    mean_values = df_yearly_filtered['Temperatur-Anomalie (°C)'].mean()
    x_values = df_yearly_filtered['Jahr']

upper_band = [mean_values + 2 * std_values] * len(x_values)
lower_band = [mean_values - 2 * std_values] * len(x_values)
fig.add_scatter(
    x=x_values,
    y=upper_band,
    mode='lines',
    name='+2 Standardabweichungen',
    line=dict(color='green', dash='dash')
)
fig.add_scatter(
    x=x_values,
    y=lower_band,
    mode='lines',
    name='-2 Standardabweichungen',
    fill='tonexty',
    line=dict(color='green', dash='dash')
)

# Gleitender Durchschnitt hinzufügen (falls aktiviert)
if show_rolling_avg and not show_monthly:
    df_yearly_filtered['Gleitender Durchschnitt'] = df_yearly_filtered['Temperatur-Anomalie (°C)'].rolling(7).mean()
    fig.add_scatter(
        x=df_yearly_filtered['Jahr'],
        y=df_yearly_filtered['Gleitender Durchschnitt'],
        mode='lines',
        name='7-Jahres-Durchschnitt',
        line=dict(color='red', width=3)
    )

fig.update_layout(yaxis_title="Temperatur-Anomalie (°C)", xaxis_title="Jahr")
st.plotly_chart(fig, use_container_width=True)

# Statistiken anzeigen
st.subheader("Zusammenfassung")
col1, col2, col3 = st.columns(3)
latest_year = int(df_yearly['Jahr'].max())
latest_value = df_yearly.loc[df_yearly['Jahr'] == latest_year, 'Temperatur-Anomalie (°C)'].iloc[0]
col1.metric(f"Aktuellster Wert ({latest_year})", f"{latest_value:.2f} °C")
col2.metric("Durchschnitt (1900–heute)", f"{df_yearly_filtered['Temperatur-Anomalie (°C)'].mean():.2f} °C")
col3.metric("Maximale Anomalie", f"{df_yearly_filtered['Temperatur-Anomalie (°C)'].max():.2f} °C")

# Rohdaten anzeigen (optional)
if st.checkbox("Rohdaten anzeigen"):
    st.dataframe(df_filtered)