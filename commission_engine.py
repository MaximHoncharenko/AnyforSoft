"""
Refactored High-Performance Daily Commission Engine for MLM Network.

This module provides efficient computation of daily commissions for partners
in a multilevel marketing network using post-order DFS traversal.
Refactored to follow SOLID principles and clean code practices.

The CommissionEngine serves as a facade that orchestrates the commission
calculation process while delegating specific responsibilities to specialized
components.
"""

from types import TracebackType
from typing import Dict, List, Optional, Type
from datetime import datetime
import logging

from tree_components import (
    Partner, PartnerTree, TreeBuilder, TreeValidator, DailyProfitCalculator
)
from commission_components import CommissionCalculator, TreeStatistics
from utils import FileUtils, ValidationUtils
from config import ErrorMessages

# Set up module logger
logger = logging.getLogger(__name__)


class CommissionEngine:
    """
    High-performance commission calculation engine for MLM networks.
    
    Acts as a facade that coordinates commission calculation workflow.
    Follows Single Responsibility Principle by delegating specific tasks
    to specialized components.
    
    Can be used as a context manager for automatic resource cleanup:
    
    with CommissionEngine() as engine:
        engine.load_partners(data)
        commissions = engine.calculate_commissions()
    
    Responsibilities:
    - Orchestrate the commission calculation workflow
    - Validate input state before operations
    - Provide a simple interface for commission processing
    """
    
    def __init__(self):
        """Initialize the commission engine with its components."""
        self.tree: Optional[PartnerTree] = None
        self.tree_builder = TreeBuilder()
        self.tree_validator = TreeValidator()
        self.daily_profit_calculator = DailyProfitCalculator()
        self.commission_calculator = CommissionCalculator()
        self.tree_statistics = TreeStatistics()
    
    def load_partners(self, data: List[Dict]) -> None:
        """
        Load partners from input data and build the tree structure.
        
        Args:
            data: List of partner dictionaries from JSON input
            
        Raises:
            ValueError: If cycles are detected or invalid structure found
            TypeError: If input data is not in expected format
        """
        try:
            logger.info(f"Loading {len(data)} partners")
            
            # Validate input
            if not isinstance(data, list):
                raise TypeError(f"Expected list, got {type(data).__name__}")
            
            if not data:
                raise ValueError("Partner data cannot be empty")
            
            # Validate data structure
            ValidationUtils.validate_partner_data(data)
            
            # Build tree from data
            self.tree = self.tree_builder.build_from_data(data)
            
            # Validate tree structure
            self.tree_validator.validate(self.tree)
            
            logger.info(f"Successfully loaded {self.tree.size()} partners")
            
        except Exception as e:
            logger.error(f"Failed to load partners: {e}")
            self.tree = None  # Reset state on error
            raise
    
    def calculate_daily_profits(self, target_date: Optional[datetime] = None) -> None:
        """
        Calculate daily profits from monthly revenue.
        
        Args:
            target_date: Date for which to calculate profits (defaults to current date)
            
        Raises:
            RuntimeError: If no partners are loaded
            ValueError: If target_date is invalid
        """
        try:
            self._ensure_tree_loaded()
            assert self.tree is not None  # Type hint for mypy
            
            logger.debug(f"Calculating daily profits for date: {target_date}")
            self.daily_profit_calculator.calculate_daily_profits(self.tree, target_date)
            logger.debug("Daily profits calculated successfully")
            
        except Exception as e:
            logger.error(f"Failed to calculate daily profits: {e}")
            raise
    
    def calculate_commissions(self) -> Dict[str, float]:
        """
        Calculate commissions for all partners using post-order DFS.
        
        Returns:
            Dictionary mapping partner IDs to their total commissions
            
        Raises:
            RuntimeError: If no partners are loaded
            
        Time Complexity: O(n) where n is the number of partners
        Space Complexity: O(h) where h is the height of the tree
        """
        try:
            self._ensure_tree_loaded()
            assert self.tree is not None  # Type hint for mypy
            
            logger.debug("Starting commission calculation")
            result = self.commission_calculator.calculate_commissions(self.tree)
            logger.info(f"Commission calculation completed for {len(result)} partners")
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate commissions: {e}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the partner network.
        
        Returns:
            Dictionary with network statistics
            
        Raises:
            RuntimeError: If no partners are loaded
        """
        self._ensure_tree_loaded()
        assert self.tree is not None  # Type hint for mypy
        return self.tree_statistics.get_stats(self.tree)
    
    def get_level_distribution(self) -> Dict[int, int]:
        """
        Get distribution of partners across different levels.
        
        Returns:
            Dictionary mapping level to partner count
            
        Raises:
            RuntimeError: If no partners are loaded
        """
        self._ensure_tree_loaded()
        assert self.tree is not None  # Type hint for mypy
        return self.tree_statistics.get_level_distribution(self.tree)
    
    def process_file(self, input_file: str, output_file: str) -> None:
        """
        Process commission calculation from input file to output file.
        
        This is a convenience method that handles the complete workflow:
        1. Load data from input JSON file
        2. Build partner tree and validate structure
        3. Calculate daily profits from monthly revenue
        4. Calculate commissions using post-order DFS
        5. Save results to output JSON file
        
        Args:
            input_file: Path to input JSON file containing partner data.
                       Expected format: List of dictionaries with keys:
                       - id (int): Partner unique identifier
                       - parent_id (int, optional): Parent partner ID
                       - name (str, optional): Partner name
                       - monthly_revenue (float): Monthly gross profit
            output_file: Path to output JSON file for commission results.
                        Output format: Dictionary mapping partner_id -> commission
        
        Example:
            >>> engine = CommissionEngine()
            >>> engine.process_file('partners.json', 'commissions.json')
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            json.JSONDecodeError: If input file contains invalid JSON
            ValueError: If data structure is invalid or contains cycles
            IOError: If output file cannot be written
        """
        try:
            logger.info(f"Processing commission calculation: {input_file} -> {output_file}")
            
            # Load input data
            data = FileUtils.read_json(input_file)
            
            # Process data
            self.load_partners(data)
            self.calculate_daily_profits()
            commissions = self.calculate_commissions()
            
            # Save results
            FileUtils.write_json(output_file, commissions)
            
            logger.info(f"Commission calculation completed successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Input file not found: {input_file}")
            raise
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get performance metrics for the current tree.
        
        Returns:
            Dictionary with performance-related metrics
            
        Raises:
            RuntimeError: If no partners are loaded
        """
        self._ensure_tree_loaded()
        assert self.tree is not None
        
        stats = self.get_stats()
        total_partners = stats['total_partners']
        max_depth = stats['max_depth']
        
        # Estimate memory usage (rough approximation)
        estimated_memory_kb = total_partners * 0.5  # ~0.5KB per partner
        
        # Performance score based on tree structure
        performance_score = min(100.0, (10000 / max(total_partners, 1)) * 100)
        
        return {
            'total_partners': float(total_partners),
            'max_depth': float(max_depth),
            'estimated_memory_kb': estimated_memory_kb,
            'performance_score': performance_score,
            'complexity_factor': float(max_depth * total_partners)
        }
    
    def reset(self) -> None:
        """Reset the engine state, clearing all loaded data."""
        logger.debug("Resetting commission engine state")
        self.tree = None
    
    def is_loaded(self) -> bool:
        """Check if partners have been loaded."""
        return self.tree is not None
    
    def __enter__(self) -> 'CommissionEngine':
        """Context manager entry."""
        logger.debug("Entering CommissionEngine context")
        return self
    
    def __exit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Context manager exit - cleanup resources."""
        logger.debug("Exiting CommissionEngine context")
        if exc_type is not None:
            logger.error(f"Exception in context: {exc_type.__name__}: {exc_val}")
        self.reset()
    
    def _ensure_tree_loaded(self) -> None:
        """
        Ensure that a partner tree has been loaded.
        
        Raises:
            RuntimeError: If no partners have been loaded
        """
        if self.tree is None:
            error_msg = ErrorMessages.NO_PARTNERS_LOADED
            logger.error(error_msg)
            raise RuntimeError(error_msg)


# Backward compatibility - keep the old Partner class available
# for existing code that imports it directly
__all__ = ['CommissionEngine', 'Partner']
