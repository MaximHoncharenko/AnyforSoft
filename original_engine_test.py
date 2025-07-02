"""
Original Commission Engine for comparison.
"""

from typing import Dict, List, Optional, Set
import json
import calendar
from datetime import datetime


class OriginalPartner:
    """Represents a partner in the MLM network."""
    
    def __init__(self, partner_id: int, parent_id: Optional[int], 
                 name: str, monthly_revenue: float):
        self.id = partner_id
        self.parent_id = parent_id
        self.name = name
        self.monthly_revenue = monthly_revenue
        self.children: List['OriginalPartner'] = []
        self.daily_profit: float = 0.0
        self.total_commission: float = 0.0


class OriginalCommissionEngine:
    """Original commission calculation engine."""
    
    COMMISSION_RATE = 0.05  # 5% commission rate
    
    def __init__(self):
        self.partners: Dict[int, OriginalPartner] = {}
        self.roots: List[OriginalPartner] = []
        self.visited: Set[int] = set()
        self.rec_stack: Set[int] = set()
    
    def load_partners(self, data: List[Dict]) -> None:
        # Create all partner objects first
        for item in data:
            partner = OriginalPartner(
                partner_id=item['id'],
                parent_id=item.get('parent_id'),
                name=item.get('name', ''),
                monthly_revenue=item['monthly_revenue']
            )
            self.partners[partner.id] = partner
        
        # Build parent-child relationships
        for partner in self.partners.values():
            if partner.parent_id is None:
                self.roots.append(partner)
            else:
                if partner.parent_id not in self.partners:
                    raise ValueError(f"Parent {partner.parent_id} not found for partner {partner.id}")
                parent = self.partners[partner.parent_id]
                parent.children.append(partner)
        
        # Detect cycles
        self._detect_cycles()
        
        if not self.roots:
            raise ValueError("No root partners found")
    
    def _detect_cycles(self) -> None:
        self.visited.clear()
        self.rec_stack.clear()
        
        for partner in self.partners.values():
            if partner.id not in self.visited:
                if self._has_cycle_util(partner):
                    raise ValueError(f"Cycle detected involving partner {partner.id}")
    
    def _has_cycle_util(self, partner: OriginalPartner) -> bool:
        self.visited.add(partner.id)
        self.rec_stack.add(partner.id)
        
        for child in partner.children:
            if child.id not in self.visited:
                if self._has_cycle_util(child):
                    return True
            elif child.id in self.rec_stack:
                return True
        
        self.rec_stack.remove(partner.id)
        return False
    
    def calculate_daily_profits(self, target_date: Optional[datetime] = None) -> None:
        if target_date is None:
            target_date = datetime.now()
        
        days_in_month = calendar.monthrange(target_date.year, target_date.month)[1]
        
        for partner in self.partners.values():
            partner.daily_profit = partner.monthly_revenue / days_in_month
    
    def calculate_commissions(self) -> Dict[str, float]:
        # Reset commission calculations
        for partner in self.partners.values():
            partner.total_commission = 0.0
        
        # Calculate commissions using post-order traversal
        for root in self.roots:
            self._calculate_subtree_commission(root)
        
        # Format output with 2 decimal precision
        return {
            str(partner.id): round(partner.total_commission, 2)
            for partner in self.partners.values()
        }
    
    def _calculate_subtree_commission(self, partner: OriginalPartner) -> float:
        # Calculate subtree profit (profit from all descendants)
        subtree_profit = 0.0
        
        # First, recursively process all children (post-order)
        for child in partner.children:
            child_subtree_profit = self._calculate_subtree_commission(child)
            subtree_profit += child_subtree_profit
        
        # Add this partner's own profit to subtree total
        subtree_profit += partner.daily_profit
        
        # Calculate commission for this partner (5% of descendants' profits only)
        descendants_profit = subtree_profit - partner.daily_profit
        partner.total_commission = descendants_profit * self.COMMISSION_RATE
        
        return subtree_profit


def test_original_vs_refactored():
    """Test original vs refactored implementation."""
    # Load data
    with open('dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Test original
    original_engine = OriginalCommissionEngine()
    original_engine.load_partners(data)
    original_engine.calculate_daily_profits()
    original_commissions = original_engine.calculate_commissions()
    
    # Save original results
    with open('commissions_original_test.json', 'w', encoding='utf-8') as f:
        json.dump(original_commissions, f, indent=2)
    
    print(f"Original engine processed {len(original_commissions)} partners")
    return original_commissions


if __name__ == "__main__":
    test_original_vs_refactored()
