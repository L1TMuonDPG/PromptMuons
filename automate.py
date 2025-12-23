import os
import argparse

def generate_batch_submission_script(output_base_dir, include_run):
    batch_submission_content = f"""#!/bin/bash

# Check if the dataset is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

dataset="$1"

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

# Submit the jobs to condor
python3 run_nano.py --dataset "$dataset" --exec eff_all.py --output "$output_dir/eff/" --jobFlav testmatch --submitName eff_${{year_run}}.sh --submit

sleep 5

python3 run_nano.py --dataset "$dataset" --exec misid.py --output "$output_dir/misid/" --jobFlav testmatch --submitName misid_${{year_run}}.sh --submit 
"""
     
    if include_run:
        batch_submission_content +=f"""
sleep 5

python3 run_nano.py --dataset "$dataset" --exec eff_vs_run.py --output "$output_dir/eff_vs_run/" --jobFlav testmatch --submitName eff_vs_run_${{year_run}}.sh --submit

sleep 5

python3 run_nano.py --dataset "$dataset" --exec misid_vs_run.py --output "$output_dir/misid_vs_run/" --jobFlav testmatch --submitName misid_vs_run_${{year_run}}.sh --submit
"""
    script_path = "./condor/batch_submission.sh"
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as file:
        file.write(batch_submission_content)

    os.chmod(script_path, 0o755)
    print(f"Generated {script_path}")


def generate_make_plots_script(output_base_dir, include_run):
    make_plots_content = f"""#!/bin/bash

# Check if the era is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <era>"
    exit 1
fi

era="$1"

############ settings #############
root_files_dir="{output_base_dir}/files/$era"
output_dir="{output_base_dir}/plots/$era"
###################################

current_dir=$PWD

echo "Root files dir: ${{root_files_dir}}"
echo "Output dir: ${{output_dir}}"
echo "Dataset legend: ${{era}}"

mkdir -p $output_dir

############ Efficiency #############
mkdir -p $output_dir/eff/
mkdir -p $output_dir/eff_22_15/
mkdir -p $output_dir/eff_22_11/
mkdir -p $output_dir/eff_qual/
mkdir -p $output_dir/eff_22_15_7_3/
mkdir -p $output_dir/eff_comparison_Qual12/
mkdir -p $output_dir/eff_comparison_Qual8/

cd $root_files_dir/eff/

rm -rf merged_total.root
hadd merged_total.root *.root

cd $current_dir/../plotters/

python3 eff_plots.py -o $output_dir/eff/ -i $root_files_dir/eff/ --legend "$era"

python3 eff_22_15_plots.py -o $output_dir/eff_22_15/ -i $root_files_dir/eff/ --legend "$era"

python3 eff_22_11_plots.py -o $output_dir/eff_22_11/ -i $root_files_dir/eff/ --legend "$era"

python3 eff_qual_plots.py -o $output_dir/eff_qual/ -i $root_files_dir/eff/ --legend "$era"

python3 eff_22_15_7_3_plots.py -o $output_dir/eff_22_15_7_3/ -i $root_files_dir/eff/ --legend "$era"

python3 eff_comparison_Qual12_plots.py -o $output_dir/eff_comparison_Qual12/ -i $root_files_dir/eff/ --legend "$era"

python3 eff_comparison_Qual8_plots.py -o $output_dir/eff_comparison_Qual8/ -i $root_files_dir/eff/ --legend "$era"

############ Charge misidentification #############
mkdir -p $output_dir/misid/
cd $root_files_dir/misid/

rm -rf merged_total.root
hadd merged_total.root *.root

cd $current_dir/../plotters/

python3 misid_plots.py -o $output_dir/misid/ -i $root_files_dir/misid/ --legend "$era"

cd $current_dir

"""
    if include_run:
        make_plots_content += f"""
############ Efficiency vs Run #############
mkdir -p $output_dir/eff_vs_run/
cd $root_files_dir/eff_vs_run/

rm -rf merged_total.root
hadd merged_total.root *.root

cd $current_dir/../plotters/

python3 eff_vs_run_plots.py -o $output_dir/eff_vs_run/ -i $root_files_dir/eff_vs_run/ --legend "$era" 

############ Charge misidentification vs run #############
mkdir -p $output_dir/misid_vs_run/
cd $root_files_dir/misid_vs_run/

rm -rf merged_total.root
hadd merged_total.root *.root

cd $current_dir/../plotters/

python3 misid_vs_run_plots.py -o $output_dir/misid_vs_run/ -i $root_files_dir/misid_vs_run/ --legend "$era"
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
# Check if the era is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <era>"
    exit 1
fi

era="$1"

############ settings #############
root_files_dir="{output_base_dir}/files/$era/{option}/"
output_dir="{output_base_dir}/plots/$era/{option}/"
###################################

current_dir=$PWD

echo "Root files dir: ${{root_files_dir}}"
echo "Output dir: ${{output_dir}}"
echo "Dataset legend: ${{era}}"

mkdir -p $output_dir

cd $root_files_dir

rm -rf merged_total.root
hadd merged_total.root *.root

cd $current_dir/../plotters/

python3 {option}_plots.py -o $output_dir -i $root_files_dir --legend "$era"

cd $current_dir

echo "DONE"
"""
    
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
