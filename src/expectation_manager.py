"""
Expectation Manager Library
==========================

This library provides utilities for managing Great Expectations suites using Pydantic models.
It offers conversion between Pydantic models and GX ExpectationSuite objects, validation,
and serialization/deserialization capabilities.

Core Features:
1. Convert Pydantic expectation models to GX ExpectationSuite objects
2. Convert GX ExpectationSuite objects back to Pydantic models
3. Validate GX suites for correctness
4. Serialize/deserialize Pydantic suites to/from JSON and YAML
5. Comprehensive validation and error handling

Author: GitHub Copilot
Version: 1.0
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import great_expectations as gx
import yaml
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.expectations.expectation_configuration import \
    ExpectationConfiguration
from great_expectations.expectations.metadata_types import FailureSeverity
from pydantic import ValidationError

# Import the Pydantic models
from src.expectations import (  # Individual expectation models; ExpectColumnValuesToMatchStrftimeFormat,
    ExpectationWithMetadata, ExpectColumnMaxToBeBetween,
    ExpectColumnMeanToBeBetween, ExpectColumnMinToBeBetween,
    ExpectColumnSumToBeBetween, ExpectColumnToExist,
    ExpectColumnValuesToBeBetween, ExpectColumnValuesToBeInSet,
    ExpectColumnValuesToBeOfType, ExpectColumnValuesToBeUnique,
    ExpectColumnValuesToMatchRegex, ExpectColumnValuesToNotBeNull,
    ExpectCompoundColumnsToBeUnique, ExpectTableRowCountToBeBetween,
    GreatExpectation, GreatExpectationsSuite)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpectationManagerError(Exception):
    """Custom exception for expectation manager errors"""
    pass


class ExpectationManager:
    """
    Manager class for Great Expectations suites using Pydantic models
    """

    def __init__(self):
        """Initialize the expectation manager"""
        self.gx_context = None
        self._initialize_gx_context()

    def _initialize_gx_context(self):
        """Initialize Great Expectations data context"""
        try:
            # Try to get existing context first
            #try:
            self.gx_context = gx.get_context()
            logger.info("Using existing Great Expectations context")
            #except Exception:
            #    # Create a minimal ephemeral context if none exists
            #    logger.info("Creating ephemeral Great Expectations context")
            #    from great_expectations.data_context import \
            #        EphemeralDataContext
            #    self.gx_context = EphemeralDataContext()

        except Exception as e:
            raise ExpectationManagerError(
                f"Failed to initialize Great Expectations context: {e}"
            ) from e

    def ensure_gx_context(self):
        """Ensure GX context is available"""
        if not self.gx_context:
            self._initialize_gx_context()

    # =============================================================================
    # PYDANTIC TO GX CONVERSION
    # =============================================================================

    def pydantic_to_gx_suite(
        self,
        pydantic_suite: GreatExpectationsSuite,
        suite_name: Optional[str] = None
    ) -> ExpectationSuite:
        """
        Convert a Pydantic GreatExpectationsSuite to a GX ExpectationSuite

        Args:
            pydantic_suite: The Pydantic suite model
            suite_name: Optional name for the suite (defaults to generated name)

        Returns:
            GX ExpectationSuite object

        Raises:
            ExpectationManagerError: If conversion fails
        """
        self.ensure_gx_context()

        try:
            # Generate suite name if not provided
            if not suite_name:
                suite_name = f"suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Convert each expectation to GX format
            gx_expectations = []
            for exp_with_metadata in pydantic_suite.expectations:
                gx_config = self._pydantic_expectation_to_gx_config(exp_with_metadata)
                gx_expectations.append(gx_config)

            # Create the GX suite
            gx_suite = ExpectationSuite(
                name=suite_name,
                expectations=gx_expectations,
                meta={
                    "created_by": "ExpectationManager",
                    "created_at": datetime.now().isoformat(),
                    "total_expectations": len(gx_expectations)
                }
            )

            logger.info(f"Converted Pydantic suite to GX suite '{suite_name}' with {len(gx_expectations)} expectations")
            return gx_suite

        except Exception as e:
            raise ExpectationManagerError(f"Failed to convert Pydantic suite to GX: {e}") from e

    def _pydantic_expectation_to_gx_config(
        self,
        exp_with_metadata: ExpectationWithMetadata
    ) -> ExpectationConfiguration:
        """
        Convert a single Pydantic expectation to GX ExpectationConfiguration

        Args:
            exp_with_metadata: Pydantic expectation with metadata

        Returns:
            GX ExpectationConfiguration object
        """
        expectation = exp_with_metadata.expectation
        expectation_type = expectation.expectation_type

        # Extract kwargs from the Pydantic model
        kwargs = {}

        # Convert Pydantic model to dict and extract relevant fields
        exp_dict = expectation.model_dump()

        for key, value in exp_dict.items():
            if key != "expectation_type":
                # Handle special field name mappings
                if key == "type_":
                    kwargs["type_"] = value
                else:
                    kwargs[key] = value

        # Create meta information from the wrapper
        meta = {
            "expectation_id": exp_with_metadata.id,
            "description": exp_with_metadata.description,
            "source": exp_with_metadata.source,
        }

        if exp_with_metadata.severity == "warning":
            severity = FailureSeverity.WARNING
        elif exp_with_metadata.severity == "info":
            severity = FailureSeverity.INFO
        else:
            severity = FailureSeverity.CRITICAL

        # Create the GX expectation configuration
        config = ExpectationConfiguration(
            type=expectation_type,
            kwargs=kwargs,
            meta=meta,
            severity=severity
        )

        return config

    # =============================================================================
    # GX TO PYDANTIC CONVERSION
    # =============================================================================

    def gx_suite_to_pydantic(
        self,
        gx_suite: ExpectationSuite
    ) -> GreatExpectationsSuite:
        """
        Convert a GX ExpectationSuite to a Pydantic GreatExpectationsSuite

        Args:
            gx_suite: The GX ExpectationSuite object

        Returns:
            Pydantic GreatExpectationsSuite object

        Raises:
            ExpectationManagerError: If conversion fails
        """
        try:
            pydantic_expectations = []

            for i, gx_expectation in enumerate(gx_suite.expectations):
                pydantic_exp = self._gx_config_to_pydantic_expectation(gx_expectation, i)
                pydantic_expectations.append(pydantic_exp)

            # Create the Pydantic suite
            pydantic_suite = GreatExpectationsSuite(
                expectations=pydantic_expectations
            )

            logger.info(f"Converted GX suite '{gx_suite.name}' to Pydantic with {len(pydantic_expectations)} expectations")
            return pydantic_suite

        except Exception as e:
            raise ExpectationManagerError(f"Failed to convert GX suite to Pydantic: {e}") from e

    def _gx_config_to_pydantic_expectation(
        self,
        gx_config: ExpectationConfiguration,
        index: int
    ) -> ExpectationWithMetadata:
        """
        Convert a GX ExpectationConfiguration to Pydantic ExpectationWithMetadata

        Args:
            gx_config: GX ExpectationConfiguration object
            index: Index for generating ID if not in meta

        Returns:
            Pydantic ExpectationWithMetadata object
        """
        expectation_type = gx_config.expectation_type
        kwargs = gx_config.configuration.kwargs or {}
        meta = gx_config.configuration.meta or {}

        # Extract metadata
        exp_id = meta.get("expectation_id", f"exp_{index + 1}")
        description = meta.get("description", f"Expectation for {expectation_type}")
        source = meta.get("source", "GX Suite Import")

        # Create the appropriate Pydantic expectation model
        pydantic_expectation = self._create_pydantic_expectation(expectation_type, kwargs)

        # Wrap in metadata
        exp_with_metadata = ExpectationWithMetadata(
            id=exp_id,
            expectation=pydantic_expectation,
            description=description,
            source=source
        )

        return exp_with_metadata

    def _create_pydantic_expectation(
        self,
        expectation_type: str,
        kwargs: Dict[str, Any]
    ) -> GreatExpectation:
        """
        Create the appropriate Pydantic expectation model based on type

        Args:
            expectation_type: The GX expectation type
            kwargs: The expectation parameters

        Returns:
            Pydantic expectation model instance
        """
        # Mapping of GX expectation types to Pydantic models
        expectation_mapping = {
            "expect_column_to_exist": ExpectColumnToExist,
            "expect_column_values_to_not_be_null": ExpectColumnValuesToNotBeNull,
            "expect_column_values_to_be_unique": ExpectColumnValuesToBeUnique,
            "expect_compound_columns_to_be_unique": ExpectCompoundColumnsToBeUnique,
            "expect_column_values_to_be_in_set": ExpectColumnValuesToBeInSet,
            "expect_column_values_to_match_regex": ExpectColumnValuesToMatchRegex,
            "expect_column_values_to_be_between": ExpectColumnValuesToBeBetween,
            "expect_column_values_to_be_of_type": ExpectColumnValuesToBeOfType,
#            "expect_column_values_to_match_strftime_format": ExpectColumnValuesToMatchStrftimeFormat,
            "expect_column_mean_to_be_between": ExpectColumnMeanToBeBetween,
            "expect_table_row_count_to_be_between": ExpectTableRowCountToBeBetween,
            "expect_column_min_to_be_between": ExpectColumnMinToBeBetween,
            "expect_column_max_to_be_between": ExpectColumnMaxToBeBetween,
            "expect_column_sum_to_be_between": ExpectColumnSumToBeBetween,
        }

        pydantic_class = expectation_mapping.get(expectation_type)
        if not pydantic_class:
            raise ExpectationManagerError(f"Unsupported expectation type: {expectation_type}")

        # Create the model data
        model_data = {"expectation_type": expectation_type}
        model_data.update(kwargs)

        try:
            return pydantic_class(**model_data)
        except ValidationError as e:
            raise ExpectationManagerError(f"Failed to create Pydantic model for {expectation_type}: {e}") from e

    # =============================================================================
    # VALIDATION
    # =============================================================================

    def validate_gx_suite(self, gx_suite: ExpectationSuite) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a GX ExpectationSuite for correctness

        Args:
            gx_suite: The GX ExpectationSuite to validate

        Returns:
            Tuple of (is_valid, validation_report)
        """
        validation_report = {
            "suite_name": gx_suite.name,
            "total_expectations": len(gx_suite.expectations),
            "validation_errors": [],
            "validation_warnings": [],
            "expectation_details": [],
            "is_valid": True,
            "validated_at": datetime.now().isoformat()
        }

        try:
            # Basic suite validation
            if not gx_suite.name:
                validation_report["validation_warnings"].append("Suite has no name")

            if not gx_suite.expectations:
                validation_report["validation_errors"].append("Suite has no expectations")
                validation_report["is_valid"] = False

            # Validate individual expectations
            for i, expectation in enumerate(gx_suite.expectations):
                exp_validation = self._validate_single_expectation(expectation, i)
                validation_report["expectation_details"].append(exp_validation)

                if not exp_validation["is_valid"]:
                    validation_report["is_valid"] = False

        except Exception as e:
            validation_report["validation_errors"].append(f"Validation failed with error: {e}")
            validation_report["is_valid"] = False

        logger.info(f"Validated GX suite '{gx_suite.name}': {'PASS' if validation_report['is_valid'] else 'FAIL'}")
        return validation_report["is_valid"], validation_report

    def _validate_single_expectation(
        self,
        expectation: ExpectationConfiguration,
        index: int
    ) -> Dict[str, Any]:
        """
        Validate a single expectation configuration

        Args:
            expectation: GX ExpectationConfiguration to validate
            index: Index of the expectation in the suite

        Returns:
            Validation details dictionary
        """
        validation_details = {
            "index": index,
            "expectation_type": expectation.expectation_type,
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        try:
            # Check if expectation type is supported
            supported_types = [
                "expect_column_to_exist",
                "expect_column_values_to_not_be_null",
                "expect_column_values_to_be_unique",
                "expect_compound_columns_to_be_unique",
                "expect_column_values_to_be_in_set",
                "expect_column_values_to_match_regex",
                "expect_column_values_to_be_between",
                "expect_column_values_to_be_of_type",
                "expect_column_values_to_match_strftime_format",
                "expect_column_mean_to_be_between",
                "expect_table_row_count_to_be_between",
                "expect_column_min_to_be_between",
                "expect_column_max_to_be_between",
                "expect_column_sum_to_be_between"
            ]

            if expectation.expectation_type not in supported_types:
                validation_details["errors"].append(f"Unsupported expectation type: {expectation.expectation_type}")
                validation_details["is_valid"] = False

            # Basic kwargs validation
            #kwargs = expectation.configuration.kwargs or {}

            # Check for required column parameter (most expectations need this)
            #column_expectations = [t for t in supported_types if t != "expect_table_row_count_to_be_between"]
            #if expectation.expectation_type in column_expectations and "column" not in kwargs:
            #    validation_details["errors"].append("Missing required 'column' parameter")
            #    validation_details["is_valid"] = False

        except Exception as e:
            validation_details["errors"].append(f"Validation error: {e}")
            validation_details["is_valid"] = False

        return validation_details

    # =============================================================================
    # SERIALIZATION AND DESERIALIZATION
    # =============================================================================

    def serialize_to_json(
        self,
        pydantic_suite: GreatExpectationsSuite,
        output_path: Optional[str] = None
    ) -> str:
        """
        Serialize a Pydantic suite to JSON format

        Args:
            pydantic_suite: The Pydantic suite to serialize
            output_path: Optional path to save the JSON file

        Returns:
            JSON string representation
        """
        try:
            # Convert to JSON
            json_data = pydantic_suite.model_dump(exclude_none=True)
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

            # Save to file if path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(json_str)

                logger.info(f"Saved Pydantic suite to JSON: {output_path}")

            return json_str

        except Exception as e:
            raise ExpectationManagerError(f"Failed to serialize suite to JSON: {e}") from e

    def deserialize_from_json(
        self,
        json_input: Union[str, Path],
        is_file: bool = True
    ) -> GreatExpectationsSuite:
        """
        Deserialize a Pydantic suite from JSON format

        Args:
            json_input: JSON string or file path
            is_file: Whether json_input is a file path (True) or JSON string (False)

        Returns:
            Pydantic GreatExpectationsSuite object
        """
        try:
            if is_file:
                json_path = Path(json_input)
                if not json_path.exists():
                    raise FileNotFoundError(f"JSON file not found: {json_input}")

                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                logger.info(f"Loaded Pydantic suite from JSON: {json_input}")
            else:
                data = json.loads(json_input)

            # Create Pydantic suite from data
            return GreatExpectationsSuite(**data)

        except ValidationError as e:
            raise ExpectationManagerError(f"Failed to validate JSON data as Pydantic suite: {e}") from e
        except Exception as e:
            raise ExpectationManagerError(f"Failed to deserialize suite from JSON: {e}") from e

    def serialize_to_yaml(
        self,
        pydantic_suite: GreatExpectationsSuite,
        output_path: Optional[str] = None
    ) -> str:
        """
        Serialize a Pydantic suite to YAML format

        Args:
            pydantic_suite: The Pydantic suite to serialize
            output_path: Optional path to save the YAML file

        Returns:
            YAML string representation
        """
        try:
            # Convert to YAML
            yaml_data = pydantic_suite.model_dump(exclude_none=True)
            yaml_str = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(yaml_data)
            print(yaml_str)

            # Save to file if path provided
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_str)

                logger.info(f"Saved Pydantic suite to YAML: {output_path}")

            return yaml_str

        except Exception as e:
            raise ExpectationManagerError(f"Failed to serialize suite to YAML: {e}") from e

    def deserialize_from_yaml(
        self,
        yaml_input: Union[str, Path],
        is_file: bool = True
    ) -> GreatExpectationsSuite:
        """
        Deserialize a Pydantic suite from YAML format

        Args:
            yaml_input: YAML string or file path
            is_file: Whether yaml_input is a file path (True) or YAML string (False)

        Returns:
            Pydantic GreatExpectationsSuite object
        """
        try:
            if is_file:
                yaml_path = Path(yaml_input)
                if not yaml_path.exists():
                    raise FileNotFoundError(f"YAML file not found: {yaml_input}")

                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                logger.info(f"Loaded Pydantic suite from YAML: {yaml_input}")
            else:
                data = yaml.safe_load(yaml_input)

            # Create Pydantic suite from data
            print(data)
            return GreatExpectationsSuite(**data)

        except ValidationError as e:
            raise ExpectationManagerError(f"Failed to validate YAML data as Pydantic suite: {e}") from e
        except Exception as e:
            raise ExpectationManagerError(f"Failed to deserialize suite from YAML: {e}") from e

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def get_suite_summary(self, pydantic_suite: GreatExpectationsSuite) -> Dict[str, Any]:
        """
        Get a summary of a Pydantic suite

        Args:
            pydantic_suite: The Pydantic suite to summarize

        Returns:
            Summary dictionary
        """
        expectation_types = {}

        for exp_with_metadata in pydantic_suite.expectations:
            exp_type = exp_with_metadata.expectation.expectation_type
            expectation_types[exp_type] = expectation_types.get(exp_type, 0) + 1

        return {
            "total_expectations": len(pydantic_suite.expectations),
            "expectation_types": expectation_types,
            "expectation_ids": [exp.id for exp in pydantic_suite.expectations],
            "sources": list(set([exp.source for exp in pydantic_suite.expectations]))
        }

    def validate_pydantic_suite(self, pydantic_suite: GreatExpectationsSuite) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a Pydantic suite by converting to GX and validating

        Args:
            pydantic_suite: The Pydantic suite to validate

        Returns:
            Tuple of (is_valid, validation_report)
        """
        try:
            # Convert to GX suite
            gx_suite = self.pydantic_to_gx_suite(pydantic_suite)

            print("Validando suite")


            # Validate the GX suite
            is_valid, validation_report = self.validate_gx_suite(gx_suite)

            # Add Pydantic-specific information
            validation_report["source"] = "Pydantic Suite Validation"
            validation_report["pydantic_summary"] = self.get_suite_summary(pydantic_suite)

            return is_valid, validation_report

        except Exception as e:
            return False, {
                "is_valid": False,
                "error": str(e),
                "source": "Pydantic Suite Validation",
                "validated_at": datetime.now().isoformat()
            }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_manager() -> ExpectationManager:
    """
    Convenience function to create an ExpectationManager instance

    Returns:
        ExpectationManager instance
    """
    return ExpectationManager()


def pydantic_to_gx(
    pydantic_suite: GreatExpectationsSuite,
    suite_name: Optional[str] = None
) -> ExpectationSuite:
    """
    Convenience function to convert Pydantic suite to GX suite

    Args:
        pydantic_suite: The Pydantic suite to convert
        suite_name: Optional name for the suite

    Returns:
        GX ExpectationSuite object
    """
    manager = create_manager()
    return manager.pydantic_to_gx_suite(pydantic_suite, suite_name)


def gx_to_pydantic(gx_suite: ExpectationSuite) -> GreatExpectationsSuite:
    """
    Convenience function to convert GX suite to Pydantic suite

    Args:
        gx_suite: The GX suite to convert

    Returns:
        Pydantic GreatExpectationsSuite object
    """
    manager = create_manager()
    return manager.gx_suite_to_pydantic(gx_suite)


def save_suite_json(
    pydantic_suite: GreatExpectationsSuite,
    output_path: str
) -> str:
    """
    Convenience function to save Pydantic suite to JSON

    Args:
        pydantic_suite: The suite to save
        output_path: Path to save the JSON file

    Returns:
        JSON string representation
    """
    manager = create_manager()
    return manager.serialize_to_json(pydantic_suite, output_path)


def load_suite_json(json_path: str) -> GreatExpectationsSuite:
    """
    Convenience function to load Pydantic suite from JSON

    Args:
        json_path: Path to the JSON file

    Returns:
        Pydantic GreatExpectationsSuite object
    """
    manager = create_manager()
    return manager.deserialize_from_json(json_path, is_file=True)


def save_suite_yaml(
    pydantic_suite: GreatExpectationsSuite,
    output_path: Optional[str] = None
) -> str:
    """
    Convenience function to save Pydantic suite to YAML

    Args:
        pydantic_suite: The suite to save
        output_path: Path to save the YAML file

    Returns:
        YAML string representation
    """
    manager = create_manager()
    return manager.serialize_to_yaml(pydantic_suite, output_path)


def load_suite_yaml(yaml_path: str, is_file: bool = True) -> GreatExpectationsSuite:
    """
    Convenience function to load Pydantic suite from YAML

    Args:
        yaml_path: Path to the YAML file

    Returns:
        Pydantic GreatExpectationsSuite object
    """
    manager = create_manager()
    return manager.deserialize_from_yaml(yaml_path, is_file=is_file)
