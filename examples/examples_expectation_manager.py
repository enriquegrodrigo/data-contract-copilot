"""
ExpectationManager Library Usage Examples
=========================================

This script demonstrates comprehensive usage of the ExpectationManager library
with real-world examples and different use cases.
"""

import sys
from pathlib import Path

# Add the src directory to the path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from expectation_manager import (ExpectationManager, create_manager,
                                 gx_to_pydantic, load_suite_json,
                                 load_suite_yaml, pydantic_to_gx,
                                 save_suite_json, save_suite_yaml)
from expectations import (ExpectationWithMetadata, ExpectColumnToExist,
                          ExpectColumnValuesToBeBetween,
                          ExpectColumnValuesToBeInSet,
                          ExpectColumnValuesToBeUnique,
                          ExpectColumnValuesToMatchRegex,
                          ExpectColumnValuesToNotBeNull,
                          ExpectTableRowCountToBeBetween,
                          GreatExpectationsSuite)


def example_1_basic_usage():
    """Example 1: Basic usage - Create, convert, validate"""
    print("📊 Example 1: Basic Usage")
    print("-" * 40)

    # Create a simple expectation suite
    expectations = [
        ExpectationWithMetadata(
            id="customer_id_exists",
            expectation=ExpectColumnToExist(column="customer_id"),
            description="Customer ID column must be present",
            source="Data Schema Requirements"
        ),
        ExpectationWithMetadata(
            id="customer_id_not_null",
            expectation=ExpectColumnValuesToNotBeNull(column="customer_id", mostly=1.0),
            description="All customer IDs must be non-null",
            source="Data Quality Rules"
        )
    ]

    pydantic_suite = GreatExpectationsSuite(expectations=expectations)

    # Use the library
    manager = create_manager()

    # Convert to GX and validate
    gx_suite = manager.pydantic_to_gx_suite(pydantic_suite, "customer_validation")
    is_valid, report = manager.validate_gx_suite(gx_suite)

    print(f"✅ Created suite with {len(pydantic_suite.expectations)} expectations")
    print(f"✅ Converted to GX suite: {gx_suite.name}")
    print(f"✅ Validation result: {'PASS' if is_valid else 'FAIL'}")

    return pydantic_suite, gx_suite


def example_2_comprehensive_data_validation():
    """Example 2: Comprehensive data validation suite"""
    print("\n📋 Example 2: Comprehensive Data Validation")
    print("-" * 50)

    # Create a comprehensive suite for an e-commerce orders dataset
    expectations = [
        # Data existence checks
        ExpectationWithMetadata(
            id="order_id_exists",
            expectation=ExpectColumnToExist(column="order_id"),
            description="Order ID column must exist",
            source="Database Schema"
        ),
        ExpectationWithMetadata(
            id="customer_id_exists",
            expectation=ExpectColumnToExist(column="customer_id"),
            description="Customer ID column must exist",
            source="Database Schema"
        ),
        ExpectationWithMetadata(
            id="order_date_exists",
            expectation=ExpectColumnToExist(column="order_date"),
            description="Order date column must exist",
            source="Database Schema"
        ),

        # Data completeness checks
        ExpectationWithMetadata(
            id="order_id_not_null",
            expectation=ExpectColumnValuesToNotBeNull(column="order_id", mostly=1.0),
            description="Order ID cannot be null",
            source="Primary Key Constraint"
        ),
        ExpectationWithMetadata(
            id="customer_id_not_null",
            expectation=ExpectColumnValuesToNotBeNull(column="customer_id", mostly=0.99),
            description="Customer ID should rarely be null (99% non-null)",
            source="Business Rules"
        ),

        # Data uniqueness checks
        ExpectationWithMetadata(
            id="order_id_unique",
            expectation=ExpectColumnValuesToBeUnique(column="order_id", mostly=1.0),
            description="Each order should have a unique ID",
            source="Primary Key Constraint"
        ),

        # Data validity checks
        ExpectationWithMetadata(
            id="order_total_range",
            expectation=ExpectColumnValuesToBeBetween(
                column="order_total",
                min_value=0.01,
                max_value=50000.0,
                mostly=0.98
            ),
            description="Order total should be between $0.01 and $50,000 for 98% of orders",
            source="Business Logic"
        ),
        ExpectationWithMetadata(
            id="order_status_valid",
            expectation=ExpectColumnValuesToBeInSet(
                column="order_status",
                value_set=["pending", "confirmed", "shipped", "delivered", "cancelled"],
                mostly=1.0
            ),
            description="Order status must be one of the predefined values",
            source="Enumeration Constraint"
        ),
        ExpectationWithMetadata(
            id="email_format",
            expectation=ExpectColumnValuesToMatchRegex(
                column="customer_email",
                regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                mostly=0.95
            ),
            description="Customer email should follow standard email format",
            source="Data Validation Rules"
        ),

        # Statistical checks
        ExpectationWithMetadata(
            id="reasonable_row_count",
            expectation=ExpectTableRowCountToBeBetween(min_value=1000, max_value=10000000),
            description="Dataset should contain reasonable number of orders",
            source="Data Volume Expectations"
        )
    ]

    suite = GreatExpectationsSuite(expectations=expectations)

    # Get detailed summary
    manager = create_manager()
    summary = manager.get_suite_summary(suite)

    print(f"✅ Created comprehensive suite:")
    print(f"   - Total expectations: {summary['total_expectations']}")
    print(f"   - Expectation types: {len(summary['expectation_types'])}")
    print(f"   - Data sources: {summary['sources']}")

    for exp_type, count in summary['expectation_types'].items():
        print(f"     • {exp_type}: {count}")

    return suite


