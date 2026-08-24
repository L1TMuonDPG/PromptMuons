import os
import argparse

def generate_batch_submission_script(output_base_dir, include_run):
    batch_submission_content = f"""#!/bin/bash

# Initialize variables
SPLIT_RUNS=false
MIN_RUN=0
DATASET=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --split-runs)
      SPLIT_RUNS=true
      shift # past argument
      ;;
    --min-run)
      MIN_RUN=$2
      shift 2 # past argument and value
      ;;
    *)
      DATASET=$1
      shift # past argument
      ;;
  esac
done

# Check if the dataset is provided
if [ -z "$DATASET" ]; then
    echo "Usage: $0 <dataset> [--split-runs] [--min-run <run_number>]"
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
output_dir="{output_base_dir}/files/$year_run"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Fetch the list of runs for the given dataset
run_list_file="$output_dir/runs_${{year_run}}.txt"
echo "Fetching run list..."
dasgoclient -query="run dataset=$dataset" > "$run_list_file"
echo "Run list saved to: $run_list_file"
# -------------------------

if [ "$SPLIT_RUNS" = true ]; then
    echo "Splitting submission by run number (Threshold >= $MIN_RUN)..."
    
    # Read the run list file line by line
    while IFS= read -r run; do
        # Skip empty lines
        [ -z "$run" ] && continue
        
        # Check against threshold
        if [ "$MIN_RUN" -gt 0 ] && [ "$run" -lt "$MIN_RUN" ]; then
            echo "Skipping run $run (below threshold $MIN_RUN)"
            continue
        fi
        
        echo "----------------------------------------"
        echo "Submitting jobs for run: $run"
        
        # Create a run-specific output directory
        run_out_dir="$output_dir/$run"
        mkdir -p "$run_out_dir"
        
        # Execute the python script for THIS run specifically
        python3 run_nano.py --dataset "$dataset" --exec eff_all.py --output "$run_out_dir/eff/" --jobFlav testmatch --submitName eff_${{year_run}}_${{run}}.sh --runs "$run" --submit
        sleep 2
        
        python3 run_nano.py --dataset "$dataset" --exec misid.py --output "$run_out_dir/misid/" --jobFlav testmatch --submitName misid_${{year_run}}_${{run}}.sh --runs "$run" --submit 
    done < "$run_list_file"

else
    echo "Submitting jobs for the entire dataset (all runs combined)..."
    
    # Submit the jobs to condor
    python3 run_nano.py --dataset "$dataset" --exec eff_all.py --output "$output_dir/eff/" --jobFlav testmatch --submitName eff_${{year_run}}.sh --submit

    sleep 5

    python3 run_nano.py --dataset "$dataset" --exec misid.py --output "$output_dir/misid/" --jobFlav testmatch --submitName misid_${{year_run}}.sh --submit 
"""

    if include_run:
        batch_submission_content += f"""
    sleep 5

    python3 run_nano.py --dataset "$dataset" --exec eff_vs_run.py --output "$output_dir/eff_vs_run/" --jobFlav testmatch --submitName eff_vs_run_${{year_run}}.sh --submit

    sleep 5

    python3 run_nano.py --dataset "$dataset" --exec misid_vs_run.py --output "$output_dir/misid_vs_run/" --jobFlav testmatch --submitName misid_vs_run_${{year_run}}.sh --submit
"""

    batch_submission_content += "\nfi\n"

    script_path = "./condor/batch_submission.sh"
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as file:
        file.write(batch_submission_content)

    os.chmod(script_path, 0o755)
    print(f"Generated {script_path}")


