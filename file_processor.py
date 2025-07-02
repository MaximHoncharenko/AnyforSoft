"""
File processing facade for MLM Commission Engine.
"""

from typing import Optional
from datetime import datetime
import logging

from commission_engine import CommissionEngine
from utils import FileUtils


class FileProcessor:
    """
    Handles file I/O operations for commission calculation.
    Separates file processing concerns from business logic.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize file processor.
        
        Args:
            logger: Optional logger for operation tracking
        """
        self.engine = CommissionEngine()
        self.logger = logger or logging.getLogger(__name__)
    
    def process_commission_file(self, input_file: str, output_file: str,
                              target_date: Optional[datetime] = None,
                              include_stats: bool = False) -> dict:
        """
        Process commission calculation from input file to output file.
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file  
            target_date: Date for calculation (defaults to current date)
            include_stats: Whether to include statistics in output
            
        Returns:
            Dictionary with processing results and optional statistics
        """
        try:
            self.logger.info(f"Starting commission processing: {input_file} -> {output_file}")
            
            # Load and validate input data
            data = FileUtils.read_json(input_file)
            self.logger.info(f"Loaded {len(data)} partners from input file")
            
            # Process commission calculation
            result = self._process_commissions(data, target_date)
            
            # Save results
            FileUtils.write_json(output_file, result['commissions'])
            self.logger.info(f"Commission results saved to {output_file}")
            
            # Add statistics if requested
            if include_stats:
                result['statistics'] = self.engine.get_stats()
                result['level_distribution'] = self.engine.get_level_distribution()
            
            self.logger.info("Commission processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Commission processing failed: {str(e)}")
            raise
    
    def _process_commissions(self, data: list, target_date: Optional[datetime]) -> dict:
        """Internal method to process commission calculations."""
        # Load partners and build tree
        self.engine.load_partners(data)
        
        # Calculate daily profits
        self.engine.calculate_daily_profits(target_date)
        
        # Calculate commissions
        commissions = self.engine.calculate_commissions()
        
        return {
            'commissions': commissions,
            'total_partners': len(data),
            'processing_date': target_date.isoformat() if target_date else None
        }
    
    def validate_input_file(self, input_file: str) -> dict:
        """
        Validate input file structure without processing.
        
        Args:
            input_file: Path to input file to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            data = FileUtils.read_json(input_file)
            
            # Try to build tree to validate structure
            temp_engine = CommissionEngine()
            temp_engine.load_partners(data)
            stats = temp_engine.get_stats()
            
            return {
                'valid': True,
                'partner_count': len(data),
                'statistics': stats,
                'message': 'Input file is valid'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'message': f'Input file validation failed: {str(e)}'
            }
