import streamlit as st
import os
import shutil
import base64
import fitz
import tempfile
import datetime
import pandas as pd
import csv

PIN_CODE = "1234"

# Set the page configuration
st.set_page_config(
    page_title="QTG Review System",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define folder paths
source_folder = "source_folder"
pass_folder = "pass_folder"
fail_folder = "fail_folder"
signed_folder = "signed_folder"
log_file = "signing_log.csv"

# Ensure folders exist
for folder in [source_folder, pass_folder, fail_folder, signed_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Ensure signing_log.csv exists with appropriate headers
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Document Name", "Signed By", "Date/Time"])

# Function to safely list directory contents
def list_files(folder):
    try:
        return os.listdir(folder)
    except FileNotFoundError:
        return []

# Function to move a file
def move_file(src, dest):
    try:
        shutil.move(src, dest)
        return True
    except Exception as e:
        st.error(f"Error moving file {src} to {dest}: {e}")
        return False

# Function to retrieve selected files
def retrieve_files(selected_files, src_folder, dest_folder):
    moved_files = []
    for item in selected_files:
        src_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)
        if move_file(src_path, dest_path):
            moved_files.append(item)
    return moved_files

# Function to create a download link for a file
def get_file_link(file_path):
    with open(file_path, "rb") as f:
        pdf_data = f.read()
        b64 = base64.b64encode(pdf_data).decode()
        return f'<a href="data:application/pdf;base64,{b64}" target="_blank">Open PDF</a>'

# Function to add signature to the PDF
def add_signature_to_pdf(pdf_path, signature_path, signed_folder, signer_name):
    try:
        # Open the PDF and load the signature image
        doc = fitz.open(pdf_path)

        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Set the dimensions and position for the signature image on the first page
        page = doc[0]  # Only modify the first page
        top_margin = 20 + 150 * len(doc)  # To stagger signatures (modify based on number of signatures)
        x = 50  # Horizontal position 
        image_width = 150  
        image_height = 150  

        # Define the position rectangle for the signature
        image_rect = fitz.Rect(x, top_margin, x + image_width, top_margin + image_height)

        # Insert the image on the first page
        page.insert_image(image_rect, filename=signature_path)

        # Add the current date and time and signer's name
        text_rect = fitz.Rect(x, top_margin + image_height + 5, x + 200, top_margin + image_height + 25)  # Position for date-time
        page.insert_text(text_rect.tl, f"{signer_name} signed on: {current_datetime}", fontsize=10)

        # Save the signed PDF to the signed folder
        signed_file_path = os.path.join(signed_folder, os.path.basename(pdf_path))
        doc.save(signed_file_path)
        doc.close()

        # Log the signature in the CSV file
        log_signature(signer_name, current_datetime)

        return signed_file_path

    except Exception as e:
        st.error(f"Error signing PDF: {e}")
        return None

def log_signature(signer_name, timestamp):
    try:
        # Check if the log file exists
        if not os.path.exists(log_file):
            # Create a new log file with headers
            df = pd.DataFrame(columns=["Signer", "Timestamp"])
            df.to_csv(log_file, index=False)

        # Append the new signature to the log file
        df = pd.read_csv(log_file)
        df = df.append({"Signer": signer_name, "Timestamp": timestamp}, ignore_index=True)
        df.to_csv(log_file, index=False)

    except Exception as e:
        st.error(f"Error logging signature: {e}")


# Function to create data in DataFrame format for folder contents
def create_file_dataframe(folder_path):
    folder_contents = list_files(folder_path)
    data = [[item] for item in folder_contents]
    return pd.DataFrame(data, columns=["File Name"])

def create_file_dataframe(folder_path):
    folder_contents = list_files(folder_path)
    if folder_contents:  # If there are files in the folder
        data = [[item] for item in folder_contents]
        return pd.DataFrame(data, columns=["File Name"])
    else:  # If the folder is empty
        return pd.DataFrame(columns=["File Name"])


# Main Layout with Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["📂 Manage QTG Files", "🔄 Retrieve Files", "🖊️ E-Sign Document", "📊 Signing Log"]
)

with tab1:
    st.header("📁 QTG Review and Classification")

    # Section to Review and Move Files
    with st.container():
        st.subheader("1. Review QTG Files")
        files = list_files(source_folder)
        
        if files:
            # Select a file to review
            file_to_move = st.selectbox("Select the QTG to review", files)
            
            # Button to open the selected PDF
            pdf_file_path = os.path.join(source_folder, file_to_move)
            if os.path.exists(pdf_file_path):
                # Create an Open PDF button
                open_pdf_link = get_file_link(pdf_file_path)
                st.markdown(open_pdf_link, unsafe_allow_html=True)

            # Select status
            status = st.radio("Status of QTG", ["Pass", "Fail"], horizontal=True)
            
            # Submit button to move the file
            if st.button("Submit"):
                destination_folder = pass_folder if status == "Pass" else fail_folder
                src_path = os.path.join(source_folder, file_to_move)
                dest_path = os.path.join(destination_folder, file_to_move)
                
                if move_file(src_path, dest_path):
                    st.success(f"Moved '{file_to_move}' to **{'Pass' if status == 'Pass' else 'Fail'}** folder.")
        else:
            st.warning("🚫 No files to move in the source folder.")

    st.markdown("---")  # Separator

    # Section to Display Folder Contents
    with st.container():
        st.subheader("2. View Folder Contents")
        
        # Source Folder
        st.markdown("### 📂 Source Folder")
        source_data = create_file_dataframe(source_folder)
        if not source_data.empty:
            st.dataframe(source_data)  # Use st.dataframe instead of st.table
        else:
            st.write("No files in source folder.")

        st.markdown("---")

        # Pass Folder
        st.markdown("### Pass Folder")
        pass_data = create_file_dataframe(pass_folder)
        if not pass_data.empty:
            st.dataframe(pass_data)  # Use st.dataframe instead of st.table
        else:
            st.write("No files in pass folder.")

        st.markdown("---")

        # Fail Folder
        st.markdown("### Fail Folder")
        fail_data = create_file_dataframe(fail_folder)
        if not fail_data.empty:
            st.dataframe(fail_data)  # Use st.dataframe instead of st.table
        else:
            st.write("No files in fail folder.")



