import streamlit as st
import os
import shutil
import json
import fitz
import zipfile
import io
from life_splitter import get_life_toc
from nl_splitter import get_nl_toc

# App Configuration
st.set_page_config(page_title="PDF Splitter Portal", page_icon="📄", layout="wide")

# Directory setup
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

def setup_directories():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def cleanup_directories():
    for d in [UPLOAD_DIR, OUTPUT_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
    setup_directories()

# Initialize session state for tracking current upload
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'split_files' not in st.session_state:
    st.session_state.split_files = []

def split_pdf_by_toc(pdf_path, toc, output_dir):
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    generated_files = []
    
    for i in range(len(toc)):
        start_page = toc[i]['page']
        end_page = toc[i+1]['page'] - 1 if i + 1 < len(toc) else num_pages - 1
        
        if end_page < start_page:
            end_page = start_page
            
        topic = toc[i]['topic']
        safe_topic = "".join([c for c in topic if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
        
        split_doc = fitz.open()
        split_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
        
        output_filename = f"{safe_topic}.pdf"
        output_filepath = os.path.join(output_dir, output_filename)
        
        counter = 1
        while os.path.exists(output_filepath):
            output_filepath = os.path.join(output_dir, f"{safe_topic}_{counter}.pdf")
            counter += 1
            
        split_doc.save(output_filepath)
        split_doc.close()
        generated_files.append(output_filepath)
        
    doc.close()
    return generated_files

def create_zip(file_paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            zip_file.write(file_path, arcname=file_name)
    return zip_buffer.getvalue()

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "[]"

def save_json(filepath, data_str):
    try:
        parsed = json.loads(data_str)
        with open(filepath, 'w') as f:
            json.dump(parsed, f, indent=4)
        return True, "Saved successfully!"
    except json.JSONDecodeError:
        return False, "Invalid JSON format."
    except Exception as e:
        return False, f"Error saving: {e}"

# UI Layout
st.title("✨ Premium PDF Splitter Portal")
st.markdown("Easily split your PDFs based on rule-based TOC extraction for Life and NL configurations.")

# Split view for main application and sidebar/expander for config
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("⚙️ System Rules")
    with st.expander("🛠️ Show/Hide Configurations", expanded=False):
        st.info("Modify the JSON rules used by the Auto Splitter.")
        conf_tab1, conf_tab2 = st.tabs(["📄 NL Rules", "💚 Life Rules"])
        
        with conf_tab1:
            nl_data = load_json('nl.json')
            nl_input = st.text_area("JSON Settings", value=nl_data, height=400, key="nl_config", help="Edit the NL extraction logic.")
            if st.button("💾 Save NL Config", use_container_width=True):
                success, msg = save_json('nl.json', nl_input)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                
        with conf_tab2:
            life_data = load_json('life.json')
            life_input = st.text_area("JSON Settings", value=life_data, height=400, key="life_config", help="Edit the Life extraction logic.")
            if st.button("💾 Save Life Config", use_container_width=True):
                success, msg = save_json('life.json', life_input)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

with col1:
    st.subheader("📂 Document Processing")
    
    # Setup directories on load
    setup_directories()

    uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])
    
    # Cleanup detection
    if uploaded_file is not None:
        if st.session_state.current_file != uploaded_file.name:
            cleanup_directories()
            st.session_state.current_file = uploaded_file.name
            st.session_state.split_files = []
            
        # Save uploaded file
        pdf_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Uploaded: {uploaded_file.name}")
        
        tab_auto, tab_manual = st.tabs(["⚡ Auto Splitter", "✂️ Manual Splitter"])
        
        with tab_auto:
            splitter_type = st.radio("Select Splitter Type:", ("NL Splitter", "Life Splitter"), horizontal=True)
            
            if st.button("✨ Auto Split PDF", type="primary"):
                with st.spinner("Extracting TOC and Splitting PDF..."):
                    try:
                        if splitter_type == "NL Splitter":
                            toc = get_nl_toc(pdf_path)
                        else:
                            toc = get_life_toc(pdf_path)
                            
                        if not toc:
                            st.warning("No sections found to split.")
                        else:
                            st.write("### Extracted TOC:")
                            st.dataframe(toc, use_container_width=True)
                            
                            split_files = split_pdf_by_toc(pdf_path, toc, OUTPUT_DIR)
                            st.session_state.split_files = split_files
                            st.success(f"Successfully split into {len(split_files)} parts!")
                    except Exception as e:
                        st.error(f"An error occurred during splitting: {e}")

        with tab_manual:
            st.markdown("Extract a specific page range from the uploaded PDF.")
            try:
                doc = fitz.open(pdf_path)
                max_pages = len(doc)
                doc.close()
            except:
                max_pages = 1
                
            c1, c2 = st.columns(2)
            with c1:
                start_p = st.number_input("Start Page (1-indexed)", min_value=1, max_value=max_pages, value=1)
            with c2:
                end_p = st.number_input("End Page (1-indexed)", min_value=1, max_value=max_pages, value=max_pages)
                
            out_name = st.text_input("Output File Name", value="manual_split")
            
            if st.button("✂️ Extract Pages", type="primary"):
                if start_p <= end_p:
                    with st.spinner("Extracting pages..."):
                        try:
                            temp_doc = fitz.open(pdf_path)
                            split_doc = fitz.open()
                            split_doc.insert_pdf(temp_doc, from_page=start_p-1, to_page=end_p-1)
                            safe_name = "".join([c for c in out_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
                            if not safe_name: safe_name = "manual_split"
                            out_file = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")
                            
                            counter = 1
                            while os.path.exists(out_file):
                                out_file = os.path.join(OUTPUT_DIR, f"{safe_name}_{counter}.pdf")
                                counter += 1
                                
                            split_doc.save(out_file)
                            split_doc.close()
                            temp_doc.close()
                            
                            if out_file not in st.session_state.split_files:
                                st.session_state.split_files.append(out_file)
                            st.success(f"Extracted pages {start_p} to {end_p} into {os.path.basename(out_file)}!")
                        except Exception as e:
                            st.error(f"Error during manual extraction: {e}")
                else:
                    st.error("Start page must be less than or equal to end page.")

    # Results section
    if st.session_state.split_files:
        st.divider()
        st.subheader("📥 Download Results")
        
        def get_pdf_info(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            size_str = f"{size_kb:.1f}KB" if size_kb < 1024 else f"{size_kb/1024:.1f}MB"
            try:
                doc = fitz.open(filepath)
                pages = len(doc)
                doc.close()
            except:
                pages = "?"
            return f"{size_str}, {pages} page{'s' if pages != 1 else ''}"

        display_options = {}
        for f in st.session_state.split_files:
            bname = os.path.basename(f)
            info = get_pdf_info(f)
            display_name = f"{bname} ({info})"
            display_options[display_name] = f
            
        selected_display = st.selectbox("View Generated PDFs:", list(display_options.keys()))
        
        if selected_display:
            selected_path = display_options[selected_display]
            selected_file = os.path.basename(selected_path)
            with open(selected_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label=f"Download {selected_file}",
                data=pdf_bytes,
                file_name=selected_file,
                mime="application/pdf",
                key="single_download"
            )
            
        st.markdown("#### Bulk Download")
        zip_data = create_zip(st.session_state.split_files)
        st.download_button(
            label="📦 Download All as ZIP",
            data=zip_data,
            file_name="split_pdfs.zip",
            mime="application/zip",
            type="primary"
        )
