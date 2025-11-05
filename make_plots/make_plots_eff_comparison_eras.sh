#!/bin/bash

############ settings #############
output_dir="/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2025/plots/2025/eff_comparison/"
###################################

current_dir=$PWD

echo "Output dir: ${output_dir}"

mkdir -p $output_dir

cd $current_dir/../plotters/

python3 eff_comparison_eras.py -o $output_dir

cd $current_dir

echo "DONE"
