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
if 'transcription_input' not in st.session_state:
    st.session_state.transcription_input = ""

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

        # Move to the next WAV file
        if st.session_state.current_index + 1 < len(st.session_state.wav_files):
            st.session_state.current_index += 1
            st.session_state.transcription_input = ""  # Reset transcription input for the next file
        else:
            st.session_state.current_index = -1  # Mark as all files transcribed

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

def reset_transcriptions():
    if os.path.exists("transcriptions.tsv"):
        os.remove("transcriptions.tsv")
    if os.path.exists("last_state.txt"):
        os.remove("last_state.txt")
    st.session_state.current_index = -1
    st.session_state.transcriptions = {}
    st.session_state.transcribed_files = {}
    st.session_state.transcription_input = ""
    st.write("Transcriptions and state have been reset.")

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

        # Print out directory and list of WAV files
        print("Directory:", directory)
        print("WAV Files:", st.session_state.wav_files)
    else:
        st.write("Invalid directory. Please try again.")

if st.session_state.current_index >= 0 and st.session_state.current_index < len(st.session_state.wav_files):
    wav_file = st.session_state.wav_files[st.session_state.current_index]
    wav_path = os.path.join(directory, wav_file)
    st.audio(wav_path)

    # Print out wav_path
    print("WAV Path:", wav_path)

    st.text_input("Transcription:", key="transcription_input", value=st.session_state.transcriptions.get(wav_path, ""), on_change=save_transcription)

    if st.button("Save Transcription"):
        save_transcription()
else:
    st.write("All files have been transcribed.")

# Load last state if exists
if os.path.exists("last_state.txt"):
    load_last_state()
    if st.session_state.current_index >= 0:
        st.write(f"Resumed from last session. Current file: {st.session_state.wav_files[st.session_state.current_index]}")

# Provide option to download the TSV file
if os.path.exists("transcriptions.tsv"):
    with open("transcriptions.tsv", "r") as f:
        tsv_content = f.read()
    st.download_button(
        label="Download Transcriptions TSV",
        data=tsv_content,
        file_name="transcriptions.tsv",
        mime="text/tab-separated-values"
    )

# Provide option to reset transcriptions
if st.button("Reset Transcriptions"):
    if st.checkbox("Confirm Reset"):
        reset_transcriptions()
