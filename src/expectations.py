import json
from enum import Enum
from typing import List, Literal, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_serializer, model_validator

# =============================================================================
# MODELOS INDIVIDUALES PARA CADA TIPO DE EXPECTATION
# =============================================================================

# Data Completeness Expectations
class ExpectColumnToExist(BaseModel):
    """Validates that a specific column exists in the dataset"""
    expectation_type: Literal["expect_column_to_exist"] = "expect_column_to_exist"
    column: str = Field(..., description="Name of the column that must exist")

class ExpectColumnValuesToNotBeNull(BaseModel):
    """Validates that column values are not null"""
    expectation_type: Literal["expect_column_values_to_not_be_null"] = "expect_column_values_to_not_be_null"
    column: str = Field(..., description="Name of the column to check for null values")
    mostly: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Minimum fraction of non-null values (0.0 to 1.0)")

# Data Uniqueness Expectations
class ExpectColumnValuesToBeUnique(BaseModel):
    """Validates that all values in a column are unique"""
    expectation_type: Literal["expect_column_values_to_be_unique"] = "expect_column_values_to_be_unique"
    column: str = Field(..., description="Name of the column that should have unique values")
    mostly: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Minimum fraction of unique values")

class ExpectCompoundColumnsToBeUnique(BaseModel):
    """Validates that combinations of multiple columns are unique"""
    expectation_type: Literal["expect_compound_columns_to_be_unique"] = "expect_compound_columns_to_be_unique"
    column_list: List[str] = Field(..., description="List of column names that together should form unique combinations")

# Data Validity Expectations
class ExpectColumnValuesToBeInSet(BaseModel):
    """Validates that column values are within a predefined set"""
    expectation_type: Literal["expect_column_values_to_be_in_set"] = "expect_column_values_to_be_in_set"
    column: str = Field(..., description="Name of the column to validate against the value set")
    value_set: List[Union[str, int, float]] = Field(..., description="List of valid values")
    mostly: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Minimum fraction of values that must be in the set")

class ExpectColumnValuesToMatchRegex(BaseModel):
    """Validates that column values match a regular expression pattern"""
    expectation_type: Literal["expect_column_values_to_match_regex"] = "expect_column_values_to_match_regex"
    column: str = Field(..., description="Name of the column to validate with regex")
    regex: str = Field(..., description="Regular expression pattern")
    mostly: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Minimum fraction of values that must match the regex")

class ExpectColumnValuesToBeBetween(BaseModel):
    """Validates that numeric column values fall within a specified range"""
    expectation_type: Literal["expect_column_values_to_be_between"] = "expect_column_values_to_be_between"
    column: str = Field(..., description="Name of the numeric column to validate")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum allowed value (inclusive)")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum allowed value (inclusive)")
    mostly: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Minimum fraction of values that must be within range")

    @model_validator(mode='after')
    def at_least_one_bound(self):
        if self.min_value is None and self.max_value is None:
            raise ValueError('At least one of min_value or max_value must be specified')
        return self

class ExpectColumnValuesToBeOfType(BaseModel):
    """Validates that column values are of the expected data type"""
    expectation_type: Literal["expect_column_values_to_be_of_type"] = "expect_column_values_to_be_of_type"
    column: str = Field(..., description="Name of the column to validate type")
    type_: str = Field(..., description="Expected data type. Examples: 'int', 'float', 'str', 'bool', 'datetime'")

#class ExpectColumnValuesToMatchStrftimeFormat(BaseModel):
#    """Validates that string values match a datetime format"""
#    expectation_type: Literal["expect_column_values_to_match_strftime_format"] = "expect_column_values_to_match_strftime_format"
#    column: str = Field(..., description="Name of the column containing datetime strings")
#    strftime_format: str = Field(..., description="Expected datetime format string")
#    mostly: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Minimum fraction of values that must match the format")

# Statistical Consistency Expectations
class ExpectColumnMeanToBeBetween(BaseModel):
    """Validates that the mean of a numeric column falls within expected bounds"""
    expectation_type: Literal["expect_column_mean_to_be_between"] = "expect_column_mean_to_be_between"
    column: str = Field(..., description="Name of the numeric column to calculate mean")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum expected mean value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum expected mean value")

    @model_validator(mode='after')
    def at_least_one_bound(self):
        if self.min_value is None and self.max_value is None:
            raise ValueError('At least one of min_value or max_value must be specified')
        return self

