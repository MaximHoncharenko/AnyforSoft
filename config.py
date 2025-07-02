"""
Constants and configuration for the MLM Commission Engine.

This module centralizes all configuration constants and error messages
to follow the DRY principle and make maintenance easier.
"""

from typing import Final


class Constants:
    """Application constants following immutable configuration pattern."""
    
    # Business logic constants
    COMMISSION_RATE: Final[float] = 0.05  # 5% commission rate
    
    # File I/O constants
    DEFAULT_ENCODING: Final[str] = 'utf-8'
    JSON_INDENT: Final[int] = 2
    
    # Performance thresholds
    MEMORY_THRESHOLD_KB_PER_PARTNER: Final[float] = 2.0
    TARGET_PERFORMANCE_SECONDS: Final[float] = 2.0
    
    # Benchmark configuration
    DEFAULT_BENCHMARK_MAX_DEPTH: Final[int] = 10
    BENCHMARK_SEED: Final[int] = 42  # For reproducible results


class ErrorMessages:
    """Centralized error messages following message catalog pattern."""
    
    # Structural errors
    PARENT_NOT_FOUND: Final[str] = "Parent {parent_id} not found for partner {partner_id}"
    CYCLE_DETECTED: Final[str] = "Cycle detected involving partner {partner_id}"
    NO_ROOT_PARTNERS: Final[str] = "No root partners found"
    
    # State errors  
    NO_PARTNERS_LOADED: Final[str] = "No partners loaded. Call load_partners() first."
    
    # Input validation errors
    INVALID_DATE: Final[str] = "Invalid date: {date}"
    INVALID_INPUT_TYPE: Final[str] = "Expected {expected_type}, got {actual_type}"
    
    # File I/O errors
    FILE_NOT_FOUND: Final[str] = "File not found: {filepath}"
    INVALID_JSON: Final[str] = "Invalid JSON format in file: {filepath}"
