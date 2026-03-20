# ✨ Premium PDF Splitter Portal

A modern, Streamlit-based web application to intelligently split PDF files based on rule-based Table of Contents (TOC) extraction for **Life** and **NL** configurations.

## 🚀 Features
- **Intelligent Processing**: Automatically splits PDFs using predefined `life` and `nl` business rules.
- **Dynamic Configuration**: View and edit `nl.json` and `life.json` extraction rules directly from the UI.
- **Seamless Document Handling**: Automatically cleans up previous uploads and generated files to ensure privacy and save space.
- **Easy Exporting**: Download individual split sections or grab everything at once in a neat ZIP file.
- **Premium UI**: Designed with Streamlit for a fast, responsive, and beautiful user experience.

## 🛠️ Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   cd nl_life_splitter
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have `streamlit` and `PyMuPDF` / `fitz` installed. Refer to your project environment for exact requirements.)*

## 💻 Usage

Run the Streamlit application using the following command:
```bash
streamlit run streamlit_app.py
```

### How to Use the App:
1. **Upload**: Drag and drop your PDF file into the main upload area.
2. **Configure (Optional)**: Open the "Show/Hide System Configurations" expander on the right side to view or adjust the extraction logic.
3. **Select Mode**: Choose between "NL Splitter" and "Life Splitter" using the radio buttons.
4. **Split**: Click the **✨ Split PDF** button to process the document.
5. **Download**: Use the dropdown to download individual PDF parts or click **📦 Download All as ZIP** to get them all at once.
