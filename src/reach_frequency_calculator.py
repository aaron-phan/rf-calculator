import numpy as np
from typing import Dict

class ReachFrequencyCalculator:
    def __init__(self, total_universe: int, total_impressions: int, max_reach_percent: float, 
                 global_overlap_factor: float, distributed_impressions: Dict[str, int]):
        
        self.total_universe = total_universe
        self.total_impressions = total_impressions
        self.max_reach_percent = max_reach_percent
        self.global_overlap_factor = global_overlap_factor
        self.distributed_impressions = distributed_impressions
        self.channel_reach = {}
        self.final_reach = 0
        self.average_frequency = 0

    def calculate_total_reach(self):
        raw_total_reach = sum(self.distributed_impressions.values()) * (1 - self.global_overlap_factor)
        max_possible_reach = (self.max_reach_percent / 100) * self.total_universe
        self.final_reach = min(max(0, raw_total_reach), max_possible_reach)
        return self.final_reach

    def calculate_frequency(self):
        if self.final_reach <= 0:
            return 0
        self.average_frequency = self.total_impressions / self.final_reach
        return self.average_frequency

    def run_all_calculations(self):
        self.calculate_total_reach()
        self.calculate_frequency()
        
        return {
            'final_reach': self.final_reach,
            'final_reach_percent': (self.final_reach / self.total_universe) * 100,
            'average_frequency': self.average_frequency
        }
