"""
Commission calculation and statistics components.
"""

from typing import Dict
from tree_components import PartnerTree, Partner
from config import Constants
from utils import MathUtils


class CommissionCalculator:
    """Calculates commissions using post-order DFS traversal."""
    
    def calculate_commissions(self, tree: PartnerTree) -> Dict[str, float]:
        """
        Calculate commissions for all partners using post-order DFS.
        
        Args:
            tree: PartnerTree to process
            
        Returns:
            Dictionary mapping partner IDs to their total commissions
            
        Time Complexity: O(n) where n is the number of partners
        Space Complexity: O(h) where h is the height of the tree
        """
        # Reset commission calculations
        self._reset_commissions(tree)
        
        # Calculate commissions using post-order traversal
        for root in tree.get_roots():
            self._calculate_subtree_commission(root)
        
        # Format output with 2 decimal precision
        return self._format_results(tree)
    
    def _reset_commissions(self, tree: PartnerTree) -> None:
        """Reset all commission values to zero."""
        for partner in tree.get_all_partners():
            partner.total_commission = 0.0
    
    def _calculate_subtree_commission(self, partner: Partner) -> float:
        """
        Calculate total commission for a partner's subtree using post-order DFS.
        
        Args:
            partner: Root of the subtree
            
        Returns:
            Total profit from this subtree (for commission calculation)
        """
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
        partner.total_commission = descendants_profit * Constants.COMMISSION_RATE
        
        return subtree_profit
    
    def _format_results(self, tree: PartnerTree) -> Dict[str, float]:
        """Format commission results with proper precision."""
        return {
            str(partner.id): MathUtils.round_currency(partner.total_commission)
            for partner in tree.get_all_partners()
        }


class TreeStatistics:
    """Calculates various statistics about the partner tree."""
    
    def get_stats(self, tree: PartnerTree) -> Dict[str, int]:
        """
        Get comprehensive statistics about the partner network.
        
        Args:
            tree: PartnerTree to analyze
            
        Returns:
            Dictionary with network statistics
        """
        return {
            'total_partners': tree.size(),
            'root_partners': len(tree.get_roots()),
            'leaf_partners': len(tree.get_leaves()),
            'max_depth': self._calculate_max_depth(tree)
        }
    
    def _calculate_max_depth(self, tree: PartnerTree) -> int:
        """Calculate maximum depth of the tree."""
        max_depth = 0
        
        for root in tree.get_roots():
            root_depth = self._calculate_depth_from_node(root)
            max_depth = max(max_depth, root_depth)
        
        return max_depth
    
    def _calculate_depth_from_node(self, partner: Partner, current_depth: int = 0) -> int:
        """
        Calculate depth starting from a specific node.
        
        Args:
            partner: Starting partner node
            current_depth: Current depth level
            
        Returns:
            Maximum depth from this node
        """
        if partner.is_leaf():
            return current_depth
        
        max_child_depth = current_depth
        for child in partner.children:
            child_depth = self._calculate_depth_from_node(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def get_level_distribution(self, tree: PartnerTree) -> Dict[int, int]:
        """
        Get distribution of partners across different levels.
        
        Args:
            tree: PartnerTree to analyze
            
        Returns:
            Dictionary mapping level to partner count
        """
        level_counts = {}
        
        for root in tree.get_roots():
            self._count_partners_by_level(root, 0, level_counts)
        
        return level_counts
    
    def _count_partners_by_level(self, partner: Partner, level: int, 
                                level_counts: Dict[int, int]) -> None:
        """Recursively count partners at each level."""
        level_counts[level] = level_counts.get(level, 0) + 1
        
        for child in partner.children:
            self._count_partners_by_level(child, level + 1, level_counts)
