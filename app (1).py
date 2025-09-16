import streamlit as st
import pandas as pd
import os

# --- Configuration ---
MATERIALS_DIR = "materials"       # Folder for training materials
LOG_FILE = "access_log.xlsx"      # Log file for employee access

# Create materials folder
import zipfile

with zipfile.ZipFile("materials.zip", 'r') as zip_ref:
    zip_ref.extractall()

# --- Utilities ---
def list_materials():
    """Return a sorted list of files in the materials folder."""
    if not os.path.exists(MATERIALS_DIR):
        os.makedirs(MATERIALS_DIR, exist_ok=True)
    return sorted([
        f for f in os.listdir(MATERIALS_DIR)
        if os.path.isfile(os.path.join(MATERIALS_DIR, f))
    ])

def record_access(name, email, material):
    """Record the employee's access in the Excel log."""
    if not name or not email:
        return False, "❌ Please enter both Name and Email."
    new_entry = pd.DataFrame([[name, email, material]],
                             columns=["Name", "Email", "Material"])
    if os.path.exists(LOG_FILE):
        existing = pd.read_excel(LOG_FILE)
        updated = pd.concat([existing, new_entry], ignore_index=True)
    else:
        updated = new_entry
    updated.to_excel(LOG_FILE, index=False)
    return True, f"✅ Access recorded for {name}."

# --- Streamlit App ---
st.set_page_config(page_title="Employee Training Portal", layout="centered")
st.title("📂 Employee Training Material Portal")
st.write("Enter your details, choose a training file, and download the material.")

# Step 1: List available training materials
materials = list_materials()

# Step 2: Collect employee details using a form
with st.form("access_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    if not materials:
        st.info("No materials available. Contact the admin to upload files.")
        selected = None
    else:
        selected = st.selectbox("Select Training Material", materials)
    submit = st.form_submit_button("Record Access")

# Step 3: Handle form submission and show download button
if submit:
    if selected:
        success, msg = record_access(name, email, selected)
        if success:
            st.success(msg)
            # Download button placed OUTSIDE the form to avoid errors
            file_path = os.path.join(MATERIALS_DIR, selected)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"⬇ Download '{selected}'",
                        data=f,
                        file_name=selected,
                        mime="application/octet-stream"
                    )
            else:
                st.error("❌ File not found on the server.")
        else:
            st.error(msg)

# --- Admin Section ---
st.markdown("---")
st.subheader("📊 Admin: View and Download Access Log")

if os.path.exists(LOG_FILE):
    df = pd.read_excel(LOG_FILE)
    st.dataframe(df, use_container_width=True)
    with open(LOG_FILE, "rb") as f:
        st.download_button(
            label="⬇ Download Access Log",
            data=f,
            file_name=LOG_FILE,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("No access log available yet.")