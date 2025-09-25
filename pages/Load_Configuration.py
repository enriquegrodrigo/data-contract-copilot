import time

import streamlit as st
import pandas as pd


st.set_page_config(page_title="Load Configuration", page_icon="⚙️")

st.markdown("# Load Configuration")
st.sidebar.header("Configuration")
openai_api_key = st.sidebar.text_input("OpenAI API Key", key="api_key", type="password")
st.write(
    """
    This is a load test of a configuration file for data contracts.
    You need to upload two files:
    1. A sample data file (.csv format)
    2. A configuration file of the data contract (.json or .yaml format)

    After uploading the files, the application will process them and show a table with the data and the configuration.
    """
)

uploaded_files = st.file_uploader(
    "Upload sample data (csv) and the configuration file of the data contract (json or yaml):",
    type=["csv", "json", "yaml"], accept_multiple_files=True
)
sample_data_file = 0
data_contract_configuration_file = 0

if uploaded_files is not None:
    for file in uploaded_files:
        if file.type == "text/csv":
            st.write(f"Sample data uploaded: {file.name}")
            sample_data_file += 1
        elif file.type == "text/json" or file.type == "application/x-yaml":
            st.write(f"Data contract configuration file uploaded: {file.name}")
            data_contract_configuration_file += 1
        if sample_data_file > 1 or data_contract_configuration_file > 1:
            st.error(
                "Please upload only one sample data (CSV) file and one data contract "
                "configuration (JSON, YAML) file."
            )

if sample_data_file == 1 and data_contract_configuration_file == 1:
    st.success("Both files uploaded successfully!")
    test_data = {
        "data_contract": {
            "expectations": [
                {"name": "field1", "type": "string", "constraints": '{"max_length": 255}'},
                {"name": "field2", "type": "integer", "constraints": '{"min_value": 0}'}
            ],
            "primary_key": ["field1"]
        }
    }
    edited_data = st.data_editor(
        test_data['data_contract']['expectations'], hide_index=True,
        num_rows="dynamic", width="stretch"
    )

    st.success("Configuration tested successfully!")
    df = pd.DataFrame(edited_data)

    # st.download_button(
    #     label="Download CSV",
    #     data=df.to_csv().encode("utf-8"),
    #     file_name="data.csv",
    #     mime="text/csv",
    #     icon=":material/download:"
    # )
    st.download_button(
        label="Download JSON",
        data=df.to_json().encode("utf-8"),
        file_name="data.json",
        mime="application/json",
        icon=":material/download:"
    )