with tab2:
    st.header("🔄 Retrieve Files to Source Folder")

    # Section to Retrieve Files
    with st.container():
        st.subheader("1. Select Files to Retrieve")

        # Retrieve from Pass Folder
        st.markdown("#### 📂 Files in Pass Folder")
        pass_files = list_files(pass_folder)
        selected_pass = []
        if pass_files:
            selected_pass = st.multiselect(
                "Select files to retrieve from Pass folder:",
                pass_files,
                key="pass_folder_multiselect",  # Unique key for Pass Folder
            )
        else:
            st.write("No files to retrieve from Pass folder.")

        # Retrieve from Fail Folder
        st.markdown("#### Files in Fail Folder")
        fail_files = list_files(fail_folder)
        selected_fail = []
        if fail_files:
            selected_fail = st.multiselect(
                "Select files to retrieve from Fail folder:",
                fail_files,
                key="fail_folder_multiselect",  # Unique key for Fail Folder
            )
        else:
            st.write("No files to retrieve from Fail folder.")

        # Button to retrieve selected files
        if st.button("Retrieve Selected Files"):
            retrieved_files = []

            # Retrieve from Pass Folder
            if selected_pass:
                moved_pass = retrieve_files(selected_pass, pass_folder, source_folder)
                retrieved_files.extend(moved_pass)

            # Retrieve from Fail Folder
            if selected_fail:
                moved_fail = retrieve_files(selected_fail, fail_folder, source_folder)
                retrieved_files.extend(moved_fail)

            if retrieved_files:
                st.success(f"Retrieved files: {', '.join(retrieved_files)} back to the source folder!")
            else:
                st.info("ℹ️ No files selected for retrieval.")

    st.markdown("---")  # Separator

    # Section to Display Updated Folder Contents
    with st.container():
        st.subheader("2. Updated Folder Contents")
        
        # Display tables for updated folder contents
        st.markdown("### 📂 Source Folder")
        source_data = create_file_dataframe(source_folder)
        if not source_data.empty:
            st.dataframe(source_data)  # Use st.dataframe instead of st.table
        else:
            st.write("No files in source folder.")

        st.markdown("---")

        st.markdown("### Pass Folder")
        pass_data = create_file_dataframe(pass_folder)
        if not pass_data.empty:
            st.dataframe(pass_data)  # Use st.dataframe instead of st.table
        else:
            st.write("No files in pass folder.")

        st.markdown("---")

        st.markdown("### Fail Folder")
        fail_data = create_file_dataframe(fail_folder)
        if not fail_data.empty:
            st.dataframe(fail_data)  # Use st.dataframe instead of st.table
        else:
            st.write("No files in fail folder.")


# Tab for signing documents
with tab3:
    st.header("🖊️ E-Sign Document")
    
    # Step 1: Upload Signature Image
    st.subheader("Upload Signature Image")
    signature_image = st.file_uploader("Choose an image file for your signature", type=["png", "jpg", "jpeg"], key="signature_uploader")

    # Check if the signature image is uploaded
    signature_path = None
    if signature_image:
        st.image(signature_image, caption="Uploaded Signature Image", use_column_width=True)
        
        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(signature_image.read())
            signature_path = tmp.name

    if signature_path is None:
        st.warning("Please upload a signature image before proceeding.")

    # Step 2: Select Document to Sign
    st.subheader("Select Document to Sign")
    pass_files = list_files(pass_folder)
    
    if pass_files:
        file_to_sign = st.selectbox("Select a document to sign", pass_files)
        selected_file_path = os.path.join(pass_folder, file_to_sign)
        st.info('This action cannot be reversed once applied', icon="🚨")

        # Step 3: Enter PIN Code for Signature
        pin_code = st.text_input("Enter PIN Code to apply signature", type="password")

        # Step 4: Enter Signer's Name
        signer_name = st.text_input("Enter your name")

        # Step 5: Apply Signature
        if st.button("Apply Signature") and signature_path:
            if pin_code == PIN_CODE:  # Check if the PIN code is correct
                if signer_name.strip() != "":
                    signed_file_path = add_signature_to_pdf(selected_file_path, signature_path, signed_folder, signer_name)
                    if signed_file_path:
                        st.success(f"Signature applied by {signer_name} successfully!")

                        # Provide the download button for the signed document
                        with open(signed_file_path, "rb") as file:
                            st.download_button(
                                label="Download Signed Document",
                                data=file,
                                file_name=file_to_sign,
                                mime="application/pdf"
                            )
                else:
                    st.error("Please enter your name.")
            else:
                st.error("Incorrect PIN Code. Please try again.")
    else:
        st.warning("No documents available to sign in the Pass folder.")

    # Step 6: Display Signature Log
    st.subheader("Signature Log")
    if os.path.exists(log_file):
        log_df = pd.read_csv(log_file)
        st.write(log_df)
    else:
        st.warning("No signatures yet.")


with tab4:
    st.header("📊 Signing Log")
    try:
        log_data = pd.read_csv(log_file)
        st.dataframe(log_data)
    except Exception as e:
        st.error(f"Error loading signing log: {e}")
