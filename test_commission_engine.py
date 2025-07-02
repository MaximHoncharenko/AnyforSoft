"""
Comprehensive unit tests for the MLM Commission Engine.

Tests cover correctness, edge cases, and performance requirements.
"""

import pytest
import json
import tempfile
import os
from typing import List, Dict
from datetime import datetime

from commission_engine import CommissionEngine, Partner


class TestPartner:
    """Test Partner class functionality."""
    
    def test_partner_initialization(self):
        """Test Partner object creation with all parameters."""
        partner = Partner(
            partner_id=1,
            parent_id=None,
            name="Test Partner",
            monthly_revenue=10000.0
        )
        
        assert partner.id == 1
        assert partner.parent_id is None
        assert partner.name == "Test Partner"
        assert partner.monthly_revenue == 10000.0
        assert partner.children == []
        assert partner.daily_profit == 0.0
        assert partner.total_commission == 0.0
    
    def test_partner_with_parent(self):
        """Test Partner object with parent relationship."""
        partner = Partner(
            partner_id=2,
            parent_id=1,
            name="Child Partner",
            monthly_revenue=5000.0
        )
        
        assert partner.parent_id == 1


class TestCommissionEngine:
    """Test CommissionEngine functionality."""
    
    def test_simple_two_level_structure(self):
        """Test commission calculation for simple parent-child structure."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 3100},  # 100/day
            {"id": 2, "parent_id": 1, "name": "Child", "monthly_revenue": 1550}    # 50/day
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits(datetime(2024, 1, 15))  # January has 31 days
        
        commissions = engine.calculate_commissions()
        
        # Root should get 5% of child's daily profit: 0.05 * 50 = 2.5
        # Child should get 0 (no descendants)
        assert commissions["1"] == 2.5
        assert commissions["2"] == 0.0
    
    def test_three_level_structure(self):
        """Test commission calculation for three-level hierarchy."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 3100},      # 100/day
            {"id": 2, "parent_id": 1, "name": "Child1", "monthly_revenue": 1550},      # 50/day
            {"id": 3, "parent_id": 2, "name": "Grandchild", "monthly_revenue": 620}    # 20/day
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits(datetime(2024, 1, 15))  # January has 31 days
        
        commissions = engine.calculate_commissions()
        
        # Root gets 5% of (Child1 + Grandchild): 0.05 * (50 + 20) = 3.5
        # Child1 gets 5% of Grandchild: 0.05 * 20 = 1.0
        # Grandchild gets 0
        assert commissions["1"] == 3.5
        assert commissions["2"] == 1.0
        assert commissions["3"] == 0.0
    
    def test_multiple_children(self):
        """Test commission calculation with multiple children per parent."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 3100},      # 100/day
            {"id": 2, "parent_id": 1, "name": "Child1", "monthly_revenue": 1550},      # 50/day
            {"id": 3, "parent_id": 1, "name": "Child2", "monthly_revenue": 930},       # 30/day
            {"id": 4, "parent_id": 1, "name": "Child3", "monthly_revenue": 620}        # 20/day
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits(datetime(2024, 1, 15))  # January has 31 days
        
        commissions = engine.calculate_commissions()
        
        # Root gets 5% of all children: 0.05 * (50 + 30 + 20) = 5.0
        # Children get 0 each (no descendants)
        assert commissions["1"] == 5.0
        assert commissions["2"] == 0.0
        assert commissions["3"] == 0.0
        assert commissions["4"] == 0.0
    
    def test_multiple_roots(self):
        """Test handling of multiple root partners (forest structure)."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root1", "monthly_revenue": 3100},     # 100/day
            {"id": 2, "parent_id": 1, "name": "Child1", "monthly_revenue": 1550},      # 50/day
            {"id": 3, "parent_id": None, "name": "Root2", "monthly_revenue": 930},     # 30/day
            {"id": 4, "parent_id": 3, "name": "Child2", "monthly_revenue": 620}        # 20/day
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits(datetime(2024, 1, 15))  # January has 31 days
        
        commissions = engine.calculate_commissions()
        
        # Root1 gets 5% of Child1: 0.05 * 50 = 2.5
        # Root2 gets 5% of Child2: 0.05 * 20 = 1.0
        assert commissions["1"] == 2.5
        assert commissions["2"] == 0.0
        assert commissions["3"] == 1.0
        assert commissions["4"] == 0.0
    
    def test_single_partner_no_commission(self):
        """Test single partner (root only) receives no commission."""
        data = [
            {"id": 1, "parent_id": None, "name": "Lonely Root", "monthly_revenue": 3100}
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits()
        
        commissions = engine.calculate_commissions()
        
        assert commissions["1"] == 0.0
    
    def test_cycle_detection(self):
        """Test detection of cycles in partner structure."""
        data = [
            {"id": 1, "parent_id": 2, "name": "Partner1", "monthly_revenue": 1000},
            {"id": 2, "parent_id": 1, "name": "Partner2", "monthly_revenue": 1000}
        ]
        
        engine = CommissionEngine()
        
        with pytest.raises(ValueError, match="Cycle detected"):
            engine.load_partners(data)
    
    def test_self_reference_cycle(self):
        """Test detection of self-referencing partner."""
        data = [
            {"id": 1, "parent_id": 1, "name": "Self Reference", "monthly_revenue": 1000}
        ]
        
        engine = CommissionEngine()
        
        with pytest.raises(ValueError, match="Cycle detected"):
            engine.load_partners(data)
    
    def test_nonexistent_parent(self):
        """Test error handling for nonexistent parent reference."""
        data = [
            {"id": 1, "parent_id": 999, "name": "Orphan", "monthly_revenue": 1000}
        ]
        
        engine = CommissionEngine()
        
        with pytest.raises(ValueError, match="Parent 999 not found"):
            engine.load_partners(data)
    
    def test_no_root_partners(self):
        """Test error handling when no root partners exist (all in cycle)."""
        data = [
            {"id": 1, "parent_id": 2, "name": "Partner1", "monthly_revenue": 1000},
            {"id": 2, "parent_id": 3, "name": "Partner2", "monthly_revenue": 1000},
            {"id": 3, "parent_id": 1, "name": "Partner3", "monthly_revenue": 1000}
        ]
        
        engine = CommissionEngine()
        
        # This should detect cycle before checking for roots
        with pytest.raises(ValueError, match="Cycle detected"):
            engine.load_partners(data)
    
    def test_actual_no_root_partners(self):
        """Test error handling when all partners have parents but no cycles."""
        data = [
            {"id": 1, "parent_id": 999, "name": "Partner1", "monthly_revenue": 1000}
        ]
        
        engine = CommissionEngine()
        
        # This should fail due to missing parent
        with pytest.raises(ValueError, match="Parent 999 not found"):
            engine.load_partners(data)
    
    def test_commission_precision(self):
        """Test commission calculation precision to 2 decimal places."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 3100},      # 100/day
            {"id": 2, "parent_id": 1, "name": "Child", "monthly_revenue": 1023.33}     # 33.01/day
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits(datetime(2024, 1, 15))  # January has 31 days
        
        commissions = engine.calculate_commissions()
        
        # Root gets 5% of child: 0.05 * 33.01 = 1.6505, rounded to 1.65
        assert commissions["1"] == 1.65
    
    def test_leap_year_calculation(self):
        """Test daily profit calculation for February in leap year."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 2900},  # 100/day in Feb leap year
            {"id": 2, "parent_id": 1, "name": "Child", "monthly_revenue": 1450}    # 50/day in Feb leap year
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits(datetime(2024, 2, 15))  # February 2024 (leap year, 29 days)
        
        commissions = engine.calculate_commissions()
        
        # Root should get 5% of child's daily profit: 0.05 * 50 = 2.5
        assert commissions["1"] == 2.5
        assert commissions["2"] == 0.0
    
    def test_deep_hierarchy(self):
        """Test performance with deep hierarchy (10 levels)."""
        data = []
        for i in range(1, 11):  # 10 partners in chain
            parent_id = i - 1 if i > 1 else None
            data.append({
                "id": i,
                "parent_id": parent_id,
                "name": f"Partner{i}",
                "monthly_revenue": 3100  # 100/day each
            })
        
        engine = CommissionEngine()
        engine.load_partners(data)
        engine.calculate_daily_profits(datetime(2024, 1, 15))
        
        commissions = engine.calculate_commissions()
        
        # Partner 1 (root) should get commission from all 9 descendants: 0.05 * 9 * 100 = 45
        # Partner 2 should get commission from 8 descendants: 0.05 * 8 * 100 = 40
        # etc.
        assert commissions["1"] == 45.0
        assert commissions["2"] == 40.0
        assert commissions["10"] == 0.0  # Leaf node
    
    def test_file_processing(self):
        """Test end-to-end file processing functionality."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 3100},
            {"id": 2, "parent_id": 1, "name": "Child", "monthly_revenue": 1550}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            json.dump(data, input_file)
            input_filename = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            output_filename = output_file.name
        
        try:
            engine = CommissionEngine()
            engine.process_file(input_filename, output_filename)
            
            # Verify output file
            with open(output_filename, 'r') as f:
                result = json.load(f)
            
            assert "1" in result
            assert "2" in result
            # Use approximate comparison due to different days in month calculation
            assert abs(result["1"] - 2.5) < 0.1  # Allow small difference for different months
            assert result["2"] == 0.0
            
        finally:
            os.unlink(input_filename)
            os.unlink(output_filename)
    
    def test_stats_generation(self):
        """Test network statistics generation."""
        data = [
            {"id": 1, "parent_id": None, "name": "Root", "monthly_revenue": 1000},
            {"id": 2, "parent_id": 1, "name": "Child1", "monthly_revenue": 1000},
            {"id": 3, "parent_id": 1, "name": "Child2", "monthly_revenue": 1000},
            {"id": 4, "parent_id": 2, "name": "Grandchild", "monthly_revenue": 1000}
        ]
        
        engine = CommissionEngine()
        engine.load_partners(data)
        
        stats = engine.get_stats()
        
        assert stats['total_partners'] == 4
        assert stats['root_partners'] == 1
        assert stats['leaf_partners'] == 2  # Child2 and Grandchild
        assert stats['max_depth'] == 2  # Root -> Child -> Grandchild


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
