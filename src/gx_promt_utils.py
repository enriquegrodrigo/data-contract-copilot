# Preparar toda esta información para un prompt de LLM
import json
from datetime import datetime

from pandas import DataFrame

from src.expectations import (  # Importar todos los modelos de expectativas
    ExpectColumnMaxToBeBetween, ExpectColumnMeanToBeBetween,
    ExpectColumnMinToBeBetween, ExpectColumnSumToBeBetween,
    ExpectColumnToExist, ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToBeInSet, ExpectColumnValuesToBeOfType,
    ExpectColumnValuesToBeUnique, ExpectColumnValuesToMatchRegex,
    ExpectColumnValuesToNotBeNull, ExpectCompoundColumnsToBeUnique,
    ExpectTableRowCountToBeBetween, convert_model_to_str)


def get_pydantic_expectations_info():
    """
    Extrae información de los modelos Pydantic de expectativas
    en lugar de usar la configuración YAML
    """
    # Lista de todos los modelos de expectativas
    expectation_models = [
        ExpectColumnToExist, ExpectColumnValuesToNotBeNull, ExpectColumnValuesToBeUnique,
        ExpectCompoundColumnsToBeUnique, ExpectColumnValuesToBeInSet,
        ExpectColumnValuesToMatchRegex, ExpectColumnValuesToBeBetween,
        ExpectColumnValuesToBeOfType, ExpectColumnValuesToMatchStrftimeFormat,
        ExpectColumnMeanToBeBetween, ExpectTableRowCountToBeBetween, ExpectColumnMinToBeBetween,
        ExpectColumnMaxToBeBetween, ExpectColumnSumToBeBetween
    ]

    expectations_info = []

    for model in expectation_models:
        expectations_info.append(convert_model_to_str(model))

    return expectations_info


def format_pydantic_expectations_for_prompt(expectations_info):
    """
    Formatea la información de expectativas extraída de Pydantic para el prompt del LLM
    """
    if not expectations_info:
        return "No hay información de expectativas disponible."

    formatted_text = "EXPECTATIVAS DE GREAT EXPECTATIONS PERMITIDAS (desde modelos Pydantic):\n\n"

    for exp in expectations_info:
        formatted_text += f"{exp}\n"

    return formatted_text


def prepare_data_analysis_prompt(data_profile: dict, df: DataFrame, documentation: str):
    """
    Prepara toda la información extraída (datos, documentación, perfil)
    para ser enviada a un LLM para análisis de calidad de datos
    Ahora usa información extraída de modelos Pydantic en lugar de YAML
    """

    prompt_data = {
        "context": {
            "task": "Análisis de calidad de datos para generar reglas de Great Expectations",
            "dataset_name": "orders",
            "analysis_date": datetime.now().isoformat()
        },

        "dataset_info": {
            "shape": data_profile["shape"] if data_profile else None,
            "total_rows": data_profile["shape"][0] if data_profile else None,
            "total_columns": data_profile["shape"][1] if data_profile else None,
            "sample_data": df.head(3).to_dict('records') if df is not None else None
        },

        "column_analysis": data_profile["columns"] if data_profile else {},

        "documentation": {
            "content": documentation,
            "length": len(documentation) if documentation else 0,
            "available": documentation is not None
        },

        "data_quality_observations": {
            "columns_with_nulls": [
                col for col, info in (data_profile["columns"] if data_profile else {}).items()
                if info["null_count"] > 0
            ],
            "potential_id_columns": [
                col for col, info in (data_profile["columns"] if data_profile else {}).items()
                if data_profile and info["unique_count"] == data_profile["shape"][0]
            ],
            "categorical_columns": [
                col for col, info in (data_profile["columns"] if data_profile else {}).items()
                if info.get("is_categorical", False)
            ],
            "numeric_columns": [
                col for col, info in (data_profile["columns"] if data_profile else {}).items()
                if info["dtype"] in ["int64", "float64"]
            ]
        },

        # Nueva sección: información de expectativas desde modelos Pydantic
        "pydantic_expectations_info": get_pydantic_expectations_info()
    }

    return prompt_data


