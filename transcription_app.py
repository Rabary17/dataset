import os
import pandas as pd
import streamlit as st

# Directory selection
directory = st.text_input("Select directory containing WAV files:", value="")

# Load WAV files
def load_wav_files(directory):
    if os.path.isdir(directory):
        wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
        wav_files.sort()
        return wav_files
    else:
        return []

wav_files = load_wav_files(directory)

# Session variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = {}

# Save transcription
def save_transcription():
    transcription = st.session_state.transcription_input.strip()
    if transcription:
        wav_file = wav_files[st.session_state.current_index]
        wav_path = os.path.join(directory, wav_file)
        st.session_state.transcriptions[wav_path] = transcription

        # Save to TSV
        df = pd.DataFrame(list(st.session_state.transcriptions.items()), columns=["Path", "Sentence"])
        df.to_csv("transcriptions.tsv", sep="\t", index=False)

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

    # Transcription input
    st.text_input(
        "Transcription:", 
        key="transcription_input", 
        value=st.session_state.transcriptions.get(wav_path, ""), 
        on_change=save_transcription
    )

    if st.button("Save Transcription"):
        save_transcription()

else:
    st.write("All files have been transcribed or directory is empty.")

# Download TSV file
if os.path.exists("transcriptions.tsv"):
    with open("transcriptions.tsv", "r") as f:
        tsv_content = f.read()
    st.download_button(
        label="Download Transcriptions TSV",
        data=tsv_content,
        file_name="transcriptions.tsv",
        mime="text/tab-separated-values"
    )

# Reset transcriptions
if st.button("Reset Transcriptions"):
    if st.checkbox("Confirm Reset"):
        if os.path.exists("transcriptions.tsv"):
            os.remove("transcriptions.tsv")
        st.session_state.current_index = 0
        st.session_state.transcriptions = {}
        st.session_state.transcription_input = ""
        st.write("Transcriptions and state have been reset.")
