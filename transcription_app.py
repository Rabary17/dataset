import os
import pandas as pd
import streamlit as st

# Initialize session state variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = {}
if 'wav_files' not in st.session_state:
    st.session_state.wav_files = []

def save_transcription(index, transcription):
    transcription = transcription.strip()
    if transcription:
        wav_file = st.session_state.wav_files[index]
        wav_path = os.path.join(directory, wav_file)
        st.session_state.transcriptions[wav_path] = transcription

        # Save to TSV
        df = pd.DataFrame(list(st.session_state.transcriptions.items()), columns=["Path", "Sentence"])
        df.to_csv("transcriptions.tsv", sep="\t", index=False)

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

def reset_transcriptions():
    if os.path.exists("transcriptions.tsv"):
        os.remove("transcriptions.tsv")
    if os.path.exists("last_state.txt"):
        os.remove("last_state.txt")
    st.session_state.current_index = 0
    st.session_state.transcriptions = {}
    st.session_state.wav_files = []
    st.write("Transcriptions have been reset.")

def reset_session():
    if os.path.exists("transcriptions.tsv"):
        os.remove("transcriptions.tsv")
    if os.path.exists("last_state.txt"):
        os.remove("last_state.txt")
    st.session_state.current_index = 0
    st.session_state.transcriptions = {}
    st.session_state.wav_files = []
    st.write("Session has been reset.")

# User interface
st.title("Transcription App")

directory = st.text_input("Select directory containing WAV files:", value="")

if st.button("Load Directory"):
    if os.path.isdir(directory):
        st.session_state.wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
        st.session_state.wav_files.sort()
        load_transcriptions()
        st.write(f"Loaded {len(st.session_state.wav_files)} files.")
        print("Directory:", directory)
        print("WAV Files:", st.session_state.wav_files)
    else:
        st.write("Invalid directory. Please try again.")

if st.session_state.wav_files:
    num_files = min(5, len(st.session_state.wav_files) - st.session_state.current_index)
    columns = st.beta_columns(num_files)

    for i in range(num_files):
        wav_file = st.session_state.wav_files[st.session_state.current_index + i]
        wav_path = os.path.join(directory, wav_file)
        columns[i].audio(wav_path)
        transcription = columns[i].text_input(f"Transcription for {wav_file}", 
                                              key=f"transcription_{i}", 
                                              value=st.session_state.transcriptions.get(wav_path, ""), 
                                              on_change=save_transcription, args=(st.session_state.current_index + i, st.session_state[f"transcription_{i}"]))
    
    if st.button("Next 5 Files"):
        st.session_state.current_index += num_files

if os.path.exists("last_state.txt"):
    load_last_state()
    if st.session_state.current_index >= 0:
        st.write(f"Resumed from last session. Current file: {st.session_state.wav_files[st.session_state.current_index]}")

if os.path.exists("transcriptions.tsv"):
    with open("transcriptions.tsv", "r") as f:
        tsv_content = f.read()
    st.download_button(
        label="Download Transcriptions TSV",
        data=tsv_content,
        file_name="transcriptions.tsv",
        mime="text/tab-separated-values"
    )

if st.button("Reset Transcriptions"):
    if st.checkbox("Confirm Reset"):
        reset_transcriptions()

if st.button("Reset Session"):
    if st.checkbox("Confirm Reset"):
        reset_session()
