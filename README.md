# Employing a Modified Louvain Algorithm for Dynamic Community Detection in Large Temporal Graphs

Eduard-Raul Kontos, Tijmen Oliehoek

---

## Environment Setup

In order to recreate our experimental setup, kindly install the necessary dependencies found in `requirements.txt`; you can create a virtual environment and install them as follows:
```
python -m venv ./venv/<env>
source ./venv/<env>/bin/activate
pip install -r requirements.txt
```

## Repository Structure

Our repository is structured as follows:
* `data_generation`: C++ code to generate synthetic dynamic networks, from [Greene et al.](https://www.researchgate.net/publication/221273637_Tracking_the_Evolution_of_Communities_in_Dynamic_Social_Networks)
* `data_stackoverflow`: directory containing the JSON files obtained following the preprocessing performed as described in the paper.
* `dyn_graph`: the actual synthetic network data, split into files per time step.
* `evaluation`: all of the necessary scripts and notebooks to run the evaluation, create the lineplots, and perform statistical tests (i.e., one-sided Wilcoxon signed-rank test).
* `louvain_variant`: contains the modified Louvain algorithms for CLT (`louvain_variant.py`) and CLT Leiden-Addition (`louvain_variant_leiden_addition.py`), alongside all of the necessary utilities.
* the remaining files were made to recreate the experimental environment and to allow anyone to easily start and replicate our results.

## Running Experiments

There are two methods to (re-)run an experiment:
1) run the individual Python script `run_eval.py`, \
which has flags that can be used for specific effects:
* `--data_path` (mandatory): the path to the synthetic network;
* `--load_results` (optional): if the results for an experiment are already available (in the form of a `pickle` file), then you can opt to simply load the results and create the lineplots.
* `--num_t` (optional): how many time steps to include in the evaluation; if not specified, all available time steps will be considered.
* `--num_seeds` (optional; 1<= num_seeds <= 10): how many re-runs to perform and to average over.

2) run the Bash script `run_total_eval.sh`, \
which will run **all** experiments on **all** synthetic networks. 

You can include the flag `--load_results` to only load the results for the synthetic networks, but only if they exist.