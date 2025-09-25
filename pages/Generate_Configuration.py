import json

import instructor
import pandas as pd
import streamlit as st
from openai import OpenAI

from src.expectation_manager import create_manager, save_suite_yaml
from src.expectations import GreatExpectationsSuite
from src.gx_data_extractor import DataExtractor
from src.gx_promt_utils import create_llm_prompt, prepare_data_analysis_prompt


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
        elif file.type in ["text/plain", "application/octet-stream", "text/markdown"] and not doc_file:
            st.write(f"Data contract description uploaded: {file.name}")
            # data_contract_description_file += 1
            doc_file = file
            extra_files = False
        else:
            st.write(file.type)
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
    print(data)

    for item in data:
        item['enabled'] = True
        item['expectation'] = json.dumps(item['expectation'].model_dump())

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
    # Convert edited data back to pydantic model
    def create_modified_pydantic_suite(original_suite, edited_df):
        """
        Create a modified pydantic suite based on user edits
        """


        # Convert edited dataframe to list of dictionaries
        edited_expectations = []

        for i in range(len(edited_df)):
            # Only include enabled expectations
            if edited_df.iloc[i]['enabled']:
                try:
                    # Parse the expectation JSON string from the edited table
                    expectation_json_str = edited_df.iloc[i]['expectation']

                    # If it's already a dict, use it directly, otherwise parse JSON
                    #if isinstance(expectation_json_str, str):
                    expectation_dict = json.loads(expectation_json_str)
                    #else:
                    #    expectation_dict = expectation_json_str

                    # Create the appropriate expectation object based on expectation_type
                    expectation_type = expectation_dict.get('expectation_type')

                    # Import all expectation classes dynamically
                    from src.expectations import (
                        ExpectColumnMaxToBeBetween,
                        ExpectColumnMeanToBeBetween,
                        ExpectColumnMinToBeBetween, ExpectColumnSumToBeBetween,
                        ExpectColumnToExist, ExpectColumnValuesToBeBetween,
                        ExpectColumnValuesToBeInSet,
                        ExpectColumnValuesToBeOfType,
                        ExpectColumnValuesToBeUnique,
                        ExpectColumnValuesToMatchRegex,
                        ExpectColumnValuesToNotBeNull,
                        ExpectTableRowCountToBeBetween)

                    # Map expectation types to their corresponding classes
                    expectation_class_map = {
                        'expect_column_to_exist': ExpectColumnToExist,
                        'expect_column_values_to_not_be_null': ExpectColumnValuesToNotBeNull,
                        'expect_column_values_to_be_unique': ExpectColumnValuesToBeUnique,
                        'expect_column_values_to_be_in_set': ExpectColumnValuesToBeInSet,
                        'expect_column_values_to_match_regex': ExpectColumnValuesToMatchRegex,
                        'expect_column_values_to_be_between': ExpectColumnValuesToBeBetween,
                        'expect_column_values_to_be_of_type': ExpectColumnValuesToBeOfType,
                        'expect_column_mean_to_be_between': ExpectColumnMeanToBeBetween,
                        'expect_table_row_count_to_be_between': ExpectTableRowCountToBeBetween,
                        'expect_column_min_to_be_between': ExpectColumnMinToBeBetween,
                        'expect_column_max_to_be_between': ExpectColumnMaxToBeBetween,
                        'expect_column_sum_to_be_between': ExpectColumnSumToBeBetween,
                    }

                    # Create the expectation object
                    if expectation_type in expectation_class_map:
                        expectation_class = expectation_class_map[expectation_type]
                        expectation_obj = expectation_class(**expectation_dict)
                    else:
                        st.error(f"Unknown expectation type: {expectation_type}")
                        continue

                    # Create the complete expectation with metadata
                    expectation_with_metadata = {
                        'id': edited_df.iloc[i]['id'],
                        'expectation': expectation_obj,
                        'description': edited_df.iloc[i]['description'],
                        'source': edited_df.iloc[i]['source'],
                        'severity': edited_df.iloc[i]['severity']
                    }
                    edited_expectations.append(expectation_with_metadata)

                except (Exception) as e:
                    st.error(f"Error processing expectation {edited_df.iloc[i]['id']}: {e}")
                    continue

        # Create new pydantic model with edited data
        modified_suite_dict = {
            'expectations': edited_expectations,
            # Keep other fields from original suite if they exist
            'name': getattr(original_suite, 'name', 'Generated Suite'),
            'version': getattr(original_suite, 'version', '1.0.0'),
            'description': getattr(original_suite, 'description', 'LLM Generated Data Contract')
        }

        # Create new pydantic instance
        try:
            new_suite = GreatExpectationsSuite(**modified_suite_dict)
            return new_suite
        except (ValueError, TypeError) as e:
            st.error(f"Error creating modified pydantic suite: {e}")
            return None

    # Create the modified pydantic suite
    modified_suite = create_modified_pydantic_suite(resp, edited_data)

    if modified_suite:
        st.success("✅ Modified pydantic suite created successfully!")

        # Display the modified suite
        with st.expander("View Modified Pydantic Suite"):
            st.json(modified_suite.model_dump_json(indent=2))

        # Validate the modified suite
        manager = create_manager()
        validation_result = manager.validate_pydantic_suite(modified_suite)
        st.write("**Validation result:**", validation_result[0])

        gx_suite = manager.pydantic_to_gx_suite(modified_suite)
        suite_validation = manager.validate_gx_suite(gx_suite)
        st.write("**Validation result:**", suite_validation[0])

        # Optional: Save or download the modified suite
        if validation_result[0]:
            st.download_button(
                label="Download YAML Configuration",
                data=manager.serialize_to_yaml(modified_suite),
                file_name="modified_gx_configuration.yaml",
                mime="application/x-yaml"
            )

    # Debug information (can be removed in production)
    with st.expander("Debug Information"):
        st.write("**Edited Data JSON:**")
        st.json(edited_data.to_json())
        st.write("**Original Suite JSON:**")
        st.json(resp.model_dump_json(indent=2))
