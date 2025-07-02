"""
Utility functions for file operations and common tasks.
"""

import json
import tempfile
import os
from typing import Any, Dict, List
from pathlib import Path

from config import Constants, ErrorMessages


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def read_json(filepath: str) -> Any:
        """
        Read JSON data from file with proper error handling.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        try:
            with open(filepath, 'r', encoding=Constants.DEFAULT_ENCODING) as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(ErrorMessages.FILE_NOT_FOUND.format(filepath=filepath))
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                ErrorMessages.INVALID_JSON.format(filepath=filepath),
                e.doc, e.pos
            )
    
    @staticmethod
    def write_json(filepath: str, data: Any) -> None:
        """
        Write data to JSON file with proper formatting.
        
        Args:
            filepath: Path to output file
            data: Data to write
        """
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding=Constants.DEFAULT_ENCODING) as f:
            json.dump(data, f, indent=Constants.JSON_INDENT)
    
    @staticmethod
    def create_temp_json(data: Any) -> str:
        """
        Create temporary JSON file with data.
        
        Args:
            data: Data to write to temp file
            
        Returns:
            Path to temporary file
        """
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False,
            encoding=Constants.DEFAULT_ENCODING
        ) as f:
            json.dump(data, f, indent=Constants.JSON_INDENT)
            return f.name


class ValidationUtils:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_partner_data(data: List[Dict]) -> None:
        """
        Validate partner data structure.
        
        Args:
            data: List of partner dictionaries
            
        Raises:
            ValueError: If data structure is invalid
        """
        if not isinstance(data, list):
            raise ValueError(ErrorMessages.INVALID_INPUT_TYPE.format(
                expected_type="list", actual_type=type(data).__name__
            ))
        
        required_fields = {'id', 'monthly_revenue'}
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Partner data at index {i} must be a dictionary")
            
            missing_fields = required_fields - set(item.keys())
            if missing_fields:
                raise ValueError(f"Partner at index {i} missing required fields: {missing_fields}")
            
            # Validate data types
            if not isinstance(item['id'], int):
                raise ValueError(f"Partner ID at index {i} must be integer")
            
            if not isinstance(item['monthly_revenue'], (int, float)):
                raise ValueError(f"Monthly revenue at index {i} must be numeric")


class MathUtils:
    """Utility class for mathematical operations."""
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Safely divide two numbers, returning default if denominator is zero.
        
        Args:
            numerator: Number to divide
            denominator: Number to divide by
            default: Value to return if denominator is zero
            
        Returns:
            Result of division or default value
        """
        return numerator / denominator if denominator != 0 else default
    
    @staticmethod
    def round_currency(value: float, decimal_places: int = 2) -> float:
        """
        Round currency value to specified decimal places.
        
        Args:
            value: Value to round
            decimal_places: Number of decimal places
            
        Returns:
            Rounded value
        """
        return round(value, decimal_places)
