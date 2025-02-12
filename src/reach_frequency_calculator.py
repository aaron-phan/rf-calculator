import numpy as np
from typing import Dict, Tuple

class ReachFrequencyCalculator:
    def __init__(self, total_universe: int, total_impressions: int, max_reach_percent: float,
                 global_overlap_factor: float, distributed_impressions: Dict[str, int],
                 channel_penetration: Dict[str, float], efficiency_factors: Dict[str, float]):
        self.total_universe = total_universe
        self.total_impressions = total_impressions
        self.max_reach_percent = max_reach_percent
        self.global_overlap_factor = global_overlap_factor
        self.distributed_impressions = distributed_impressions
        self.channel_penetration = channel_penetration
        self.efficiency_factors = efficiency_factors
        self.channel_reach = {}
        self.channel_contributions = {}
        self.final_reach = 0
        self.average_frequency = 0
        self.effective_reach = {}

    def calculate_channel_reach(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        total_channel_reach = 0
        for channel, impressions in self.distributed_impressions.items():
            penetration = self.channel_penetration.get(channel, 0)
            max_possible_reach = penetration * self.total_universe
            reach = max_possible_reach * (1 - np.exp(-impressions / max_possible_reach))
            self.channel_reach[channel] = min(reach, max_possible_reach)
            total_channel_reach += reach

        if total_channel_reach > 0:
            for channel, reach in self.channel_reach.items():
                self.channel_contributions[channel] = (reach / total_channel_reach) * 100
        return self.channel_reach, self.channel_contributions

    def calculate_total_reach(self) -> float:
        self.final_reach = sum(self.channel_reach.values()) * (1 - self.global_overlap_factor)
        self.final_reach = min(self.final_reach, (self.max_reach_percent / 100) * self.total_universe)
        return self.final_reach

    def calculate_frequency(self) -> float:
        self.average_frequency = self.total_impressions / max(1, self.final_reach)
        return self.average_frequency

    def calculate_effective_reach(self, max_frequency: int = 6) -> Dict[str, float]:
        x = 1 / max(1.0, self.average_frequency)
        reach_percent = (self.final_reach / self.total_universe) * 100
        self.effective_reach = {f"{i}+": reach_percent * (1 - x) for i in range(2, max_frequency + 1)}
        return self.effective_reach

    def run_all_calculations(self) -> Dict:
        self.calculate_channel_reach()
        self.calculate_total_reach()
        self.calculate_frequency()
        self.calculate_effective_reach()
        return {
            'channel_contributions': self.channel_contributions,
            'final_reach': self.final_reach,
            'final_reach_percent': (self.final_reach / self.total_universe) * 100,
            'average_frequency': self.average_frequency,
            'effective_reach': self.effective_reach
        }
