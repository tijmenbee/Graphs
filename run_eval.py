import numpy as np
import os
import pickle

from argparse import ArgumentParser, BooleanOptionalAction
from collections import defaultdict
from evaluation.load_graphs import load_dyn_data
from evaluation.temporal_wrapper import TemporalLouvainIterator
from evaluation.utils import compute_nmi, compute_modularity
from evaluation.utils import METHOD_MAPPING_ORIGINAL, METHOD_MAPPING_VARIANT
from evaluation.utils import return_def_list
from evaluation.visualization import plot_all
from tqdm import tqdm

np.random.seed(42)
SEEDS = [35161, 58086, 39824, 41633, 45775, 16416, 27860, 57299, 34548, 29213]
RESULTS_PATH = "evaluation/results"
CC_THRESHOLDS = np.linspace(0,1,5).round(1)

def eval_timesteps(temporal_graph: list, core_threshold: float=0.8, limit_steps: int=None, evaluate_cc: bool=True, random_state: int=42) -> dict:
    """
    Perform evaluation (and measure Time (s), Modularity, and NMI) on all specified subset of methods with the given parameters
    """
    results_dict = {}
    paras = {
        "random_state":random_state, 
        "core_threshold": core_threshold,
        "prev_partition": True
    }
    
    iterator_methods = tqdm(METHOD_MAPPING_VARIANT.items() if evaluate_cc else METHOD_MAPPING_ORIGINAL.items(), desc="")
    for name, method in iterator_methods:
        iterator_methods.set_description(name)
        parameters = paras.copy()
        if "variant" not in name.lower():
            parameters.pop("core_threshold")
        if "temporal" not in name.lower() and "variant" not in name.lower():
            parameters.pop("prev_partition")

        iterator = TemporalLouvainIterator(method, limit_steps=limit_steps, **parameters)
        partitions, time_list = iterator.process_temporal_graph(temporal_graph, measure_time=True)
        results_dict[name] = {
            "partitions": partitions, 
            "time": time_list,
            "nmi": compute_nmi(temporal_graph, partitions),
            "modularity": compute_modularity(temporal_graph, partitions)
        }

    return results_dict

def run_eval(data_path: str, NUM_TIMESTEPS: int=None) -> dict:
    """
    Perform evaluation on all methods on the given temporal/dynamic graph
    """
    temporal_graph = load_dyn_data(data_path)
    
    results_total = {
        cc_th.item(): defaultdict(return_def_list) for cc_th in np.linspace(0,1,5).round(1)
    }
    results_total["original"] = defaultdict(return_def_list)

    for random_state in SEEDS:
        results = eval_timesteps(temporal_graph[:], core_threshold=None, limit_steps=NUM_TIMESTEPS, evaluate_cc=False, random_state=random_state)
        for method_name, method_result in results.items():
            for result_type, result_value in method_result.items():
                results_total["original"][method_name][result_type] += [result_value]

        for cc in CC_THRESHOLDS:
            results = eval_timesteps(temporal_graph[:], core_threshold=cc, limit_steps=NUM_TIMESTEPS, evaluate_cc=True, random_state=random_state)
            for method_name, method_result in results.items():
                for result_type, result_value in method_result.items():
                    results_total[cc][method_name][result_type] += [result_value]

    for cc_th, results in results_total.items():
        for method_name, all_results in results.items():
            for result_type, result_value in all_results.items():
                if result_type == "partitions":
                    continue
                results_total[cc_th][method_name][result_type] = (np.mean(result_value,axis=0), np.std(result_value, axis=0))
                
    file_name = f"results_{data_path.split("/")[-1]}_T{NUM_TIMESTEPS}.pickle" if NUM_TIMESTEPS is not None \
                else f"results_{data_path.split("/")[-1]}.pickle"
    pickle.dump(results_total, open(os.path.join(RESULTS_PATH,file_name), "wb"))

    return results_total

if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--data_path", type=str)
    arg_parser.add_argument("--load_results", action=BooleanOptionalAction)
    arg_parser.add_argument("--num_t", type=int, default=None) # evaluate on all available time steps if None
    arg_parser.add_argument("--num_seeds", type=int, default=len(SEEDS)) # how many rounds of evaluation to do

    args = arg_parser.parse_args()
    load_results = args.load_results
    data_path = args.data_path
    NUM_TIMESTEPS = args.num_t
    num_seeds = args.num_seeds
    SEEDS = SEEDS[:num_seeds]

    if not load_results:
        results_total = run_eval(data_path, NUM_TIMESTEPS=NUM_TIMESTEPS)

    file_name = f"results_{data_path.split("/")[-1]}_T{NUM_TIMESTEPS}.pickle" if NUM_TIMESTEPS is not None \
                else f"results_{data_path.split("/")[-1]}.pickle"
    results_total = pickle.load(open(os.path.join(RESULTS_PATH,file_name), "rb"))

    fig_name = data_path.split("/")[-1] # use the name of the folder (i.e., specific dataset) as the name of the plot
    plot_all(results_total, os.path.join(RESULTS_PATH,fig_name + (f"_T{NUM_TIMESTEPS}" if NUM_TIMESTEPS is not None else "")))
