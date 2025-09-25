import great_expectations as gx


def run_gx_dataset_validation(gx_suite, df):
    fresh_context = gx.get_context()

    # 1. Crear datasource, asset y batch en una secuencia
    ds = fresh_context.data_sources.add_pandas(name="direct_datasource")
    asset = ds.add_dataframe_asset(name="direct_asset")
    batch_def = asset.add_batch_definition_whole_dataframe(name="direct_batch")

    # 2. Agregar suite
    fresh_context.suites.add(gx_suite)

    # 3. Crear y agregar validation definition
    val_def = gx.ValidationDefinition(
        suite=gx_suite,
        data=batch_def,
        name="direct_validation"
    )
    fresh_context.validation_definitions.add(val_def)

    return val_def.run(batch_parameters={"dataframe": df})


def analyze_validation_results(validation_result):
    """
    Analiza los resultados de validación de Great Expectations y retorna un resumen estructurado
    para cada expectativa con información detallada sobre éxitos y fallos.

    Args:
        validation_result: Resultado de validación de Great Expectations (dict o objeto)

    Returns:
        dict: Diccionario con resumen ejecutivo y detalles por expectativa
    """
    # Convertir a dict si es necesario
    if hasattr(validation_result, 'to_json_dict'):
        result_dict = validation_result.to_json_dict()
    elif hasattr(validation_result, '__dict__'):
        result_dict = validation_result.__dict__
    else:
        result_dict = validation_result

    # Extraer información principal
    overall_success = result_dict.get('success', False)
    results = result_dict.get('results', [])
    statistics = result_dict.get('statistics', {})

    # Resumen ejecutivo
    executive_summary = {
        'overall_success': overall_success,
        'total_expectations': statistics.get('evaluated_expectations', len(results)),
        'successful_expectations': statistics.get('successful_expectations', 0),
        'failed_expectations': statistics.get('unsuccessful_expectations', 0),
        'success_percentage': statistics.get('success_percent', 0.0),
        'validation_time': result_dict.get('meta', {}).get('validation_time'),
        'suite_name': result_dict.get('suite_name')
    }

    # Análisis detallado por expectativa
    expectation_details = []

    for result in results:
        expectation_config = result.get('expectation_config', {})
        expectation_result = result.get('result', {})
        meta = expectation_config.get('meta', {})

        # Información básica de la expectativa
        detail = {
            'expectation_id': meta.get('expectation_id', 'unknown'),
            'expectation_type': expectation_config.get('type', 'unknown'),
            'column': expectation_config.get('kwargs', {}).get('column'),
            'description': meta.get('description', 'No description'),
            'severity': expectation_config.get('severity', 'unknown'),
            'source': meta.get('source', 'unknown'),
            'success': result.get('success', False)
        }

        # Análisis específico según el resultado
        if result.get('success', False):
            detail['status'] = 'PASS'
            detail['failure_info'] = None
        else:
            detail['status'] = 'FAIL'

            # Información detallada de fallos
            failure_info = {
                'total_elements': expectation_result.get('element_count', 0),
                'invalid_count': expectation_result.get('unexpected_count', 0),
                'invalid_percentage': expectation_result.get('unexpected_percent', 0.0),
                'invalid_values': expectation_result.get('partial_unexpected_list', []),
                'invalid_indices': expectation_result.get('partial_unexpected_index_list', []),
                'value_counts': expectation_result.get('partial_unexpected_counts', [])
            }

            # Información adicional de valores faltantes si está disponible
            if 'missing_count' in expectation_result:
                failure_info['missing_count'] = expectation_result['missing_count']
                failure_info['missing_percentage'] = expectation_result.get('missing_percent', 0.0)

            detail['failure_info'] = failure_info

        # Información adicional específica del tipo de expectativa
        detail['expectation_kwargs'] = expectation_config.get('kwargs', {})

        expectation_details.append(detail)

    # Resumen por categorías de fallo
    failure_summary = {
        'failed_by_type': {},
        'failed_by_column': {},
        'critical_failures': [],
        'warning_failures': [],
        'info_failures': [],
        'most_common_failures': []
    }

    # Análisis de fallos por tipo y columna
    for detail in expectation_details:
        if detail['status'] == 'FAIL':
            exp_type = detail['expectation_type']
            column = detail['column']

            # Contar por tipo
            failure_summary['failed_by_type'][exp_type] = failure_summary['failed_by_type'].get(exp_type, 0) + 1

            # Contar por columna
            if column:
                failure_summary['failed_by_column'][column] = failure_summary['failed_by_column'].get(column, 0) + 1

            # Identificar fallos críticos
            if detail['severity'] == 'critical':
                failure_summary['critical_failures'].append({
                    'expectation_id': detail['expectation_id'],
                    'column': detail['column'],
                    'invalid_percentage': detail['failure_info']['invalid_percentage'] if detail['failure_info'] else 0
                })
            if detail['severity'] == 'warning':
                failure_summary['warning_failures'].append({
                    'expectation_id': detail['expectation_id'],
                    'column': detail['column'],
                    'invalid_percentage': detail['failure_info']['invalid_percentage'] if detail['failure_info'] else 0
                })
            if detail['severity'] == 'info':
                failure_summary['info_failures'].append({
                    'expectation_id': detail['expectation_id'],
                    'column': detail['column'],
                    'invalid_percentage': detail['failure_info']['invalid_percentage'] if detail['failure_info'] else 0
                })


    # Identificar los fallos más comunes (por porcentaje de valores inválidos)
    failed_expectations = [d for d in expectation_details if d['status'] == 'FAIL' and d['failure_info']]
    failure_summary['most_common_failures'] = sorted(
        failed_expectations,
        key=lambda x: x['failure_info']['invalid_percentage'],
        reverse=True
    )[:5]  # Top 5 fallos más comunes

    return {
        'executive_summary': executive_summary,
        'expectation_details': expectation_details,
        'failure_summary': failure_summary,
        'raw_statistics': statistics
    }

# Función para obtener solo las expectativas fallidas con detalles
def get_failed_expectations_summary(validation_result):
    """
    Retorna solo las expectativas que fallaron con información detallada
    """
    analysis = analyze_validation_results(validation_result)

    failed_expectations = [
        detail for detail in analysis['expectation_details']
        if detail['status'] == 'FAIL'
    ]

    return {
        'total_failures': len(failed_expectations),
        'failed_expectations': failed_expectations,
        'failure_summary': analysis['failure_summary']
    }
