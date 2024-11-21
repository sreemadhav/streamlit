import streamlit as st
import os
import shutil
import base64
import fitz
import tempfile
import datetime
import pandas as pd
import csv

st.set_page_config(
    page_title="QTG Review System",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.header("QTG Review System")
st.sidebar.markdown("Manage and review your QTG files efficiently.")
device = st.sidebar.selectbox("Select Device", options=["Select", "FFS", "FTD"], key="device_selection")
year = st.sidebar.selectbox("Select Year", options=["Select", "2023", "2024"], key="year_selection")
set = st.sidebar.selectbox("Select Set", options=["Select", "Set A", "Set B", "Set C", "Set D"], key="set_selection")
if device == "Select" or year == "Select" or set == "Select":
    st.sidebar.warning("Please select a device, year, and set to proceed.")
    st.write("### 🚫 Please select a device, year, and respective QTG set in the sidebar to continue.")
    st.stop()  

base_folder = os.path.join(f"./{device}", year, set)
source_folder = os.path.join(base_folder, "source_folder")
pass_folder = os.path.join(base_folder, "pass_folder")
fail_folder = os.path.join(base_folder, "fail_folder")
signed_folder = os.path.join(base_folder, "signed_folder")
log_file = os.path.join(base_folder, "signing_log.csv")
for folder in [source_folder, pass_folder, fail_folder, signed_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

if not os.path.exists(log_file):
    with open(log_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Document Name", "Signed By", "Date/Time"])

if "update" not in st.session_state:
    st.session_state["update"] = False

if st.session_state["update"]:
    st.session_state["update"] = False
    st.experimental_rerun()
    
st.write(f"### 📂 QTG Review System: {device} - {year} - {set}")
st.markdown(f"#### Base Folder: {base_folder}")

def list_files(folder):
    """List files in a folder."""
    try:
        return os.listdir(folder)
    except FileNotFoundError:
        return []

def move_file(src, dest):
    try:
        shutil.move(src, dest)
        return True
    except Exception as e:
        st.error(f"Error moving file {src} to {dest}: {e}")
        return False

def retrieve_files(selected_files, src_folder, dest_folder):
    moved_files = []
    for item in selected_files:
        src_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)
        if move_file(src_path, dest_path):
            moved_files.append(item)
    return moved_files

def get_file_link(file_path):
    with open(file_path, "rb") as f:
        pdf_data = f.read()
        b64 = base64.b64encode(pdf_data).decode()
        return f'<a href="data:application/pdf;base64,{b64}" target="_blank">Open PDF</a>'
    
def add_signature_to_pdf(pdf_path, signature_path, signed_folder, signer_name):
    try:
        doc = fitz.open(pdf_path)
        signature_img = fitz.open(signature_path)

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        page = doc[0]  
        top_margin = 20 
        x = 50 
        image_width = 150
        image_height = 150

        image_rect = fitz.Rect(x, top_margin, x + image_width, top_margin + image_height)

        page.insert_image(image_rect, filename=signature_path)

        text_rect = fitz.Rect(x, top_margin + image_height + 5, x + 200, top_margin + image_height + 25)
        page.insert_text(text_rect.tl, f"Signed on: {current_datetime}", fontsize=10)

        signed_file_path = os.path.join(signed_folder, os.path.basename(pdf_path))
        doc.save(signed_file_path)
        doc.close()

        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([os.path.basename(pdf_path), signer_name, current_datetime])

        if os.path.exists(signed_file_path):
            os.remove(pdf_path)

        return signed_file_path

    except Exception as e:
        st.error(f"Error signing PDF: {e}")
        return None

def create_file_dataframe(folder_path):
    folder_contents = list_files(folder_path)
    if folder_contents: 
        data = [[item] for item in folder_contents]
        return pd.DataFrame(data, columns=["File Name"])
    else: 
        return pd.DataFrame(columns=["File Name"])

tab1, tab2, tab3, tab4 = st.tabs(
    ["📂 Manage QTG Files", "🔄 Retrieve Files", "🖊️ E-Sign Document", "📊 Signing Log"]
)

with tab1:
    st.header("📁 QTG Review and Classification")

    with st.container():
        st.subheader("Review QTG Files")
        files = list_files(source_folder)
        
        if files:
            file_to_move = st.selectbox("Select the QTG to review", files)
            if file_to_move:
                pdf_file_path = os.path.join(source_folder, file_to_move)
                if os.path.exists(pdf_file_path):
                    with open(pdf_file_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()
                        st.download_button(
                            label="Open PDF",
                            data=pdf_data,
                            file_name=file_to_move,
                            mime="application/pdf",
                            use_container_width=True
                        )
            status = st.radio("Status of QTG", ["Pass", "Fail"], horizontal=True)
            if st.button("Submit"):
                destination_folder = pass_folder if status == "Pass" else fail_folder
                src_path = os.path.join(source_folder, file_to_move)
                dest_path = os.path.join(destination_folder, file_to_move)

                if move_file(src_path, dest_path):
                    st.success(f"Moved '{file_to_move}' to **{'Pass' if status == 'Pass' else 'Fail'}** folder.")
                    st.rerun() 
        else:
            st.warning("🚫 No files to move in the source folder.")

            

    st.markdown("---")
    with st.container():
        st.subheader("2. View Folder Contents")
        
        st.markdown("### 📂 Source Folder")
        source_data = create_file_dataframe(source_folder)
        if not source_data.empty:
            st.dataframe(source_data) 
        else:
            st.write("No files in source folder.")

        st.markdown("---")
        st.markdown("### Pass Folder")
        pass_data = create_file_dataframe(pass_folder)
        if not pass_data.empty:
            st.dataframe(pass_data) 
        else:
            st.write("No files in pass folder.")

        st.markdown("---")
        st.markdown("### Fail Folder")
        fail_data = create_file_dataframe(fail_folder)
        if not fail_data.empty:
            st.dataframe(fail_data) 
        else:
            st.write("No files in fail folder.")

with tab2:
    st.header("🔄 Retrieve Files to Source Folder")

    retrieved_files = []  # Initialize the list to track moved files

    with st.container():
        st.subheader("1. Select Files to Retrieve")

        st.markdown("#### 📂 Files in Pass Folder")
        pass_files = list_files(pass_folder)
        selected_pass = []
        if pass_files:
            selected_pass = st.multiselect(
                "Select files to retrieve from Pass folder:",
                pass_files,
                key="pass_folder_multiselect", 
            )
        else:
            st.write("No files to retrieve from Pass folder.")

        st.markdown("#### Files in Fail Folder")
        fail_files = list_files(fail_folder)
        selected_fail = []
        if fail_files:
            selected_fail = st.multiselect(
                "Select files to retrieve from Fail folder:",
                fail_files,
                key="fail_folder_multiselect",  
            )
        else:
            st.write("No files to retrieve from Fail folder.")

        if st.button("Retrieve Selected Files"):
            if selected_pass:
                moved_pass = retrieve_files(selected_pass, pass_folder, source_folder)
                retrieved_files.extend(moved_pass)

            if selected_fail:
                moved_fail = retrieve_files(selected_fail, fail_folder, source_folder)
                retrieved_files.extend(moved_fail)

            if retrieved_files:
                st.success(f"Retrieved files: {', '.join(retrieved_files)} back to the source folder!")
            else:
                st.info("ℹ️ No files selected for retrieval.")


with tab3:
    st.header("🖊️ E-Sign Document")
    signature_image = st.file_uploader(
        "Choose an image file for your signature", type=["png", "jpg", "jpeg"], key="signature_uploader"
    )
    signer_name = st.text_input("Enter your name", key="signer_name")
    pass_files = list_files(pass_folder)

    if pass_files:
        file_to_sign = st.selectbox("Select a document to sign", pass_files)
        selected_file_path = os.path.join(pass_folder, file_to_sign)

        if st.button("Apply Signature") and signature_image and signer_name:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(signature_image.read())
                signature_path = tmp.name

            signed_file_path = add_signature_to_pdf(
                selected_file_path, signature_path, signed_folder, signer_name
            )
            if signed_file_path:
                st.success(f"Signed {file_to_sign} successfully!")
                with open(signed_file_path, "rb") as file:
                    st.download_button(
                        "Download Signed Document",
                        data=file,
                        file_name=os.path.basename(signed_file_path),
                        mime="application/pdf",
                    )
    else:
        st.warning("No files available to sign in the Pass folder.")

with tab4:
    st.header("📊 Signing Log")
    try:
        if os.path.exists(log_file):
            log_data = pd.read_csv(log_file)
            if log_data.empty:
                st.warning("The signing log is empty.")
            else:
                st.dataframe(log_data)
        else:
            st.warning("The signing log file does not exist.")
    except Exception as e:
        st.error(f"Error loading signing log: {e}")