def create_llm_prompt(prompt_data):
    """
    Crea un prompt estructurado para el LLM basado en los datos analizados
    Ahora incluye información de expectativas extraída de modelos Pydantic
    """

    # Formatear expectativas Pydantic para el prompt
    expectations_text = format_pydantic_expectations_for_prompt(
        prompt_data.get('pydantic_expectations_info', {})
    )

    # Incluir información específica de columnas categóricas en el prompt
    categorical_info = ""
    if prompt_data['data_quality_observations']['categorical_columns']:
        categorical_info = "\n## INFORMACIÓN DETALLADA DE COLUMNAS CATEGÓRICAS\n"
        for col in prompt_data['data_quality_observations']['categorical_columns']:
            col_info = prompt_data['column_analysis'].get(col, {})
            if col_info.get('is_categorical'):
                categorical_info += f"- {col}: valores posibles = {col_info.get('unique_values', [])}\n"
                categorical_info += f"  frecuencias = {col_info.get('value_frequencies', {})}\n"

    prompt = f"""
Eres un experto en calidad de datos y Great Expectations. Tu tarea es analizar la documentación y el resumen de datos proporcionados
para identificar un conjunto de reglas de calidad iniciales que sean críticas para el negocio y detectables con Great Expectations.

IMPORTANTE: Solo puedes usar las expectativas de Great Expectations que están definidas en los modelos Pydantic proporcionados.

## INFORMACIÓN DEL DATASET
- Nombre: {prompt_data['context']['dataset_name']}
- Filas: {prompt_data['dataset_info']['total_rows']}
- Columnas: {prompt_data['dataset_info']['total_columns']}

## MUESTRA DE DATOS
{json.dumps(prompt_data['dataset_info']['sample_data'], indent=2, ensure_ascii=False)}

## ANÁLISIS POR COLUMNA
{json.dumps(prompt_data['column_analysis'], indent=2, ensure_ascii=False)}

## OBSERVACIONES DE CALIDAD
- Columnas con nulos: {prompt_data['data_quality_observations']['columns_with_nulls']}
- Posibles columnas ID: {prompt_data['data_quality_observations']['potential_id_columns']}
- Columnas categóricas: {prompt_data['data_quality_observations']['categorical_columns']}
- Columnas numéricas: {prompt_data['data_quality_observations']['numeric_columns']}{categorical_info}

## DOCUMENTACIÓN DISPONIBLE
{prompt_data['documentation']['content'] if prompt_data['documentation']['available'] else 'No hay documentación disponible'}

## {expectations_text}

## INSTRUCCIONES
Por favor, analiza esta información y genera un GreatExpectationsSuite completo con:

1. **Reglas de validación críticas para este dataset**
   - Usa SOLO las expectativas definidas en los modelos Pydantic listados arriba
   - Especifica exactamente qué expectativa usar y con qué parámetros
   - Prioriza reglas críticas para la integridad del negocio

2. **Expectativas específicas recomendadas**
   - Para columnas categóricas, usa los valores exactos observados en expect_column_values_to_be_in_set
   - Para columnas numéricas, define rangos apropiados con expect_column_values_to_be_between
   - Para columnas ID, usa expect_column_values_to_be_unique
   - Para completitud, usa expect_column_values_to_not_be_null con parámetro 'mostly' apropiado

3. **Metadatos detallados**
   - Proporciona IDs descriptivos para cada expectativa
   - Incluye descripciones claras de por qué cada expectativa es importante
   - Especifica la fuente de la recomendación (datos observados, documentación, etc.)

4. **Uso de información categórica específica**
   - Para las columnas categóricas detectadas, usa los valores únicos exactos observados
   - Considera las frecuencias para determinar si usar parámetro 'mostly'

RESTRICCIONES CRÍTICAS:
- NUNCA inventes expectativas que no estén en los modelos Pydantic
- SIEMPRE usa los nombres exactos de parámetros definidos en los modelos
- USA los valores categóricos exactos observados en los datos
- Considera los parámetros requeridos vs opcionales según los modelos Pydantic
- Usa parámetros 'mostly' cuando sea apropiado para tolerancia realista
"""

    return prompt
