vimport os
import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets authentication
def authenticate_gsheets(json_keyfile):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client

# Load data from Google Sheets
def load_gsheets_data(sheet_url, sheet_name):
    client = authenticate_gsheets('https://drive.google.com/file/d/1FNgMWFIXCOKw-rO555AlTDbkAaJ3HiA6/view?usp=sharing')
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Save data to Google Sheets
def save_gsheets_data(sheet_url, sheet_name, data):
    client = authenticate_gsheets('https://drive.google.com/file/d/1FNgMWFIXCOKw-rO555AlTDbkAaJ3HiA6/view?usp=sharing')
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    sheet.clear()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# Initialize session state variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = {}

# Load transcriptions from Google Sheets
sheet_url = st.text_input("Enter Google Sheet URL:")
sheet_name = st.text_input("Enter Sheet Name:")
if st.button("Load Transcriptions"):
    transcriptions_df = load_gsheets_data(sheet_url, sheet_name)
    for _, row in transcriptions_df.iterrows():
        st.session_state.transcriptions[row['Path']] = row['Sentence']
    st.write("Transcriptions loaded.")

# Directory selection and file loading
directory = st.text_input("Select directory containing WAV files:", value="")
wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')] if directory else []

# Save transcription
def save_transcription():
    transcription = st.session_state.transcription_input.strip()
    if transcription:
        wav_file = wav_files[st.session_state.current_index]
        wav_path = os.path.join(directory, wav_file)
        st.session_state.transcriptions[wav_path] = transcription

        # Save to Google Sheets
        transcriptions_df = pd.DataFrame(list(st.session_state.transcriptions.items()), columns=["Path", "Sentence"])
        save_gsheets_data(sheet_url, sheet_name, transcriptions_df)

        # Move to the next WAV file
        if st.session_state.current_index + 1 < len(wav_files):
            st.session_state.current_index += 1
            st.session_state.transcription_input = ""  # Reset transcription input for the next file
        else:
            st.session_state.current_index = -1  # Mark as all files transcribed

# Display current WAV file
if wav_files and st.session_state.current_index >= 0:
    wav_file = wav_files[st.session_state.current_index]
    wav_path = os.path.join(directory, wav_file)
    st.audio(wav_path)
    st.text_input("Transcription:", key="transcription_input", value=st.session_state.transcriptions.get(wav_path, ""), on_change=save_transcription)

    if st.button("Save Transcription"):
        save_transcription()
else:
    st.write("All files have been transcribed or directory is empty.")

# Reset transcriptions
if st.button("Reset Transcriptions"):
    if st.checkbox("Confirm Reset"):
        st.session_state.current_index = 0
        st.session_state.transcriptions = {}
        st.session_state.transcription_input = ""
        transcriptions_df = pd.DataFrame(columns=["Path", "Sentence"])
        save_gsheets_data(sheet_url, sheet_name, transcriptions_df)
        st.write("Transcriptions and state have been reset.")