def generate_make_plots_script(output_base_dir, include_run):
    make_plots_content = f"""#!/bin/bash

MIN_RUN=0
era=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --min-run)
      MIN_RUN=$2
      shift 2
      ;;
    *)
      if [ -z "$era" ]; then
          era=$1
      fi
      shift
      ;;
  esac
done

if [ -z "$era" ]; then
    echo "Usage: $0 <era> [--min-run <run_number>]"
    exit 1
fi

############ settings #############
root_files_dir="{output_base_dir}/files/$era"
output_dir="{output_base_dir}/plots/$era"
current_dir=$PWD
###################################

echo "Root files dir: ${{root_files_dir}}"
echo "Output dir: ${{output_dir}}"
echo "Dataset legend: ${{era}}"
[ "$MIN_RUN" -gt 0 ] && echo "Filtering for runs >= $MIN_RUN"

# Detect all valid 6-digit run directories
VALID_RUNS=""
for d in $(find $root_files_dir -mindepth 1 -maxdepth 1 -type d 2>/dev/null); do
    b=$(basename $d)
    if [[ $b =~ ^[0-9]{{6}}$ ]]; then
        if [ "$MIN_RUN" -le 0 ] || [ "$b" -ge "$MIN_RUN" ]; then
            VALID_RUNS="$VALID_RUNS $b"
        fi
    fi
done

############ Efficiency #############
GLOBAL_EFF_MERGE=""

# 1. Per-run Efficiency (Basic eff_all_plots only)
for run in $VALID_RUNS; do
    run_in="$root_files_dir/$run/eff"
    run_out="$output_dir/$run"
    
    if [ -d "$run_in" ]; then
        echo ">>> Processing Efficiency for Run $run"
        mkdir -p $run_out/eff/
        
        cd $run_in
        rm -f merged_total.root
        run_files=$(find . -maxdepth 1 -name "*.root" ! -name "merged_total.root")
        if [ -n "$run_files" ]; then
            hadd -j 20 merged_total.root $run_files
            GLOBAL_EFF_MERGE="$GLOBAL_EFF_MERGE $run_in/merged_total.root"
            
            cd $current_dir/../plotters/
            python3 eff_all_plots.py -o $run_out/eff/ -i $run_in/ --legend "${{era}}_${{run}}"
        fi
    fi
done

# 2. Global Efficiency (All plots)
echo ">>> Processing Global Efficiency for ${{era}}"
mkdir -p $root_files_dir/eff/
mkdir -p $output_dir/eff/ $output_dir/eff_22_15/ $output_dir/eff_22_11/ $output_dir/eff_qual/ $output_dir/eff_22_15_7_3/ $output_dir/eff_comparison_Qual12/ $output_dir/eff_comparison_Qual8/

# Catch flat files if script was run without split-runs
flat_eff_files=$(find $root_files_dir/eff -maxdepth 1 -name "*.root" ! -name "merged_total.root" 2>/dev/null)
GLOBAL_EFF_MERGE="$GLOBAL_EFF_MERGE $flat_eff_files"

cd $root_files_dir/eff/
rm -f merged_total.root
if [ -n "$(echo $GLOBAL_EFF_MERGE | xargs)" ]; then
    hadd -j 20 merged_total.root $GLOBAL_EFF_MERGE
    
    cd $current_dir/../plotters/
    python3 eff_all_plots.py -o $output_dir/eff/ -i $root_files_dir/eff/ --legend "$era"
    python3 eff_22_15_plots.py -o $output_dir/eff_22_15/ -i $root_files_dir/eff/ --legend "$era"
    python3 eff_22_11_plots.py -o $output_dir/eff_22_11/ -i $root_files_dir/eff/ --legend "$era"
    python3 eff_qual_plots.py -o $output_dir/eff_qual/ -i $root_files_dir/eff/ --legend "$era"
    python3 eff_22_15_7_3_plots.py -o $output_dir/eff_22_15_7_3/ -i $root_files_dir/eff/ --legend "$era"
    python3 eff_comparison_Qual12_plots.py -o $output_dir/eff_comparison_Qual12/ -i $root_files_dir/eff/ --legend "$era"
    python3 eff_comparison_Qual8_plots.py -o $output_dir/eff_comparison_Qual8/ -i $root_files_dir/eff/ --legend "$era"
fi

############ Charge misidentification #############
GLOBAL_MISID_MERGE=""

# 1. Per-run Misid
for run in $VALID_RUNS; do
    run_in="$root_files_dir/$run/misid"
    run_out="$output_dir/$run/misid"
    
    if [ -d "$run_in" ]; then
        echo ">>> Processing Misid for Run $run"
        mkdir -p $run_out
        cd $run_in
        rm -f merged_total.root
        run_files=$(find . -maxdepth 1 -name "*.root" ! -name "merged_total.root")
        if [ -n "$run_files" ]; then
            hadd -j 20 merged_total.root $run_files
            GLOBAL_MISID_MERGE="$GLOBAL_MISID_MERGE $run_in/merged_total.root"
            
            cd $current_dir/../plotters/
            python3 misid_plots.py -o $run_out/ -i $run_in/ --legend "${{era}}_${{run}}"
        fi
    fi
done

# 2. Global Misid
echo ">>> Processing Global Misid for ${{era}}"
mkdir -p $root_files_dir/misid/
mkdir -p $output_dir/misid/

flat_misid_files=$(find $root_files_dir/misid -maxdepth 1 -name "*.root" ! -name "merged_total.root" 2>/dev/null)
GLOBAL_MISID_MERGE="$GLOBAL_MISID_MERGE $flat_misid_files"

cd $root_files_dir/misid/
rm -f merged_total.root
if [ -n "$(echo $GLOBAL_MISID_MERGE | xargs)" ]; then
    hadd -j 20 merged_total.root $GLOBAL_MISID_MERGE
    cd $current_dir/../plotters/
    python3 misid_plots.py -o $output_dir/misid/ -i $root_files_dir/misid/ --legend "$era"
fi
"""
    if include_run:
        make_plots_content += f"""
############ Efficiency vs Run #############
# (Global only - not relevant for individual runs)
echo ">>> Processing Global Efficiency vs Run"
mkdir -p $output_dir/eff_vs_run/
mkdir -p $root_files_dir/eff_vs_run/
cd $root_files_dir/eff_vs_run/

rm -f merged_total.root
run_files=$(find . -maxdepth 1 -name "*.root" ! -name "merged_total.root")
if [ -n "$run_files" ]; then
    hadd -j 20 merged_total.root $run_files
    cd $current_dir/../plotters/
    python3 eff_vs_run_plots.py -o $output_dir/eff_vs_run/ -i $root_files_dir/eff_vs_run/ --legend "$era" 
fi

############ Charge misidentification vs run #############
# (Global only - not relevant for individual runs)
echo ">>> Processing Global Misid vs Run"
mkdir -p $output_dir/misid_vs_run/
mkdir -p $root_files_dir/misid_vs_run/
cd $root_files_dir/misid_vs_run/

rm -f merged_total.root
run_files=$(find . -maxdepth 1 -name "*.root" ! -name "merged_total.root")
if [ -n "$run_files" ]; then
    hadd -j 20 merged_total.root $run_files
    cd $current_dir/../plotters/
    python3 misid_vs_run_plots.py -o $output_dir/misid_vs_run/ -i $root_files_dir/misid_vs_run/ --legend "$era"
fi
"""
    script_path = "./make_plots/make_plots.sh"
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as file:
        file.write(make_plots_content)

    os.chmod(script_path, 0o755)
    print(f"Generated {script_path}")


