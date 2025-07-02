"""
Tree building and validation components for MLM network.
"""

from typing import Dict, List, Set, Optional
from datetime import datetime
import calendar

from config import Constants, ErrorMessages
from utils import ValidationUtils, MathUtils


class Partner:
    """Represents a partner in the MLM network."""
    
    def __init__(self, partner_id: int, parent_id: Optional[int] = None, 
                 name: str = '', monthly_revenue: float = 0.0):
        """
        Initialize a Partner instance.
        
        Args:
            partner_id: Unique identifier for the partner
            parent_id: ID of the parent partner (None for root)
            name: Partner's name
            monthly_revenue: Monthly gross profit in monetary units
        """
        self.id = partner_id
        self.parent_id = parent_id
        self.name = name
        self.monthly_revenue = monthly_revenue
        self.children: List['Partner'] = []
        self.daily_profit: float = 0.0
        self.total_commission: float = 0.0
    
    def add_child(self, child: 'Partner') -> None:
        """Add a child partner."""
        self.children.append(child)
    
    def is_leaf(self) -> bool:
        """Check if partner is a leaf node (no children)."""
        return len(self.children) == 0
    
    def is_root(self) -> bool:
        """Check if partner is a root node (no parent)."""
        return self.parent_id is None


class PartnerTree:
    """Represents the MLM partner tree structure."""
    
    def __init__(self):
        """Initialize empty partner tree."""
        self.partners: Dict[int, Partner] = {}
        self.roots: List[Partner] = []
    
    def add_partner(self, partner: Partner) -> None:
        """Add partner to the tree."""
        self.partners[partner.id] = partner
        if partner.is_root():
            self.roots.append(partner)
    
    def get_partner(self, partner_id: int) -> Optional[Partner]:
        """Get partner by ID."""
        return self.partners.get(partner_id)
    
    def get_all_partners(self) -> List[Partner]:
        """Get all partners as a list."""
        return list(self.partners.values())
    
    def get_roots(self) -> List[Partner]:
        """Get all root partners."""
        return self.roots
    
    def get_leaves(self) -> List[Partner]:
        """Get all leaf partners."""
        return [p for p in self.partners.values() if p.is_leaf()]
    
    def size(self) -> int:
        """Get total number of partners."""
        return len(self.partners)


class TreeBuilder:
    """Builds partner tree from input data."""
    
    def build_from_data(self, data: List[Dict]) -> PartnerTree:
        """
        Build partner tree from input data.
        
        Args:
            data: List of partner dictionaries
            
        Returns:
            Constructed PartnerTree
            
        Raises:
            ValueError: If data is invalid or relationships are incorrect
        """
        # Validate input data
        ValidationUtils.validate_partner_data(data)
        
        tree = PartnerTree()
        
        # Create all partner objects first
        self._create_partners(data, tree)
        
        # Build parent-child relationships
        self._build_relationships(tree)
        
        return tree
    
    def _create_partners(self, data: List[Dict], tree: PartnerTree) -> None:
        """Create partner objects from data."""
        for item in data:
            partner = Partner(
                partner_id=item['id'],
                parent_id=item.get('parent_id'),
                name=item.get('name', ''),
                monthly_revenue=item['monthly_revenue']
            )
            tree.add_partner(partner)
    
    def _build_relationships(self, tree: PartnerTree) -> None:
        """Build parent-child relationships in the tree."""
        for partner in tree.get_all_partners():
            if not partner.is_root():
                if partner.parent_id is None:
                    continue  # Skip if parent_id is None
                    
                parent = tree.get_partner(partner.parent_id)
                if parent is None:
                    raise ValueError(ErrorMessages.PARENT_NOT_FOUND.format(
                        parent_id=partner.parent_id, partner_id=partner.id
                    ))
                parent.add_child(partner)


class CycleDetector:
    """Detects cycles in partner network using DFS."""
    
    def __init__(self):
        """Initialize cycle detector."""
        self.visited: Set[int] = set()
        self.rec_stack: Set[int] = set()
    
    def has_cycles(self, tree: PartnerTree) -> bool:
        """
        Check if tree contains cycles by following parent-child relationships.
        
        Args:
            tree: PartnerTree to check
            
        Returns:
            False if no cycles detected
            
        Raises:
            ValueError: If a cycle is found (with details)
        """
        self.visited.clear()
        self.rec_stack.clear()
        
        # Check each partner for cycles by following parent links
        for partner in tree.get_all_partners():
            if partner.id not in self.visited:
                if self._has_cycle_from_partner(partner, tree):
                    raise ValueError(ErrorMessages.CYCLE_DETECTED.format(
                        partner_id=partner.id
                    ))
        
        return False
    
    def _has_cycle_from_partner(self, partner: Partner, tree: PartnerTree) -> bool:
        """
        Check for cycle starting from a specific partner by following parent links.
        
        Args:
            partner: Partner to start cycle detection from
            tree: PartnerTree containing all partners
            
        Returns:
            True if cycle is detected, False otherwise
        """
        visited_in_path: Set[int] = set()
        current = partner
        
        while current is not None:
            if current.id in visited_in_path:
                # Found a cycle
                return True
            
            visited_in_path.add(current.id)
            self.visited.add(current.id)
            
            # Follow parent link
            if current.parent_id is None:
                break
                
            current = tree.get_partner(current.parent_id)
            if current is None:
                # Parent not found - this is a structural error but not a cycle
                break
        
        return False


class TreeValidator:
    """Validates partner tree structure and integrity."""
    
    def __init__(self):
        """Initialize tree validator."""
        self.cycle_detector = CycleDetector()
    
    def validate(self, tree: PartnerTree) -> None:
        """
        Validate complete tree structure.
        
        Args:
            tree: PartnerTree to validate
            
        Raises:
            ValueError: If tree structure is invalid
        """
        # Check for cycles first, as they may explain why there are no roots
        self._validate_no_cycles(tree)
        self._validate_has_roots(tree)
    
    def _validate_has_roots(self, tree: PartnerTree) -> None:
        """Ensure tree has at least one root."""
        if not tree.get_roots():
            raise ValueError(ErrorMessages.NO_ROOT_PARTNERS)
    
    def _validate_no_cycles(self, tree: PartnerTree) -> None:
        """Ensure tree has no cycles."""
        self.cycle_detector.has_cycles(tree)


class DailyProfitCalculator:
    """Calculates daily profits from monthly revenue."""
    
    def calculate_daily_profits(self, tree: PartnerTree, 
                              target_date: Optional[datetime] = None) -> None:
        """
        Calculate daily profits for all partners.
        
        Args:
            tree: PartnerTree to process
            target_date: Date for calculation (defaults to current date)
            
        Raises:
            ValueError: If target_date is invalid
        """
        if target_date is None:
            target_date = datetime.now()
        
        self._validate_date(target_date)
        days_in_month = self._get_days_in_month(target_date)
        
        for partner in tree.get_all_partners():
            partner.daily_profit = MathUtils.safe_divide(
                partner.monthly_revenue, days_in_month
            )
    
    def _validate_date(self, target_date: datetime) -> None:
        """Validate that target_date is a proper datetime object."""
        if not isinstance(target_date, datetime):
            raise ValueError(ErrorMessages.INVALID_INPUT_TYPE.format(
                expected_type="datetime", actual_type=type(target_date).__name__
            ))
    
    def _get_days_in_month(self, target_date: datetime) -> int:
        """Get number of days in the target month."""
        try:
            return calendar.monthrange(target_date.year, target_date.month)[1]
        except ValueError as e:
            raise ValueError(ErrorMessages.INVALID_DATE.format(
                date=target_date
            )) from e
