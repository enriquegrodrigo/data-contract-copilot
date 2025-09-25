import instructor
import json
import streamlit as st
import pandas as pd

from openai import OpenAI

from src.expectations import GreatExpectationsSuite
from src.gx_promt_utils import prepare_data_analysis_prompt, create_llm_prompt
from src.gx_data_extractor import DataExtractor
from src.expectation_manager import create_manager


@st.cache_resource
def llm_configuration_generation(csv_file, doc_file, openai_api_key):
    """
    Genera un archivo de configuración de Great Expectations basado en un LLM
    usando la muestra de datos y la descripción del contrato de datos proporcionados.
    """
    st.write("Loading and processing files...")
    extractor = DataExtractor(csv_file, doc_file)
    df = extractor.load_csv()
    documentation = extractor.load_documentation()
    data_profile = extractor.get_data_profile()

    st.write("Creating data structure for LLM prompt...")
    prompt_data = prepare_data_analysis_prompt(data_profile, df, documentation)

    st.write("Generating LLM prompt...")
    llm_prompt = create_llm_prompt(prompt_data)

    st.write("Connecting to OpenAI...")
    client = instructor.from_openai(
        OpenAI(api_key=openai_api_key)
    )

    st.write("Sending LLM prompt to OpenAI...")
    resp = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": llm_prompt},
            {"role": "user", "content": "Generate a complete great expectations suite with the information you have."}
        ],
        response_model=GreatExpectationsSuite,
        max_retries=10
    )
    return resp


def transform_json_structure(df):
    # Initialize the output structure
    output = {"expectations": []}

    # Iterate through each row using integer index
    print(f'pintemos df: {df}')
    for i in range(len(df)):
        if df['enabled'][str(i)] is True:
            expectation = {
                "id": df["id"][str(i)],
                "expectation": df["expectation"][str(i)],
                "description": df["description"][str(i)],
                "source": df["source"][str(i)],
                "severity": df["severity"][str(i)]
            }
            output["expectations"].append(expectation)

    return output


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
    "Upload sample data (csv) and description of the data contract (md):",
    type=["csv", "md", "txt"], accept_multiple_files=True
)
# sample_data_file = 0
csv_file = None
# data_contract_description_file = 0
doc_file = None
extra_files = False

if uploaded_files is not None:
    for file in uploaded_files:
        if file.type == "text/csv" and not csv_file:
            st.write(f"Sample data uploaded: {file.name}")
            # sample_data_file += 1
            csv_file = file
            extra_files = False
        elif file.type in ["text/plain", "application/octet-stream"] and not doc_file:
            st.write(f"Data contract description uploaded: {file.name}")
            # data_contract_description_file += 1
            doc_file = file
            extra_files = False
        else:
            st.error(
                "Please upload only one sample data (CSV) file and one data contract "
                "description (TXT) file."
            )
            extra_files = True


if csv_file and doc_file and not extra_files:
    st.success("Both files uploaded successfully!")
    with st.status("Generating configuration...") as status:
        resp = llm_configuration_generation(csv_file, doc_file, openai_api_key)
        status.update(
            label="Configuration generated successfully!", state="complete", expanded=False
        )

    data = json.loads(resp.model_dump_json(indent=2))['expectations']
    for item in data:
        item['enabled'] = True
    data_table = pd.DataFrame(data)
    edited_data = st.data_editor(
        data_table,
        column_config={
            'id': 'Rule Name',
            'expectation': 'Params',
            'severity': 'Severity',
            'source': 'Source',
            'description': 'Description',
            'enabled': st.column_config.CheckboxColumn('Enabled', help='Enable or disable this rule', default=True)
        },
        column_order=('id', 'expectation', 'severity', 'source', 'description', 'enabled'),
        width="stretch",
        hide_index=True
    )
    edited_dataframe = pd.DataFrame(edited_data)
    transformed_json = transform_json_structure(edited_data)
    st.json(transformed_json)
    st.json(resp.model_dump_json(indent=2))
    manager = create_manager()
    st.write(manager.validate_pydantic_suite(edited_data)[0])
