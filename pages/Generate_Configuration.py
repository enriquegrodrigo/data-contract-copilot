import streamlit as st

st.set_page_config(page_title="Generate Configuration", page_icon="⚙️")

st.markdown("# Generate Configuration")
st.sidebar.header("Configuration")
openai_api_key = st.sidebar.text_input("OpenAI API Key", key="api_key", type="password")
st.write(
    """
    This is a generation test of a configuration file for data contracts based on a LLM.
    You need to upload two files:
    1. A sample data file (.csv format)
    2. Description of the data contract (.txt format)

    After uploading the files, the application will process them and send them to the LLM to generate a configuration file.
    """
)

uploaded_files = st.file_uploader(
    "Upload sample data (csv) and description of the data contract (txt):",
    type=["csv", "txt"], accept_multiple_files=True
)
sample_data_file = 0
data_contract_description_file = 0

if uploaded_files is not None:
    for file in uploaded_files:
        if file.type == "text/csv":
            st.write(f"Sample data uploaded: {file.name}")
            sample_data_file += 1
        elif file.type == "text/plain":
            st.write(f"Data contract description uploaded: {file.name}")
            data_contract_description_file += 1
        if sample_data_file > 1 or data_contract_description_file > 1:
            st.error(
                "Please upload only one sample data (CSV) file and one data contract "
                "description (TXT) file."
            )

if sample_data_file == 1 and data_contract_description_file == 1:
    st.success("Both files uploaded successfully!")
    if st.button("Generate Configuration"):
        with st.spinner("Generating configuration..."):
            # Here you would add the logic to process the files and generate the configuration
            import time
            time.sleep(3)  # Simulate a delay for processing
        st.success("Configuration generated successfully!")
        st.code(
            """
            {
                "data_contract": {
                    "fields": [
                        {"name": "field1", "type": "string", "constraints": {"max_length": 255}},
                        {"name": "field2", "type": "integer", "constraints": {"min_value": 0}}
                    ],
                    "primary_key": ["field1"]
                }
            }
            """,
            language="json"
        )
