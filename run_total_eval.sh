# this script will ALWAYS load all of the results OR will compute them from scratch

path="dyn_graph"
datasets=(
    # "5_250_10_20_02_01" # this is a test dataset, only to see if the code is working as intended
    "100_5000_20_02_02" "100_5000_20_02_05"
)
load_results=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --load_results) load_results=true ;;
    esac
    shift
done

for data in ${datasets[@]}; do
    echo "===============CURRENT DATASET: $data==============="
    if [ $load_results = true ]; then
        python run_eval.py --data_path $path/$data --load_results
    else
        python run_eval.py --data_path $path/$data
    fi
done