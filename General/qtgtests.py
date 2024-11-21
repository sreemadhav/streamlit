import streamlit as st
import os
import shutil
import base64
import fitz
import tempfile
import datetime

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

for folder in [source_folder, pass_folder, fail_folder, signed_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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

# Sidebar for Navigation (optional)
st.sidebar.header("QTG Review System")
st.sidebar.markdown("Manage and review your QTG files efficiently.")

# Function to create a download link for a file
def get_file_link(file_path):
    with open(file_path, "rb") as f:
        pdf_data = f.read()
        b64 = base64.b64encode(pdf_data).decode()  # Encode to base64
        return f'<a href="data:application/pdf;base64,{b64}" target="_blank">Open PDF</a>'

# Function to add signature image to pdf
def add_signature_to_pdf(pdf_path, signature_path, signed_folder):
    try:
        # Open the PDF and load the signature image
        doc = fitz.open(pdf_path)
        signature_img = fitz.open(signature_path)

        # Get the current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Set the dimensions and position for the signature image on the first page
        page = doc[0]  # Only modify the first page
        top_margin = 20  # Distance from the top of the page
        x = 50  # Horizontal position 
        image_width = 150  # Width of the image 
        image_height = 150  # Height of the image 

        # Define the position rectangle for the signature
        image_rect = fitz.Rect(x, top_margin, x + image_width, top_margin + image_height)

        # Insert the image on the first page
        page.insert_image(image_rect, filename=signature_path)

        # Add the current date and time to the PDF
        text_rect = fitz.Rect(x, top_margin + image_height + 5, x + 200, top_margin + image_height + 25)  # Position for date-time
        page.insert_text(text_rect.tl, f"Signed on: {current_datetime}", fontsize=10)

        # Ensure the file name is the same, and create the full path for the signed file
        signed_file_path = os.path.join(signed_folder, os.path.basename(pdf_path))

        # Save the signed PDF directly in the signed folder with the same name
        doc.save(signed_file_path)
        doc.close()

        # Return the path to the signed document
        return signed_file_path

    except Exception as e:
        st.error(f"Error signing PDF: {e}")
        return None
    

# Main Layout with Tabs
tab1, tab2, tab3 = st.tabs(["📂 Manage QTG Files", "🔄 Retrieve Files", "🖊️ E-Sign Document"])

with tab1:
    st.header("📁 QTG Review and Classification")

    # Section to Review and Move Files
    with st.container(border=True):
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
    with st.container(border=True):
        st.subheader("2. View Folder Contents")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📂 Source Folder")
            source_contents = list_files(source_folder)
            if source_contents:
                for item in source_contents:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No files in source folder.")

        with col2:
            st.markdown("### Pass Folder")
            pass_contents = list_files(pass_folder)
            if pass_contents:
                for item in pass_contents:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No files in pass folder.")

        with col3:
            st.markdown("### Fail Folder")
            fail_contents = list_files(fail_folder)
            if fail_contents:
                for item in fail_contents:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No files in fail folder.")

with tab2:
    st.header("🔄 Retrieve Files to Source Folder")

    # Section to Retrieve Files
    with st.container(border=True):
        st.subheader("1. Select Files to Retrieve")

        # Retrieve from Pass Folder
        st.markdown("#### 📂 Files in Pass Folder")
        pass_files = list_files(pass_folder)
        selected_pass = []
        if pass_files:
            selected_pass = st.multiselect("Select files to retrieve from Pass folder:", pass_files)
        else:
            st.write("No files to retrieve from Pass folder.")

        # Retrieve from Fail Folder
        st.markdown("#### Files in Fail Folder")
        fail_files = list_files(fail_folder)
        selected_fail = []
        if fail_files:
            selected_fail = st.multiselect("Select files to retrieve from Fail folder:", fail_files)
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
    with st.container(border=True):
        st.subheader("2. Updated Folder Contents")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📂 Source Folder")
            source_contents = list_files(source_folder)
            if source_contents:
                for item in source_contents:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No files in source folder.")

        with col2:
            st.markdown("### Pass Folder")
            pass_contents = list_files(pass_folder)
            if pass_contents:
                for item in pass_contents:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No files in pass folder.")

        with col3:
            st.markdown("### Fail Folder")
            fail_contents = list_files(fail_folder)
            if fail_contents:
                for item in fail_contents:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No files in fail folder.")

with tab3:
    st.header("🖊️ E-Sign Document")
    
    # Step 1: Upload Signature Image
    st.subheader("Upload Signature Image")
    signature_image = st.file_uploader("Choose an image file for your signature", type=["png", "jpg", "jpeg"])

    # Check if the signature image is uploaded
    signature_path = None
    if signature_image:
        st.image(signature_image, caption="Uploaded Signature Image", use_column_width=True)
        
        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(signature_image.read())
            signature_path = tmp.name

            # If the signature is not uploaded, show a warning
    if signature_path is None:
        st.warning("Please upload a signature image before proceeding.")

    # Step 2: Select Document to Sign
    st.subheader("Select Document to Sign")
    pass_files = list_files(pass_folder)
    
    if pass_files:
        file_to_sign = st.selectbox("Select a document to sign", pass_files)
        selected_file_path = os.path.join(pass_folder, file_to_sign)

        # Step 3: Apply Signature
        if st.button("Apply Signature") and signature_path:
            signed_file_path = add_signature_to_pdf(selected_file_path, signature_path, signed_folder)
            if signed_file_path:
                st.success(f"Signature applied to {file_to_sign} successfully!")

                # Provide the download button for the signed document
                with open(signed_file_path, "rb") as file:
                    st.download_button(
                        label="Download Signed Document",
                        data=file,
                        file_name=file_to_sign,
                        mime="application/pdf"
                    )
    else:
        st.warning("No documents available to sign in the Pass folder.")
