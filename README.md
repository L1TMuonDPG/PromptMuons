# L1 Muon DPG scripts (based on official NANOAOD)  
<!-- TOC -->

- [Install](#install)
- [Setup for run](#setup-for-run)
- [Run](#run)
    - [Run multiple datasets](#run-multiple-datasets)
- [Make plots](#make-plots)
    - [Make plots for each case](#make-plots-for-each-case)
    - [Make comparison plots](#make-comparison-plots)
- [Working points](#working-points)
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

```bash
cd muonDPG/make_plots
./make_comparison_plots_eff.sh <era_of_1st_dataset> <era_of_2nd_dataset>
```

The ratio plots will be generated with the 1st dataset being the numerator and the 2nd the denominator.
# Working points 

| Working Point | L1 pT cut   | Quality cut|        |Track Finders | Abs(Eta)   |
| :---          |    :----:   |       ---: |        | :---         |:----:      |
| L1Mu22_15     | 22 GeV      | 15         |        | uGMT         |[0.00, 2.40]|
| L1Mu26_14     | 26 GeV      | 14         |        | BMTF         |[0.00, 0.83]|
| L1Mu22_14     | 22 GeV      | 14         |        | OMTF         |[0.83, 1.24]|
| L1Mu20_14     | 20 GeV      | 14         |        | EMTF         |[1.24, 2.40]|
| L1Mu15_14     | 15 GeV      | 14         |        | EMTF1        |[1.24, 1.60]|
| L1Mu11_14     | 11 GeV      | 14         |        | EMTF2        |[1.60, 2.10]|
| L1Mu10_14     | 10 GeV      | 14         |        | EMTF3        |[2.10, 2.40]|
| L1Mu7_14      |  7 GeV      | 14         |
| L1Mu5_14      |  5 GeV      | 14         |
| L1Mu3_14      |  3 GeV      | 14         |
| L1Mu22_13     | 22 GeV      | 13         |
| L1Mu26_12     | 26 GeV      | 12         |
| L1Mu22_12     | 22 GeV      | 12         |
| L1Mu20_12     | 20 GeV      | 12         |
| L1Mu15_12     | 15 GeV      | 12         |
| L1Mu10_12     | 10 GeV      | 12         |
| L1Mu7_12      |  7 GeV      | 12         |
| L1Mu5_12      |  5 GeV      | 12         |
| L1Mu3_12      |  3 GeV      | 12         |
| L1Mu26_8      | 26 GeV      |  8         |
| L1Mu22_8      | 22 GeV      |  8         |
| L1Mu20_8      | 20 GeV      |  8         |
| L1Mu15_8      | 15 GeV      |  8         |
| L1Mu10_8      | 10 GeV      |  8         |
| L1Mu7_8       |  7 GeV      |  8         |
| L1Mu5_8       |  5 GeV      |  8         |
| L1Mu3_8       |  3 GeV      |  8         |
| L1Mu26_4      | 26 GeV      |  4         |
| L1Mu22_4      | 22 GeV      |  4         |
| L1Mu20_4      | 20 GeV      |  4         |
| L1Mu15_4      | 15 GeV      |  4         |
| L1Mu10_4      | 10 GeV      |  4         |
| L1Mu7_4       |  7 GeV      |  4         |
| L1Mu5_4       |  5 GeV      |  4         |
| L1Mu3_4       |  3 GeV      |  4         |
| L1Mu26_0      | 26 GeV      |  0         |
| L1Mu22_0      | 22 GeV      |  0         |
| L1Mu20_0      | 20 GeV      |  0         |
| L1Mu15_0      | 15 GeV      |  0         |
| L1Mu10_0      | 10 GeV      |  0         |
| L1Mu7_0       |  7 GeV      |  0         |
| L1Mu5_0       |  5 GeV      |  0         |
| L1Mu3_0       |  3 GeV      |  0         |


# Useful links

- You can find the golden json files needed in `/eos/user/c/cmsdqm/www/CAF/certification/`


