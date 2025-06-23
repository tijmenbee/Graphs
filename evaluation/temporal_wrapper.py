import time

from networkx import Graph
from typing import Tuple

class TemporalLouvainIterator:
    """
    Iterator wrapper to make it easier to switch methods and evaluate them in a consistent manner
    """
    def __init__(self, louvain_method: callable, limit_steps: int=None, **kwargs):
        self.louvain_method = louvain_method
        self.louvain_args = kwargs
        self.use_prev_partition = self.louvain_args.pop("prev_partition", False) # for louvain that restarts every time it should be False
        self.limit_steps = limit_steps

    def _process_temporal_graph_normal(self, temporal_graph: list) -> list:
        """
        Only evaluate algorithm performance
        """
        partition_list = []
        partition = self.louvain_method(temporal_graph[0], **self.louvain_args)
        partition_list += [partition]
        for snapshot in temporal_graph[1:self.limit_steps]:
            partition = self.louvain_method(snapshot, partition=partition, **self.louvain_args)
            partition_list += [partition]
        
        return partition_list
    
    def _time_measure_call(self, graph: Graph, partition: dict=None) -> Tuple[dict,int]:
        start_time = time.time()
        if partition is not None and not self.use_prev_partition: # applied to original Louvain and Smoothed (i.e., Temporal) Louvain
            partition = None
        partition = self.louvain_method(graph, partition=partition, **self.louvain_args)
        stop_time = time.time() - start_time

        return partition, stop_time
    
    def _process_temporal_graph_time(self, temporal_graph: list) -> Tuple[list,list]:
        """
        Evaluate algorithm performance and its running time
        """
        partition_list = []
        time_list = []
        partition, measured_time = self._time_measure_call(temporal_graph[0])

        partition_list += [partition]
        time_list += [measured_time]
        for snapshot in temporal_graph[1:self.limit_steps]:
            partition, measured_time = self._time_measure_call(snapshot, partition=partition)
            partition_list += [partition]
            time_list += [measured_time]
        
        return partition_list, time_list

    def process_temporal_graph(self, temporal_graph: list, measure_time: bool) -> Tuple[list,list]|list:
        self.limit_steps = self.limit_steps if self.limit_steps is not None else len(temporal_graph)
        if measure_time:
            results = self._process_temporal_graph_time(temporal_graph)
        else:
            results = self._process_temporal_graph_normal(temporal_graph)

        return results