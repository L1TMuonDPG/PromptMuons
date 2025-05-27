# L1 Muon DPG scripts (based on official NANOAOD)  
<!-- TOC -->

- [Install](#install)
- [Setup for run](#setup-for-run)
- [Run](#run)
    - [Run multiple datasets](#run-multiple-datasets)
- [Make plots](#make-plots)
    - [Make plots for each case](#make-plots-for-each-case)
    - [Make comparison plots](#make-comparison-plots)
- [Useful links](#useful-links)

<!-- TOC -->

# Install  
  
```bash
cmsrel CMSSW_14_0_1  
cd CMSSW_14_0_1/src  
cmsenv  
git clone https://github.com/yiannispar/muonDPG.git  
git checkout dev/2025
```  

# Setup for run

Generate submission and plotting scripts with the automation script:

```python
python3 automate.py -o <output_directory> [--eff] [--run] [--comparison] [--all]
```

Basic Functionality (without optional flags):
Creates scripts for:
- `eff`: Efficiency vs (pT/eta/phi) for SingleMu22 and SingleMu5.
- `misid`: Charge misidentification probability vs (pT/eta&phi) for SingleMu22.

Optional flags
- `--eff`: Include additional efficiency plots in the generated scripts.
    - `eff_22_11`: Efficiency vs (pT/eta/phi) for BMTF muons with quality and pT cuts at 12, 14 and 22 GeV, 11 GeV respectively.
    - `eff_22_15`: Efficiency vs (pT/eta/phi) for GMT muons with quality and pT cuts at 12, 8 and 22 GeV, 15 GeV respectively.
    - `eff_qual`: Efficiency vs (pT/eta/phi) for BMTF muons with pT cut at 22 GeV and quality cuts at 12, 13, 14, 15 [WIP].

- `--run`: Include plots for variables versus the run number in the generated scripts.
    - `eff_vs_run`: Efficiency vs run number for SingleMu22 [WIP].
    - `misid_vs_run`: Charge misidentification probability vs run number for SingleMu22 [WIP].

- `--comparison`: Include comparison plots for different pt and eta working points.

- `--all`: Include all additional plots (this enables both --eff and --run).

# Run  

Before submitting the jobs make sure that you have enabled the certificate for the DAS.

```bash
voms-proxy-init -voms cms 
```

```bash  
cd muonDPG/condor
./batch_submission.sh <dataset> 
```
**Notes:**
- The dataset should match the format of [DAS](https://cmsweb.cern.ch/das/), e.g. `/Muon0/Run2024F-PromptReco-v1/NANOAOD` 
- The output files will be saved in a `/files/` directory inside the specified output directory.
 

## Run multiple datasets

```bash
cd muonDPG/condor
./run_datasets.sh <dataset_list.txt>
```

# Make plots
```bash
cd muonDPG/make_plots
./make_plots.sh <era_of_dataset>
```
**Notes:**
- Output plots will be saved in a `/plots/` directory inside the specified output directory.
 
## Make plots for each case 

For finer control, you can create plots for specific cases using individual scripts created during the setup phase:

```bash
cd muonDPG/make_plots
./make_plots_<case>.sh <era_of_dataset>
```

## Make comparison plots

Work in Progress 

# Useful links

- You can find the golden json files needed in `/eos/user/c/cmsdqm/www/CAF/certification/`
