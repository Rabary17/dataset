import os
import pandas as pd
import streamlit as st

# Initialize session state variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = -1
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = {}
if 'wav_files' not in st.session_state:
    st.session_state.wav_files = []
if 'transcribed_files' not in st.session_state:
    st.session_state.transcribed_files = {}

def save_transcription():
    transcription = st.session_state.transcription_input.strip()
    if transcription:
        wav_file = st.session_state.wav_files[st.session_state.current_index]
        wav_path = os.path.join(directory, wav_file)
        st.session_state.transcriptions[wav_path] = transcription
        st.session_state.transcribed_files[wav_path] = True

        # Save to TSV
        df = pd.DataFrame(list(st.session_state.transcriptions.items()), columns=["Path", "Sentence"])
        df.to_csv("transcriptions.tsv", sep="\t", index=False)

        # Save current state
        with open("last_state.txt", "w") as f:
            f.write(f"{directory}\n{st.session_state.current_index}\n")

        # Clear transcription input
        st.session_state.transcription_input = ""

def load_last_state():
    if os.path.exists("last_state.txt"):
        with open("last_state.txt", "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                global directory
                directory = lines[0].strip()
                st.session_state.current_index = int(lines[1].strip())
                st.session_state.wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
                st.session_state.wav_files.sort()
                load_transcriptions()

def load_transcriptions():
    if os.path.exists("transcriptions.tsv"):
        df = pd.read_csv("transcriptions.tsv", sep="\t")
        for _, row in df.iterrows():
            st.session_state.transcriptions[row['Path']] = row['Sentence']
            st.session_state.transcribed_files[row['Path']] = True

# User interface
st.title("Transcription App")

directory = st.text_input("Select directory containing WAV files:", value="")

if st.button("Load Directory"):
    if os.path.isdir(directory):
        st.session_state.wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
        st.session_state.wav_files.sort()
        st.session_state.current_index = 0
        load_transcriptions()
        st.write(f"Loaded {len(st.session_state.wav_files)} files.")
    else:
        st.write("Invalid directory. Please try again.")

if st.session_state.current_index >= 0 and st.session_state.current_index < len(st.session_state.wav_files):
    wav_file = st.session_state.wav_files[st.session_state.current_index]
    wav_path = os.path.join(directory, wav_file)
    st.audio(wav_path)

    transcribed = st.session_state.transcribed_files.get(wav_path, False)
    if transcribed:
        st.write(f"File '{wav_file}' has already been transcribed.")
        st.text_input("Transcription:", key="transcription_input", value=st.session_state.transcriptions[wav_path])
    else:
        st.text_input("Transcription:", key="transcription_input")

    if st.button("Save Transcription"):
        save_transcription()

    if st.session_state.current_index + 1 < len(st.session_state.wav_files):
        if st.button("Next WAV"):
            save_transcription()

else:
    st.write("All files have been transcribed.")

# Load last state if exists
if os.path.exists("last_state.txt"):
    load_last_state()
    if st.session_state.current_index >= 0:
        st.write(f"Resumed from last session. Current file: {st.session_state.wav_files[st.session_state.current_index]}")
