"""
Constants and configuration for the MLM Commission Engine.
"""

class Constants:
    """Application constants."""
    
    COMMISSION_RATE = 0.05  # 5% commission rate
    DEFAULT_ENCODING = 'utf-8'
    JSON_INDENT = 2
    
    # Performance thresholds
    MEMORY_THRESHOLD_KB_PER_PARTNER = 2.0
    TARGET_PERFORMANCE_SECONDS = 2.0
    
    # Benchmark configuration
    DEFAULT_BENCHMARK_MAX_DEPTH = 10
    BENCHMARK_SEED = 42  # For reproducible results


class ErrorMessages:
    """Centralized error messages."""
    
    PARENT_NOT_FOUND = "Parent {parent_id} not found for partner {partner_id}"
    CYCLE_DETECTED = "Cycle detected involving partner {partner_id}"
    NO_ROOT_PARTNERS = "No root partners found"
    NO_PARTNERS_LOADED = "No partners loaded. Call load_partners() first."
    INVALID_DATE = "Invalid date: {date}"
    INVALID_INPUT_TYPE = "Expected {expected_type}, got {actual_type}"
    FILE_NOT_FOUND = "File not found: {filepath}"
    INVALID_JSON = "Invalid JSON format in file: {filepath}"
    """Centralized error messages."""
    
    PARENT_NOT_FOUND = "Parent {parent_id} not found for partner {partner_id}"
    CYCLE_DETECTED = "Cycle detected involving partner {partner_id}"
    NO_ROOT_PARTNERS = "No root partners found"
    INVALID_DATE = "Invalid date: {date}"
    INVALID_INPUT_TYPE = "Expected {expected_type}, got {actual_type}"
    FILE_NOT_FOUND = "File not found: {filepath}"
    INVALID_JSON = "Invalid JSON format in file: {filepath}"
