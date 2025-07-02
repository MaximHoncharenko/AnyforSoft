#!/usr/bin/env python3
"""
Main CLI interface for the MLM Commission Engine.

Usage:
    python main.py --input partners.json --output commissions.json
"""

import argparse
import sys
import time
import logging
from pathlib import Path

from file_processor import FileProcessor


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def main():
    """Main entry point for the commission calculation CLI."""
    parser = argparse.ArgumentParser(
        description="Calculate daily commissions for MLM partner network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --input dataset.json --output commissions.json
    python main.py -i partners.json -o results.json --verbose
    python main.py --input data.json --output results.json --validate-only
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        type=str,
        help='Input JSON file with partner data'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        type=str,
        help='Output JSON file for commission results'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with statistics and logging'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate input file structure without processing'
    )
    
    parser.add_argument(
        '--include-stats',
        action='store_true',
        help='Include network statistics in verbose output'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Validate input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file '{args.input}' not found")
        sys.exit(1)
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize file processor
        processor = FileProcessor(logger)
        
        # Handle validation-only mode
        if args.validate_only:
            logger.info(f"Validating input file: {args.input}")
            result = processor.validate_input_file(args.input)
            
            if result['valid']:
                print(f"✓ {result['message']}")
                if args.verbose:
                    stats = result['statistics']
                    print(f"  - Partners: {result['partner_count']}")
                    print(f"  - Depth: {stats['max_depth']} levels")
                    print(f"  - Roots: {stats['root_partners']}")
                    print(f"  - Leaves: {stats['leaf_partners']}")
            else:
                print(f"✗ {result['message']}")
                sys.exit(1)
            return
        
        # Process commission calculation
        start_time = time.time()
        if args.verbose:
            logger.info(f"Processing {args.input}...")
        
        result = processor.process_commission_file(
            args.input, 
            args.output,
            include_stats=args.include_stats or args.verbose
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if args.verbose:
            print(f"✓ Successfully processed {result['total_partners']} partners")
            
            if 'statistics' in result:
                stats = result['statistics']
                print(f"✓ Network depth: {stats['max_depth']} levels")
                print(f"✓ Root partners: {stats['root_partners']}")
                print(f"✓ Leaf partners: {stats['leaf_partners']}")
            
            if 'level_distribution' in result:
                print("✓ Level distribution:")
                for level, count in sorted(result['level_distribution'].items()):
                    print(f"  Level {level}: {count} partners")
            
            print(f"✓ Processing time: {processing_time:.3f} seconds")
            print(f"✓ Output saved to: {args.output}")
        else:
            print(f"Commission calculation completed. Results saved to {args.output}")
    
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
