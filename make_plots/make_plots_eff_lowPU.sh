#!/bin/bash
# Check if the era is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <era>"
    exit 1
fi

era="$1"

############ settings #############
root_files_dir="/eos/user/n/nplastir/Trigger/PromptMuons/01_12/files/$era/eff/"
output_dir="/eos/user/n/nplastir/Trigger/PromptMuons/01_12/plots/$era/eff/"
###################################

current_dir=$PWD

echo "Root files dir: ${root_files_dir}"
echo "Output dir: ${output_dir}"
echo "Dataset legend: ${era}"

mkdir -p $output_dir

cd $root_files_dir

rm -rf merged_total.root
hadd -j 20 merged_total.root *.root

cd $current_dir/../plotters/

python3 eff_plots_lowPU.py -o $output_dir -i $root_files_dir --legend "$era"

cd $current_dir

echo "DONE"
