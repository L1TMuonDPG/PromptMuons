#!/bin/bash

# Initialize variables
SPLIT_RUNS=false
DATASET=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --split-runs)
      SPLIT_RUNS=true
      shift # past argument
      ;;
    *)
      DATASET=$1
      shift # past argument
      ;;
  esac
done

# Check if the dataset is provided
if [ -z "$DATASET" ]; then
    echo "Usage: $0 <dataset> [--split-runs]"
    exit 1
fi

dataset="$DATASET"

# Extract the year and run number from the dataset path
year_run=$(echo "$dataset" | grep -oP '(?<=Run)([0-9]+[A-Z])' | head -1)

# Check if the year and run number are extracted successfully
if [ -z "$year_run" ]; then
    echo "Error: Unable to extract year and run number from the dataset path."
    exit 1
fi

# Construct the output directory path
output_dir="/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/Runs_2026/files/$year_run"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Fetch the list of runs for the given dataset
run_list_file="$output_dir/runs_${year_run}.txt"
echo "Fetching run list..."
dasgoclient -query="run dataset=$dataset" > "$run_list_file"
echo "Run list saved to: $run_list_file"
# -------------------------

if [ "$SPLIT_RUNS" = true ]; then
    echo "Splitting submission by run number..."
    
    # Read the run list file line by line
    while IFS= read -r run; do
        # Skip empty lines
        [ -z "$run" ] && continue
        
        echo "----------------------------------------"
        echo "Submitting jobs for run: $run"
        
        # Create a run-specific output directory
        run_out_dir="$output_dir/$run"
        mkdir -p "$run_out_dir"
        
        # Execute the python script for THIS run specifically
        python3 run_nano.py --dataset "$dataset" --exec eff_all.py --output "$run_out_dir/eff/" --jobFlav testmatch --submitName eff_${year_run}_${run}.sh --runs "$run" --submit
        sleep 1
        
        python3 run_nano.py --dataset "$dataset" --exec misid.py --output "$run_out_dir/misid/" --jobFlav testmatch --submitName misid_${year_run}_${run}.sh --runs "$run" --submit 
        sleep 1
    done < "$run_list_file"

else
    echo "Submitting jobs for the entire dataset (all runs combined)..."
    
    # Submit the jobs to condor (Original behavior)
    python3 run_nano.py --dataset "$dataset" --exec eff_all.py --output "$output_dir/eff/" --jobFlav testmatch --submitName eff_${year_run}.sh --submit
    sleep 5

    python3 run_nano.py --dataset "$dataset" --exec misid.py --output "$output_dir/misid/" --jobFlav testmatch --submitName misid_${year_run}.sh --submit 
    sleep 5

    python3 run_nano.py --dataset "$dataset" --exec eff_vs_run.py --output "$output_dir/eff_vs_run/" --jobFlav testmatch --submitName eff_vs_run_${year_run}.sh --submit
    sleep 5

    python3 run_nano.py --dataset "$dataset" --exec misid_vs_run.py --output "$output_dir/misid_vs_run/" --jobFlav testmatch --submitName misid_vs_run_${year_run}.sh --submit
fi