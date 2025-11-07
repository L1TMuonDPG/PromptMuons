import ROOT
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import utils_mpl as utils
import warnings
# warnings.filterwarnings("ignore", message=".*not allowed to get flow bins.*")
# warnings.filterwarnings("ignore", message=".*Adding colorbar to a different Figure.*")

plt.style.use(hep.style.CMS)

# ----------------------------------------------------------------------
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--legend', type=str, help='dataset legend')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('-i', type=str, help='input dir dir')
args = parser.parse_args()

# Pass arguments
output_dir = args.o
input_dir = args.i

# Load merged ROOT file
in_file = ROOT.TFile(input_dir + "merged_total.root","READ")

WPs = {
    "L1Mu26_4": {"L1": r"$p^{\mu,L1}_{T} \geq 26$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 30$ GeV"},
    "L1Mu22_4": {"L1": r"$p^{\mu,L1}_{T} \geq 22$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 26$ GeV"},
    "L1Mu20_4": {"L1": r"$p^{\mu,L1}_{T} \geq 20$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 24$ GeV"},
    "L1Mu15_4": {"L1": r"$p^{\mu,L1}_{T} \geq 15$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 19$ GeV"},
    "L1Mu10_4": {"L1": r"$p^{\mu,L1}_{T} \geq 10$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 14$ GeV"},
    "L1Mu5_4": {"L1": r"$p^{\mu,L1}_{T} \geq 5$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 9$ GeV"},
    "L1Mu3_4": {"L1": r"$p^{\mu,L1}_{T} \geq 3$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 7$ GeV"}
}

vars_title = {
    "eta": r"$\eta^{\mu,offline}$",
    "phi": r"$\phi^{\mu,offline}$ [rad]",
    "pt": r"$p_T^{\mu,offline}$ [GeV]",
    "pt2": r"$p_T^{\mu,offline}$ [GeV]",
}
TFs = {
    "uGMT": r"$|\eta| \leq 2.4$",
    "BMTF": r"$|\eta| \leq 0.83$",
    "OMTF": r"$0.83 < |\eta| \leq 1.24$",
    "EMTF": r"$1.24 < |\eta| \leq 2.4$",
    "EMTF1": r"$1.24 < |\eta| \leq 1.6$",
    "EMTF2": r"$1.6 < |\eta| \leq 2.1$",
    "EMTF3": r"$2.1 < |\eta| \leq 2.4$"
}

tf_markers = {
    "uGMT": "D",
    "BMTF": "o",
    "OMTF": "s",
    "EMTF": "^",
    "EMTF1": "v",
    "EMTF2": "<",
    "EMTF3": ">",
}

wp_markers = {
    "L1Mu26_4": "o",
    "L1Mu22_4": "s", 
    "L1Mu20_4": "^",
    "L1Mu15_4": "D",
    "L1Mu10_4": "v",
    "L1Mu5_4": "<",
    "L1Mu3_4": ">",
}
wp_colors = {
    "L1Mu26_4": "#1845fb", 
    "L1Mu22_4": "#ff5e02",   
    "L1Mu20_4": "#c91f16",   
    "L1Mu15_4": "#c849a9",   
    "L1Mu10_4": "#adad7d",   
    "L1Mu5_4": "#86c8dd",    
    "L1Mu3_4": "#578dff",    
}

tf_colors = {
    "BMTF": "#3f90da",    
    "OMTF": "#ffa90e",    
    "EMTF": "#bd1f01",    
    "EMTF1": "#94a4a2",   
    "EMTF2": "#832db6",    
    "EMTF3": "#a96b59",    
    "uGMT": "#e76300",     
}


# ----------------------------------------------------------------------
print("Creating pt comparison plots...")

