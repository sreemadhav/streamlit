import streamlit as st
import os
import shutil

source_folder = "source_folder"
pass_folder = "pass_folder"
fail_folder = "fail_folder"

files = os.listdir(source_folder)

file_to_move = st.selectbox("Select a file to move", files)

if files:
    status = st.radio(
        "What's the status of QTG?",
        ["Pass", "Fail"])

    if st.button("Move File"):
        destination_folder = pass_folder if status == "Pass" else fail_folder
        shutil.move(os.path.join(source_folder, file_to_move), destination_folder)
        
        # Display success message
        st.success(f"Moved {file_to_move} to {'Pass' if status == 'Pass' else 'Fail'} folder.")
else:
    st.write("No files to move in the source folder.")

# Display contents of each folder
st.write("### Files in Source Folder:")
st.write(os.listdir(source_folder))

st.write("### Files in Pass Folder:")
st.write(os.listdir(pass_folder))

st.write("### Files in Fail Folder:")
st.write(os.listdir(fail_folder))

