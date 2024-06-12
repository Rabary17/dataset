
import os
import pandas as pd
import streamlit as st

# Initialize session state variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = -1
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []
if 'wav_files' not in st.session_state:
    st.session_state.wav_files = []

def save_transcription():
    transcription = st.session_state.transcription_input.strip()
    if transcription:
        wav_file = st.session_state.wav_files[st.session_state.current_index]
        wav_path = os.path.join(directory, wav_file)
        st.session_state.transcriptions.append((wav_path, transcription))

        # Save to TSV
        df = pd.DataFrame(st.session_state.transcriptions, columns=["Path", "Sentence"])
        df.to_csv("transcriptions.tsv", sep="\t", index=False)

        # Save current state
        with open("last_state.txt", "w") as f:
            f.write(f"{directory}\n{st.session_state.current_index}\n")

        st.session_state.transcription_input = ""
        st.session_state.current_index += 1

def load_last_state():
    if os.path.exists("last_state.txt"):
        with open("last_state.txt", "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                global directory
                directory = lines[0].strip()
                st.session_state.current_index = int(lines[1].strip()) - 1
                st.session_state.wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
                st.session_state.wav_files.sort()

# User interface
st.title("Transcription App")

directory = st.text_input("Select directory containing WAV files:", value="")

if st.button("Load Directory"):
    if os.path.isdir(directory):
        st.session_state.wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
        st.session_state.wav_files.sort()
        st.session_state.current_index = 0
        st.write(f"Loaded {len(st.session_state.wav_files)} files.")
    else:
        st.write("Invalid directory. Please try again.")

if st.session_state.current_index >= 0 and st.session_state.current_index < len(st.session_state.wav_files):
    wav_file = st.session_state.wav_files[st.session_state.current_index]
    wav_path = os.path.join(directory, wav_file)
    st.audio(wav_path)

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
    st.write(f"Resumed from last session. Current file: {st.session_state.wav_files[st.session_state.current_index]}")