for var in vars_title:
    for tf in TFs:
        fig, ax = plt.subplots()
        key = f"_{var}"
        
        # Plot all working points for this track finder and variable
        for wp in WPs:
            # Get histograms
            h_passed = in_file.Get(f"{tf}_{wp}{key}_passed")
            h_total = in_file.Get(f"{tf}_{wp}{key}_total")
            
            if not h_passed or not h_total:
                print(f"Warning: Could not find {tf}_{wp}{key} in file")
                continue
                
            h_passed = utils.add_overflow(h_passed)
            h_total = utils.add_overflow(h_total)
            h_eff = ROOT.TEfficiency(h_passed, h_total)
            
            # Extract efficiency data
            x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff)            
            valid = (y > 0) & (y <= 1)
            ax.errorbar(
                x[valid], y[valid],
                xerr=xerr[valid],
                yerr=[yerr_low[valid], yerr_up[valid]],
                fmt=wp_markers[wp],
                color=wp_colors[wp],
                capsize=2,
                label=WPs[wp]["L1"],
                markersize=6,
                alpha=0.7
            )

        # Style and labels
        ax.set_xlabel(vars_title[var])
        ax.set_ylabel("Efficiency")
        ax.set_ylim(0, 1.2)
        ax.grid(True)
        
        # CMS label
        utils.add_cms_label(ax, args.legend, loc=2, text="Internal")
        
        # Track finder info
        ax.text(0.98, 0.95, TFs[tf], transform=ax.transAxes,ha='right', va='top',fontsize=22)
        # Quality label
        ax.text(0.98, 0.88, r"L1T Quality $\geq 4$", transform=ax.transAxes,ha='right', va='top', fontsize=22)
        
        # Legend - different for pt/pt2 vs other variables
        if var == "pt" or var == "pt2":
            leg = ax.legend(loc='lower right', fontsize=20)
        else:
            # Create custom legend entries with both L1 and Reco info
            custom_labels = []
            for wp in WPs:
                custom_labels.append(f"{WPs[wp]['L1']}, {WPs[wp]['Reco']}")
            leg = ax.legend(custom_labels, loc='lower right', fontsize=20)
        
        # Axis scaling
        if var == "pt":
            ax.set_xscale("log")
            ax.set_xlim(1, 200)
        elif var == "pt2":
            ax.set_xlim(0, 60)
        elif var == "phi":
            ax.set_xlim(-3.5, 3.5)
        elif var == "eta":
            ax.set_xlim(-2.5, 2.5)

        # Save plot
        utils.save_canvas(fig, output_dir, "eff_pt_comparison", f"{tf}{key}")
        plt.close(fig)

# ----------------------------------------------------------------------
# Part 2: Eta comparison plots (multiple TFs for each WP)
print("Creating eta comparison plots...")

for var in vars_title:
    if var == "eta": 
        continue  # Skip eta comparison for eta variable
    
    for wp in WPs:
        fig, ax = plt.subplots()
        key = f"{wp}_{var}"
        
        # Plot all track finders for this working point and variable
        for tf in ["BMTF", "OMTF", "EMTF", "EMTF1", "EMTF2", "EMTF3", "uGMT"]:
            # Get histograms
            h_passed = in_file.Get(f"{tf}_{key}_passed")
            h_total = in_file.Get(f"{tf}_{key}_total")
            
            if not h_passed or not h_total:
                print(f"Warning: Could not find {tf}_{key} in file")
                continue
                
            h_passed = utils.add_overflow(h_passed)
            h_total = utils.add_overflow(h_total)
            h_eff = ROOT.TEfficiency(h_passed, h_total)
            
            # Extract efficiency data
            x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff)
            valid = (y > 0) & (y <= 1)
            
            # Plot with style for this track finder
            ax.errorbar(
                x[valid], y[valid],
                xerr=xerr[valid],
                yerr=[yerr_low[valid], yerr_up[valid]],
                fmt=tf_markers[tf],
                color=tf_colors[tf],
                capsize=2,
                label=TFs[tf],
                markersize=6,
                alpha=0.7
            )

        # Style and labels
        ax.set_xlabel(vars_title[var])
        ax.set_ylabel("Efficiency")
        ax.set_ylim(0, 1.2)
        ax.grid(True)
        
        # CMS label
        utils.add_cms_label(ax, args.legend, loc=2, text="Internal")
        
        # Working point info
        ax.text(0.98, 0.95, f"{WPs[wp]['L1']}, {WPs[wp]['Reco']}", transform=ax.transAxes, ha='right', va='top', fontsize=22)
        
        # Quality label
        ax.text(0.98, 0.88, r"L1T Quality $\geq 4$", transform=ax.transAxes,ha='right', va='top', fontsize=22)
        
        # Legend
        leg = ax.legend(loc='lower right', fontsize=20)
        
        # Axis scaling
        if var == "pt":
            ax.set_xscale("log")
            ax.set_xlim(1, 200)
        elif var == "pt2":
            ax.set_xlim(0, 60)
        elif var == "phi":
            ax.set_xlim(-3.5, 3.5)

        # Save plot
        utils.save_canvas(fig, output_dir, "eff_eta_comparison", key)
        plt.close(fig)

# ----------------------------------------------------------------------
# Close the input file
in_file.Close()