def generate_make_plots_scripts(output_base_dir, include_run):
    options= ["eff", "misid"]
    if include_run:
        options+=["eff_vs_run", "misid_vs_run"]
        
    for option in options:
        make_plots_content = f"""#!/bin/bash
MIN_RUN=0
era=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --min-run)
      MIN_RUN=$2
      shift 2
      ;;
    *)
      if [ -z "$era" ]; then
          era=$1
      fi
      shift
      ;;
  esac
done

if [ -z "$era" ]; then
    echo "Usage: $0 <era> [--min-run <run_number>]"
    exit 1
fi

############ settings #############
root_files_dir="{output_base_dir}/files/$era"
output_dir="{output_base_dir}/plots/$era"
current_dir=$PWD
###################################

"""
        if option in ["eff", "misid"]:
            make_plots_content += f"""
VALID_RUNS=""
for d in $(find $root_files_dir -mindepth 1 -maxdepth 1 -type d 2>/dev/null); do
    b=$(basename $d)
    if [[ $b =~ ^[0-9]{{6}}$ ]]; then
        if [ "$MIN_RUN" -le 0 ] || [ "$b" -ge "$MIN_RUN" ]; then
            VALID_RUNS="$VALID_RUNS $b"
        fi
    fi
done

GLOBAL_MERGE=""

# 1. Per-run
for run in $VALID_RUNS; do
    run_in="$root_files_dir/$run/{option}"
    run_out="$output_dir/$run/{option}"
    
    if [ -d "$run_in" ]; then
        echo ">>> Processing {option} for Run $run"
        mkdir -p $run_out
        cd $run_in
        rm -f merged_total.root
        run_files=$(find . -maxdepth 1 -name "*.root" ! -name "merged_total.root")
        if [ -n "$run_files" ]; then
            hadd -j 20 merged_total.root $run_files
            GLOBAL_MERGE="$GLOBAL_MERGE $run_in/merged_total.root"
            
            cd $current_dir/../plotters/
            python3 {option}_plots.py -o $run_out/ -i $run_in/ --legend "${{era}}_${{run}}"
        fi
    fi
done

# 2. Global
echo ">>> Processing Global {option} for ${{era}}"
mkdir -p $root_files_dir/{option}/
mkdir -p $output_dir/{option}/

flat_files=$(find $root_files_dir/{option} -maxdepth 1 -name "*.root" ! -name "merged_total.root" 2>/dev/null)
GLOBAL_MERGE="$GLOBAL_MERGE $flat_files"

cd $root_files_dir/{option}/
rm -f merged_total.root
if [ -n "$(echo $GLOBAL_MERGE | xargs)" ]; then
    hadd -j 20 merged_total.root $GLOBAL_MERGE
    cd $current_dir/../plotters/
    python3 {option}_plots.py -o $output_dir/{option}/ -i $root_files_dir/{option}/ --legend "$era"
fi
"""
        else:
            # Logic for eff_vs_run and misid_vs_run (Global only)
            make_plots_content += f"""
echo ">>> Processing Global {option} for ${{era}}"
mkdir -p $root_files_dir/{option}/
mkdir -p $output_dir/{option}/

cd $root_files_dir/{option}/
rm -f merged_total.root
run_files=$(find . -maxdepth 1 -name "*.root" ! -name "merged_total.root")
if [ -n "$run_files" ]; then
    hadd -j 20 merged_total.root $run_files
    cd $current_dir/../plotters/
    python3 {option}_plots.py -o $output_dir/{option}/ -i $root_files_dir/{option}/ --legend "$era"
fi
"""
        make_plots_content += "\necho \"DONE\"\n"

        script_path = f"./make_plots/make_plots_{option}.sh"
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, "w") as file:
            file.write(make_plots_content)

        os.chmod(script_path, 0o755)
        print(f"Generated {script_path}")

