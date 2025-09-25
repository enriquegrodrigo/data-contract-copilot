"""
Test script for the ExpectationManager library
==============================================

This script demonstrates the key functionality of the ExpectationManager library:
1. Creating Pydantic expectation suites
2. Converting between Pydantic and GX formats
3. Validating suites
4. Serializing/deserializing to JSON and YAML

Run this script to verify that the ExpectationManager is working correctly.
"""

import sys
from pathlib import Path

# Add the src directory to the path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from expectation_manager import (ExpectationManager, create_manager,
                                 load_suite_json, pydantic_to_gx,
                                 save_suite_json)
from expectations import (ExpectationWithMetadata, ExpectColumnToExist,
                          ExpectColumnValuesToBeBetween,
                          ExpectColumnValuesToNotBeNull,
                          ExpectTableRowCountToBeBetween,
                          GreatExpectationsSuite)


def create_sample_pydantic_suite() -> GreatExpectationsSuite:
    """Create a sample Pydantic suite for testing"""

    # Create individual expectations with metadata
    expectations = [
        ExpectationWithMetadata(
            id="exp_001",
            expectation=ExpectColumnToExist(column="customer_id"),
            description="Customer ID column must exist in the dataset",
            source="Documentation"
        ),
        ExpectationWithMetadata(
            id="exp_002",
            expectation=ExpectColumnValuesToNotBeNull(column="customer_id", mostly=1.0),
            description="Customer ID cannot be null",
            source="Data Profiling"
        ),
        ExpectationWithMetadata(
            id="exp_003",
            expectation=ExpectColumnValuesToBeBetween(column="order_total", min_value=0.0, max_value=10000.0),
            description="Order total must be between 0 and 10,000",
            source="Business Rules"
        ),
        ExpectationWithMetadata(
            id="exp_004",
            expectation=ExpectTableRowCountToBeBetween(min_value=100, max_value=1000000),
            description="Dataset should have reasonable number of rows",
            source="Data Validation"
        )
    ]

    return GreatExpectationsSuite(expectations=expectations)


def test_expectation_manager():
    """Test the main functionality of ExpectationManager"""

    print("🧪 Testing ExpectationManager Library")
    print("=" * 50)

    # 1. Create manager
    print("\n1️⃣  Creating ExpectationManager...")
    manager = create_manager()
    print("✅ ExpectationManager created successfully")

    # 2. Create sample Pydantic suite
    print("\n2️⃣  Creating sample Pydantic suite...")
    pydantic_suite = create_sample_pydantic_suite()
    print(f"✅ Created suite with {len(pydantic_suite.expectations)} expectations")

    # 3. Get suite summary
    print("\n3️⃣  Getting suite summary...")
    summary = manager.get_suite_summary(pydantic_suite)
    print("✅ Suite Summary:")
    for key, value in summary.items():
        print(f"   - {key}: {value}")

    # 4. Validate Pydantic suite
    print("\n4️⃣  Validating Pydantic suite...")
    is_valid, validation_report = manager.validate_pydantic_suite(pydantic_suite)
    print(f"✅ Suite validation: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print("❌ Validation errors found:")
        for error in validation_report.get('validation_errors', []):
            print(f"   - {error}")

    # 5. Convert to GX suite
    print("\n5️⃣  Converting Pydantic suite to GX...")
    gx_suite = manager.pydantic_to_gx_suite(pydantic_suite, "test_suite")
    print(f"✅ Converted to GX suite with {len(gx_suite.expectations)} expectations")

    # 6. Validate GX suite
    print("\n6️⃣  Validating GX suite...")
    is_gx_valid, gx_validation_report = manager.validate_gx_suite(gx_suite)
    print(f"✅ GX suite validation: {'PASS' if is_gx_valid else 'FAIL'}")

    # 7. Convert GX back to Pydantic
    print("\n7️⃣  Converting GX suite back to Pydantic...")
    pydantic_suite_2 = manager.gx_suite_to_pydantic(gx_suite)
    print(f"✅ Converted back to Pydantic with {len(pydantic_suite_2.expectations)} expectations")

    # 8. Test JSON serialization
    print("\n8️⃣  Testing JSON serialization...")
    json_str = manager.serialize_to_json(pydantic_suite)
    print(f"✅ Serialized to JSON ({len(json_str)} characters)")

    # 9. Test JSON deserialization
    print("\n9️⃣  Testing JSON deserialization...")
    pydantic_suite_from_json = manager.deserialize_from_json(json_str, is_file=False)
    print(f"✅ Deserialized from JSON with {len(pydantic_suite_from_json.expectations)} expectations")

    # 10. Test YAML serialization
    print("\n🔟 Testing YAML serialization...")
    yaml_str = manager.serialize_to_yaml(pydantic_suite)
    print(f"✅ Serialized to YAML ({len(yaml_str)} characters)")

    # 11. Test YAML deserialization
    print("\n1️⃣1️⃣  Testing YAML deserialization...")
    pydantic_suite_from_yaml = manager.deserialize_from_yaml(yaml_str, is_file=False)
    print(f"✅ Deserialized from YAML with {len(pydantic_suite_from_yaml.expectations)} expectations")

    # 12. Test file save/load
    print("\n1️⃣2️⃣  Testing file save/load...")
    test_json_path = "/tmp/test_suite.json"
    manager.serialize_to_json(pydantic_suite, test_json_path)
    loaded_suite = manager.deserialize_from_json(test_json_path, is_file=True)
    print(f"✅ Saved and loaded from file with {len(loaded_suite.expectations)} expectations")

    print("\n🎉 All tests completed successfully!")
    print("=" * 50)

    return {
        "original_suite": pydantic_suite,
        "gx_suite": gx_suite,
        "roundtrip_suite": pydantic_suite_2,
        "json_suite": pydantic_suite_from_json,
        "yaml_suite": pydantic_suite_from_yaml,
        "file_suite": loaded_suite
    }


if __name__ == "__main__":
    try:
        results = test_expectation_manager()
        print("\n🏆 ExpectationManager library is working correctly!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
