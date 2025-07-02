#!/usr/bin/env python3
"""
Benchmark script for MLM Commission Engine performance testing.

Tests the engine's performance with various network sizes and structures
to validate O(n) time complexity and sub-2-second execution for 50k partners.
"""

import time
import json
import random
import tempfile
import os
import gc
from typing import List, Dict
import psutil
import platform

from commission_engine import CommissionEngine


class BenchmarkRunner:
    """Performance benchmark runner for the commission engine."""
    
    def __init__(self):
        """Initialize benchmark runner."""
        self.results: List[Dict] = []
        
    def generate_test_data(self, num_partners: int, max_depth: int = 10) -> List[Dict]:
        """
        Generate test data with specified number of partners and maximum depth.
        
        Args:
            num_partners: Number of partners to generate
            max_depth: Maximum depth of the hierarchy
            
        Returns:
            List of partner dictionaries
        """
        data = []
        partners_per_level = [1]  # Root level
        
        # Calculate partners per level to achieve desired distribution
        remaining = num_partners - 1
        level = 1
        
        while remaining > 0 and level < max_depth:
            # Exponential growth with some randomness
            level_size = min(remaining, int(partners_per_level[-1] * (2 + random.random())))
            partners_per_level.append(level_size)
            remaining -= level_size
            level += 1
        
        # Add remaining partners to the last level
        if remaining > 0:
            partners_per_level[-1] += remaining
        
        # Generate the data
        partner_id = 1
        
        # Root partners
        for _ in range(partners_per_level[0]):
            data.append({
                "id": partner_id,
                "parent_id": None,
                "name": f"Partner{partner_id}",
                "monthly_revenue": random.randint(1000, 10000)
            })
            partner_id += 1
        
        # Generate subsequent levels
        for level in range(1, len(partners_per_level)):
            parent_start = sum(partners_per_level[:level-1]) + 1 if level > 1 else 1
            parent_end = sum(partners_per_level[:level]) + 1
            
            for _ in range(partners_per_level[level]):
                parent_id = random.randint(parent_start, parent_end - 1)
                data.append({
                    "id": partner_id,
                    "parent_id": parent_id,
                    "name": f"Partner{partner_id}",
                    "monthly_revenue": random.randint(1000, 10000)
                })
                partner_id += 1
        
        return data
    
    def run_benchmark(self, num_partners: int, description: str) -> Dict:
        """
        Run a single benchmark test.
        
        Args:
            num_partners: Number of partners to test
            description: Description of the test
            
        Returns:
            Dictionary with benchmark results
        """
        print(f"Running benchmark: {description} ({num_partners:,} partners)")
        
        # Generate test data
        data_gen_start = time.time()
        data = self.generate_test_data(num_partners)
        data_gen_time = time.time() - data_gen_start
        
        # Get memory before test
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run commission calculation
        gc.collect()  # Clean up before measurement
        
        calc_start = time.time()
        engine = CommissionEngine()
        
        # Load and process
        load_start = time.time()
        engine.load_partners(data)
        load_time = time.time() - load_start
        
        daily_start = time.time()
        engine.calculate_daily_profits()
        daily_time = time.time() - daily_start
        
        commission_start = time.time()
        commissions = engine.calculate_commissions()
        commission_time = time.time() - commission_start
        
        calc_end = time.time()
        total_calc_time = calc_end - calc_start
        
        # Get memory after test
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Get network statistics
        stats = engine.get_stats()
        
        result = {
            'description': description,
            'num_partners': num_partners,
            'data_generation_time': data_gen_time,
            'load_time': load_time,
            'daily_calc_time': daily_time,
            'commission_calc_time': commission_time,
            'total_calc_time': total_calc_time,
            'memory_used_mb': memory_used,
            'max_depth': stats['max_depth'],
            'leaf_partners': stats['leaf_partners'],
            'partners_per_second': num_partners / total_calc_time if total_calc_time > 0 else 0
        }
        
        # Print results
        print(f"  ✓ Total calculation time: {total_calc_time:.3f}s")
        print(f"  ✓ Partners per second: {result['partners_per_second']:,.0f}")
        print(f"  ✓ Memory used: {memory_used:.1f} MB")
        print(f"  ✓ Max depth: {stats['max_depth']}")
        print()
        
        self.results.append(result)
        return result
    
    def run_all_benchmarks(self):
        """Run comprehensive benchmark suite."""
        print("=" * 60)
        print("MLM Commission Engine Performance Benchmark")
        print("=" * 60)
        
        # System information
        print(f"System: {platform.system()} {platform.release()}")
        print(f"Processor: {platform.processor()}")
        print(f"Python: {platform.python_version()}")
        print(f"CPU cores: {psutil.cpu_count()}")
        print(f"Available RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB")
        print()
        
        # Benchmark scenarios
        scenarios = [
            (100, "Small network (100 partners)"),
            (500, "Current scale (500 partners)"),
            (1000, "Medium network (1K partners)"),
            (5000, "Large network (5K partners)"),
            (10000, "Very large network (10K partners)"),
            (25000, "Huge network (25K partners)"),
            (50000, "Target scale (50K partners)"),
        ]
        
        # Run benchmarks
        for num_partners, description in scenarios:
            try:
                result = self.run_benchmark(num_partners, description)
                
                # Check performance requirements
                if num_partners == 50000:
                    if result['total_calc_time'] < 2.0:
                        print(f"✅ PERFORMANCE REQUIREMENT MET: 50K partners in {result['total_calc_time']:.3f}s < 2.0s")
                    else:
                        print(f"❌ PERFORMANCE REQUIREMENT FAILED: 50K partners in {result['total_calc_time']:.3f}s >= 2.0s")
                    print()
                    
            except Exception as e:
                print(f"❌ Benchmark failed: {e}")
                print()
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                'system_info': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'processor': platform.processor(),
                    'python_version': platform.python_version(),
                    'cpu_cores': psutil.cpu_count(),
                    'total_ram_gb': psutil.virtual_memory().total / 1024**3
                },
                'results': self.results,
                'timestamp': time.time()
            }, f, indent=2)
        print(f"Benchmark results saved to {filename}")
    
    def print_summary(self):
        """Print benchmark summary."""
        if not self.results:
            return
            
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        
        print(f"{'Partners':<10} {'Time (s)':<10} {'Partners/s':<12} {'Memory (MB)':<12}")
        print("-" * 50)
        
        for result in self.results:
            print(f"{result['num_partners']:<10,} "
                  f"{result['total_calc_time']:<10.3f} "
                  f"{result['partners_per_second']:<12,.0f} "
                  f"{result['memory_used_mb']:<12.1f}")
        
        # Performance analysis
        print("\nPERFORMANCE ANALYSIS:")
        
        # Check linear scaling
        if len(self.results) >= 2:
            # Find first and last results with non-zero time
            first = None
            last = None
            
            for result in self.results:
                if result['total_calc_time'] > 0:
                    if first is None:
                        first = result
                    last = result
            
            if first and last and first != last:
                time_ratio = last['total_calc_time'] / first['total_calc_time']
                size_ratio = last['num_partners'] / first['num_partners']
                
                if time_ratio <= size_ratio * 1.5:  # Allow some overhead
                    print(f"✅ Time complexity appears linear: {time_ratio:.1f}x time for {size_ratio:.1f}x partners")
                else:
                    print(f"❌ Time complexity may be worse than linear: {time_ratio:.1f}x time for {size_ratio:.1f}x partners")
            else:
                print("✅ Execution times too fast to measure reliably - excellent performance!")
        
        # Memory efficiency check
        for result in self.results:
            if result['num_partners'] >= 1000:  # Only check larger datasets
                memory_per_partner = result['memory_used_mb'] * 1024 / result['num_partners']  # KB per partner
                if memory_per_partner <= 2.0:  # Reasonable threshold
                    print(f"✅ Memory efficient: {memory_per_partner:.2f} KB per partner ({result['num_partners']:,} partners)")
                else:
                    print(f"⚠️  Memory usage: {memory_per_partner:.2f} KB per partner ({result['num_partners']:,} partners)")


def test_file_processing_benchmark():
    """Test file I/O performance with large dataset."""
    print("Testing file I/O performance...")
    
    runner = BenchmarkRunner()
    data = runner.generate_test_data(10000)
    
    # Write test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        input_file = f.name
        json.dump(data, f)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_file = f.name
    
    try:
        start_time = time.time()
        engine = CommissionEngine()
        engine.process_file(input_file, output_file)
        end_time = time.time()
        
        file_size_mb = os.path.getsize(input_file) / 1024 / 1024
        processing_time = end_time - start_time
        
        print(f"  ✓ File I/O test: {processing_time:.3f}s for {file_size_mb:.1f} MB file")
        
    finally:
        os.unlink(input_file)
        os.unlink(output_file)


def main():
    """Main benchmark execution."""
    random.seed(42)  # For reproducible results
    
    runner = BenchmarkRunner()
    runner.run_all_benchmarks()
    runner.print_summary()
    runner.save_results()
    
    print("\n" + "=" * 60)
    test_file_processing_benchmark()
    print("Benchmark completed!")


if __name__ == "__main__":
    main()