class ExpectTableRowCountToBeBetween(BaseModel):
    """Validates that the total number of rows falls within expected bounds"""
    expectation_type: Literal["expect_table_row_count_to_be_between"] = "expect_table_row_count_to_be_between"
    min_value: Optional[int] = Field(None, description="Minimum expected number of rows")
    max_value: Optional[int] = Field(None, description="Maximum expected number of rows")

    @model_validator(mode='after')
    def at_least_one_bound(self):
        if self.min_value is None and self.max_value is None:
            raise ValueError('At least one of min_value or max_value must be specified')
        return self

# Additional Numeric Validation Expectations
class ExpectColumnMinToBeBetween(BaseModel):
    """Validates that the minimum value in a column falls within expected bounds"""
    expectation_type: Literal["expect_column_min_to_be_between"] = "expect_column_min_to_be_between"
    column: str = Field(..., description="Name of the numeric column")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum expected minimum value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum expected minimum value")

    @model_validator(mode='after')
    def at_least_one_bound(self):
        if self.min_value is None and self.max_value is None:
            raise ValueError('At least one of min_value or max_value must be specified')
        return self

class ExpectColumnMaxToBeBetween(BaseModel):
    """Validates that the maximum value in a column falls within expected bounds"""
    expectation_type: Literal["expect_column_max_to_be_between"] = "expect_column_max_to_be_between"
    column: str = Field(..., description="Name of the numeric column")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum expected maximum value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum expected maximum value")

    @model_validator(mode='after')
    def at_least_one_bound(self):
        if self.min_value is None and self.max_value is None:
            raise ValueError('At least one of min_value or max_value must be specified')
        return self

class ExpectColumnSumToBeBetween(BaseModel):
    """Validates that the sum of values in a column falls within expected bounds"""
    expectation_type: Literal["expect_column_sum_to_be_between"] = "expect_column_sum_to_be_between"
    column: str = Field(..., description="Name of the numeric column to sum")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum expected sum")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum expected sum")

    @model_validator(mode='after')
    def at_least_one_bound(self):
        if self.min_value is None and self.max_value is None:
            raise ValueError('At least one of min_value or max_value must be specified')
        return self

# =============================================================================
# UNION TYPE PARA TODAS LAS EXPECTATIVAS
# =============================================================================

# Union type que puede representar cualquier expectativa permitida
GreatExpectation = Union[
    ExpectColumnToExist,
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeUnique,
    ExpectColumnValuesToBeInSet,
    ExpectColumnValuesToMatchRegex,
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToBeOfType,
#    ExpectColumnValuesToMatchStrftimeFormat,
    ExpectColumnMeanToBeBetween,
    ExpectTableRowCountToBeBetween,
    ExpectColumnMinToBeBetween,
    ExpectColumnMaxToBeBetween,
    ExpectColumnSumToBeBetween
]

# =============================================================================
# MODELO WRAPPER CON METADATOS PARA EXPECTATIVAS
# =============================================================================

class ExpectationWithMetadata(BaseModel):
    """
    Wrapper que combina una expectativa con sus metadatos asociados
    """
    id: str = Field(..., description="Unique identifier for the expectation")
    expectation: GreatExpectation = Field(..., description="The actual Great Expectations rule")
    description: str = Field(..., description="Detailed description of the expectation and its purpose")
    source: str = Field(..., description="Source of the expectation (e.g., 'Documentation', 'Data Profiling'). Provide context.")
    severity: Literal["critical", "warning", "info"] = Field("critical", description="Severity level of the expectation failure (critical, warning, info)")

# =============================================================================
# MODELO CONTENEDOR PARA LISTA DE EXPECTATIVAS CON METADATOS
# =============================================================================

class GreatExpectationsSuite(BaseModel):
    """
    Container for a list of Great Expectations rules with metadata
    """
    expectations: List[ExpectationWithMetadata] = Field(..., description="List of expectation rules with metadata")


def convert_model_to_str(expectation_model):
    return yaml.dump(expectation_model.model_json_schema(), indent=2)