def example_3_serialization_formats():
    """Example 3: Different serialization formats"""
    print("\n💾 Example 3: Serialization & Deserialization")
    print("-" * 45)

    # Create a simple suite
    suite = GreatExpectationsSuite(expectations=[
        ExpectationWithMetadata(
            id="product_id_check",
            expectation=ExpectColumnToExist(column="product_id"),
            description="Product ID must exist",
            source="Schema Validation"
        )
    ])

    manager = create_manager()

    # Test JSON serialization
    json_output = "./output/example_suite.json"
    Path(json_output).parent.mkdir(exist_ok=True)

    json_str = manager.serialize_to_json(suite, json_output)
    loaded_from_json = manager.deserialize_from_json(json_output, is_file=True)

    print(f"✅ JSON serialization:")
    print(f"   - Saved to: {json_output}")
    print(f"   - JSON length: {len(json_str)} characters")
    print(f"   - Loaded expectations: {len(loaded_from_json.expectations)}")

    # Test YAML serialization
    yaml_output = "./output/example_suite.yaml"
    yaml_str = manager.serialize_to_yaml(suite, yaml_output)
    loaded_from_yaml = manager.deserialize_from_yaml(yaml_output, is_file=True)

    print(f"✅ YAML serialization:")
    print(f"   - Saved to: {yaml_output}")
    print(f"   - YAML length: {len(yaml_str)} characters")
    print(f"   - Loaded expectations: {len(loaded_from_yaml.expectations)}")

    return json_output, yaml_output