def generate_make_comparison_plots_script(output_base_dir):
    make_plots_content = f"""#!/bin/bash

era1="$1"
era2="$2"

############ settings #############
root_files_dir1="{output_base_dir}/files/$era1"
root_files_dir2="{output_base_dir}/files/$era2"
output_dir="{output_base_dir}/plots/${{era1}}vs${{era2}}"
###################################

current_dir=$PWD

echo "Root files dir: ${{root_files_dir1}} and ${{root_files_dir2}}"
echo "Output dir: ${{output_dir}}"
echo "Dataset legend: ${{era1}} and ${{era2}}"

mkdir -p $output_dir/eff_comparison/

cd $current_dir/../plotters/

python3 eff_comparison_plots.py -o $output_dir/eff_comparison/ -i1 $root_files_dir1/eff/ -i2 $root_files_dir2/eff/ --legend1 $era1 --legend2 $era2

cd $current_dir

"""
    script_path = "./make_plots/make_comparison_plots_eff.sh"
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as file:
        file.write(make_plots_content)

    os.chmod(script_path, 0o755)
    print(f"Generated {script_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate files for automated creation of DPG plots")
    parser.add_argument("-o", "--output", required=True, type=str, help="Output directory for the DPG files and plots")
    parser.add_argument("--run", required=False, default=False, action='store_true', help="Include additional plots for variables vs the run number")
    args = parser.parse_args()

    # Remove trailing slash from output directory if present
    output_base_dir = args.output.rstrip("/")

    # Generate scripts
    generate_batch_submission_script(output_base_dir, args.run)
    generate_make_plots_script(output_base_dir, args.run)
    generate_make_plots_scripts(output_base_dir, args.run)
    generate_make_comparison_plots_script(output_base_dir)