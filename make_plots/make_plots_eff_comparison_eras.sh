#!/bin/bash

############ settings #############
output_dir="/eos/user/n/nplastir/Trigger/PromptMuons/DPS_2025/plots/2025/eff_comparison_eras/"
###################################

current_dir=$PWD

echo "Output dir: ${output_dir}"

mkdir -p $output_dir

cd $current_dir/../plotters/

python3 eff_comparison_eras_2025.py -o $output_dir

cd $current_dir

echo "DONE"
