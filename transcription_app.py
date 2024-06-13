import os
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

# Set up authentication
names = ["user1", "user2"]
usernames = ["user1", "user2"]
passwords = ["123", "456"]
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "transcription_app", "abcdef")

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    st.write(f"Welcome {name}")

    # Function to save session state to a file
    def save_session_state():
        session_state = {
            'current_index': st.session_state.current_index,
            'transcriptions': st.session_state.transcriptions,
            'wav_files': st.session_state.wav_files,
            'transcribed_files': st.session_state.transcribed_files
        }
        pd.to_pickle(session_state, "session_state.pkl")

    # Function to load session state from a file
    def load_session_state():
        if os.path.exists("session_state.pkl"):
            session_state = pd.read_pickle("session_state.pkl")
            st.session_state.current_index = session_state['current_index']
            st.session_state.transcriptions = session_state['transcriptions']
            st.session_state.wav_files = session_state['wav_files']
            st.session_state.transcribed_files = session_state['transcribed_files']
        else:
            st.session_state.current_index = -1
            st.session_state.transcriptions = {}
            st.session_state.wav_files = []
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
            save_session_state()

            # Move to the next WAV file
            if st.session_state.current_index + 1 < len(st.session_state.wav_files):
                st.session_state.current_index += 1
                st.session_state.transcription_input = ""  # Reset transcription input for the next file
            else:
                st.session_state.current_index = -1  # Mark as all files transcribed

    def reset_transcriptions():
        if os.path.exists("transcriptions.tsv"):
            os.remove("transcriptions.tsv")
        if os.path.exists("session_state.pkl"):
            os.remove("session_state.pkl")
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
            load_session_state()
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
    if os.path.exists("session_state.pkl"):
        load_session_state()
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

else:
    st.error("Username/password is incorrect")
