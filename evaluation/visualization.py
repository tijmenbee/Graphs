import matplotlib.pyplot as plt
import seaborn as sns

from evaluation.utils import METHOD_MAPPING_ORIGINAL, METHOD_MAPPING_VARIANT

METHOD_NAME_MAP = {
    "Louvain-Variant": "CTL",
    "Louvain-Variant Leiden-Addition": "CTL\nLeiden-Addition",
    "Louvain": "Louvain",
    "Temporal Louvain": "Temporal\nLouvain"
}

sns.set_theme(style="whitegrid")

def plot_algorithms(method_mapping: dict, results_total: dict, axes, color=None, label=None):
    """
    Plot a given set of algorithm results
    """
    for method_name, ax_row in zip(method_mapping.keys(), axes):
        time_score = results_total[method_name]["time"]
        modularity_score = results_total[method_name]["modularity"]
        nmi_score = results_total[method_name]["nmi"]
        ax_row[0].errorbar(x=range(len(time_score[0])), y=time_score[0], yerr=time_score[1], color=color, capsize=5)
        ax_row[1].errorbar(x=range(len(time_score[0])), y=nmi_score[0], yerr=nmi_score[1], color=color, capsize=5)
        ax_row[2].errorbar(x=range(len(time_score[0])), y=modularity_score[0], yerr=modularity_score[1], color=color, capsize=5, label=label)
        
        method_name = METHOD_NAME_MAP[method_name]
        ax_row[0].set_ylabel(method_name, fontsize=17)
        ax_row[0].get_yaxis().set_label_coords(-0.22,0.5)
        ax_row[1].set_ylim(0,1)
        ax_row[2].set_ylim(0,1)
        for ax in ax_row:
            ax.tick_params(size=16, pad=-10)

def plot_all(results_total: dict, file_name: str):
    """
    Plot the results of the original and the variant Louvain approaches 
    """
    _, axes = plt.subplots(len(METHOD_MAPPING_ORIGINAL.keys()) + len(METHOD_MAPPING_VARIANT.keys()), 3, sharex=True, figsize=(12,10))
    axes[0][0].set_title("Time (s)", fontsize=17)
    axes[0][1].set_title("NMI", fontsize=17)
    axes[0][2].set_title("Modularity", fontsize=17)
    axes[-1][1].set_xlabel("Time step", fontsize=17)

    axes_orig = axes[:len(METHOD_MAPPING_ORIGINAL.keys())]
    axes_variant = axes[len(METHOD_MAPPING_ORIGINAL.keys()):]

    plot_algorithms(METHOD_MAPPING_ORIGINAL, results_total["original"], axes_orig, color="cyan", label=None)
    for cc_th, results in results_total.items():
        if isinstance(cc_th, str): # ignore the `original` results, only look at the variants with CC
            continue
        plot_algorithms(METHOD_MAPPING_VARIANT, results, axes_variant, color=None, label=cc_th)

    plt.legend(loc="upper center", bbox_to_anchor=(-0.65,5.33), ncols=len(results_total.keys()), fontsize=15, title="Core-Centrality Thresholds", shadow=True)
    plt.tight_layout()
    # plt.subplots_adjust(hspace=0.35)
    plt.savefig(f"{file_name}_plot.pdf", bbox_inches="tight")
    plt.show()