def example_4_roundtrip_conversion():
    """Example 4: Roundtrip conversion between Pydantic and GX"""
    print("\n🔄 Example 4: Roundtrip Conversion")
    print("-" * 35)

    # Create original Pydantic suite
    original_suite = GreatExpectationsSuite(expectations=[
        ExpectationWithMetadata(
            id="inventory_check",
            expectation=ExpectColumnValuesToBeBetween(
                column="inventory_count",
                min_value=0,
                max_value=10000,
                mostly=0.99
            ),
            description="Inventory count should be reasonable",
            source="Inventory Management"
        ),
        ExpectationWithMetadata(
            id="category_valid",
            expectation=ExpectColumnValuesToBeInSet(
                column="product_category",
                value_set=["electronics", "clothing", "books", "home", "sports"],
                mostly=1.0
            ),
            description="Product category must be predefined",
            source="Catalog Standards"
        )
    ])

    manager = create_manager()

    print("Original Pydantic suite:")
    print(f"  - Expectations: {len(original_suite.expectations)}")

    # Convert Pydantic -> GX
    gx_suite = manager.pydantic_to_gx_suite(original_suite, "roundtrip_test")
    print(f"  - Converted to GX suite: {gx_suite.name}")
    print(f"  - GX expectations: {len(gx_suite.expectations)}")

    # Convert GX -> Pydantic
    converted_back = manager.gx_suite_to_pydantic(gx_suite)
    print(f"  - Converted back to Pydantic: {len(converted_back.expectations)} expectations")

    # Validate both are equivalent
    original_summary = manager.get_suite_summary(original_suite)
    converted_summary = manager.get_suite_summary(converted_back)

    print("\n✅ Roundtrip validation:")
    print(f"  - Original expectation types: {original_summary['expectation_types']}")
    print(f"  - Converted expectation types: {converted_summary['expectation_types']}")
    print(f"  - Types match: {original_summary['expectation_types'] == converted_summary['expectation_types']}")

    return original_suite, gx_suite, converted_back


def example_5_convenience_functions():
    """Example 5: Using convenience functions"""
    print("\n🚀 Example 5: Convenience Functions")
    print("-" * 35)

    # Create suite using convenience approach
    suite = GreatExpectationsSuite(expectations=[
        ExpectationWithMetadata(
            id="quick_test",
            expectation=ExpectColumnToExist(column="test_column"),
            description="Quick validation test",
            source="Demo"
        )
    ])

    # Use convenience functions
    print("Using convenience functions:")

    # Direct conversion
    gx_suite = pydantic_to_gx(suite, "convenience_suite")
    print(f"  ✅ pydantic_to_gx: Created '{gx_suite.name}'")

    # Convert back
    pydantic_suite = gx_to_pydantic(gx_suite)
    print(f"  ✅ gx_to_pydantic: {len(pydantic_suite.expectations)} expectations")

    # Save/load JSON
    json_path = "./output/convenience_suite.json"
    Path(json_path).parent.mkdir(exist_ok=True)

    save_suite_json(suite, json_path)
    loaded_suite = load_suite_json(json_path)
    print(f"  ✅ JSON save/load: {len(loaded_suite.expectations)} expectations")

    # Save/load YAML
    yaml_path = "./output/convenience_suite.yaml"
    save_suite_yaml(suite, yaml_path)
    loaded_yaml_suite = load_suite_yaml(yaml_path)
    print(f"  ✅ YAML save/load: {len(loaded_yaml_suite.expectations)} expectations")

    return suite


def main():
    """Run all examples"""
    print("🎯 ExpectationManager Library - Comprehensive Examples")
    print("=" * 60)

    try:
        # Run examples
        pydantic_suite_1, gx_suite_1 = example_1_basic_usage()
        comprehensive_suite = example_2_comprehensive_data_validation()
        json_file, yaml_file = example_3_serialization_formats()
        orig_suite, gx_suite, converted_suite = example_4_roundtrip_conversion()
        convenience_suite = example_5_convenience_functions()

        print("\n🎉 All examples completed successfully!")
        print("\n📁 Generated files:")
        print(f"  - {json_file}")
        print(f"  - {yaml_file}")
        print(f"  - ./output/convenience_suite.json")
        print(f"  - ./output/convenience_suite.yaml")

        print("\n💡 Key Features Demonstrated:")
        print("  ✅ Pydantic model creation and validation")
        print("  ✅ Conversion between Pydantic and GX formats")
        print("  ✅ Suite validation and error reporting")
        print("  ✅ JSON and YAML serialization/deserialization")
        print("  ✅ File-based save/load operations")
        print("  ✅ Roundtrip conversion integrity")
        print("  ✅ Convenience functions for common operations")

        return True

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
