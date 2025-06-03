import time
from networkx import Graph
from typing import Tuple

class TemporalLouvainIterator:
    def __init__(self, louvain_method: callable, **kwargs):
        self.louvain_method = louvain_method
        self.louvain_args = kwargs

    def _process_temporal_graph_normal(self, temporal_graph: list) -> list:
        partition_list = []
        partition = self.louvain_method(temporal_graph[0], **self.louvain_args)
        partition_list += [partition]
        for snapshot in temporal_graph[1:]:
            partition = self.louvain_method(snapshot, partition=partition, **self.louvain_args)
            partition_list += [partition]
        
        return partition_list
    
    def _time_measure_call(self, graph: Graph) -> ...:
        start_time = time.time()
        partition = self.louvain_method(graph, **self.louvain_args)
        stop_time = time.time() - start_time

        return partition, stop_time
    
    def _process_temporal_graph_time(self, temporal_graph: list) -> Tuple[list, list]:
        partition_list = []
        time_list = []
        partition, measured_time = self._time_measure_call(temporal_graph[0])

        partition_list += [partition]
        time_list += [measured_time]
        for snapshot in temporal_graph[1:]:
            partition, measured_time = self._time_measure_call(snapshot)
            partition_list += [partition]
            time_list += [measured_time]
        
        return partition_list, time_list

    def process_temporal_graph(self, temporal_graph: list, measure_time: bool) -> Tuple[list, list]|list:
        if measure_time:
            results = self._process_temporal_graph_time(temporal_graph)
        else:
            results = self._process_temporal_graph_normal(temporal_graph)

        return results