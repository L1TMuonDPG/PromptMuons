import ROOT
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import utils
import warnings

plt.style.use(hep.style.CMS)

# ----------------------------------------------------------------------
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--legend', type=str, help='dataset legend')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('-i', type=str, help='input dir')
args = parser.parse_args()

output_dir = args.o
input_dir = args.i

# Load merged ROOT file
in_file = ROOT.TFile(input_dir + "merged_total.root", "READ")

# Working points
WPs = ["L1Mu22_12", "L1Mu15_8", "L1Mu7_4", "L1Mu3_0"]

TFs = {
    "uGMT": r"$|\eta| \leq 2.4$",
    "BMTF": r"$|\eta| \leq 0.83$",
    "OMTF": r"$0.83 < |\eta| \leq 1.24$",
    "EMTF": r"$1.24 < |\eta| \leq 2.4$"
}

wp_values = {
    "L1Mu22_12": {"quality": 12, "pt_l1": 22, "pt_reco": 26},
    "L1Mu15_8": {"quality": 8, "pt_l1": 15, "pt_reco": 19},
    "L1Mu7_4": {"quality": 4, "pt_l1": 7, "pt_reco": 11},
    "L1Mu3_0": {"quality": 0, "pt_l1": 3, "pt_reco": 7}
}

vars_title = {
    "eta": r"$\eta^{\mu,offline}$",
    "phi": r"$\phi^{\mu,offline}$ [rad]",
    "pt": r"$p_T^{\mu,offline}$ [GeV]",
    "pt2": r"$p_T^{\mu,offline}$ [GeV]",
    "nPV": "Number of Vertices"
}

# Colors and markers for different working points
wp_styles = {
    "L1Mu22_12": {"color": "#5790fc", "marker": "o", "label": r"$p^{\mu,L1}_{T} \geq 22$ GeV, L1T Quality $\geq 12$"},
    "L1Mu15_8": {"color": "#f89c20", "marker": "s", "label": r"$p^{\mu,L1}_{T} \geq 15$ GeV, L1T Quality $\geq 8$"},
    "L1Mu7_4": {"color": "#e42536", "marker": "^", "label": r"$p^{\mu,L1}_{T} \geq 7$ GeV, L1T Quality $\geq 4$"},
    "L1Mu3_0": {"color": "#964a8b", "marker": "D", "label": r"$p^{\mu,L1}_{T} \geq 3$ GeV, L1T Quality $\geq 0$"}
}

# Extended labels for non-pt variables
wp_labels_extended = {
    "L1Mu22_12": r"$p^{\mu,L1}_{T} \geq 22$ GeV, $p^{\mu,offline}_{T} \geq 26$ GeV, L1T Quality $\geq 12$",
    "L1Mu15_8": r"$p^{\mu,L1}_{T} \geq 15$ GeV, $p^{\mu,offline}_{T} \geq 19$ GeV, L1T Quality $\geq 8$",
    "L1Mu7_4": r"$p^{\mu,L1}_{T} \geq 7$ GeV, $p^{\mu,offline}_{T} \geq 11$ GeV, L1T Quality $\geq 4$",
    "L1Mu3_0": r"$p^{\mu,L1}_{T} \geq 3$ GeV, $p^{\mu,offline}_{T} \geq 7$ GeV, L1T Quality $\geq 0$"
}

# ----------------------------------------------------------------------
# Main plotting loop
for var in vars_title:
    for tf in TFs:
        fig, ax = plt.subplots()
        key = f"{var}"
        
        # Plot all working points for this track finder and variable
        for wp in WPs:
            h_passed = in_file.Get(f"{tf}_{wp}_{key}_passed")
            h_total = in_file.Get(f"{tf}_{wp}_{key}_total")
            
            if not h_passed or not h_total:
                print(f"Warning: Could not find {tf}_{wp}_{key} in file")
                continue
                
            h_passed = utils.add_overflow(h_passed)
            h_total = utils.add_overflow(h_total)
            h_eff = ROOT.TEfficiency(h_passed, h_total)
            
            # Extract efficiency data
            x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff)
            valid = (y > 0) & (y <= 1)

            if var == "pt" or var == "pt2":
                label = wp_styles[wp]["label"]
            else:
                label = wp_labels_extended[wp]
                 
            ax.errorbar(
                x[valid], y[valid],
                xerr=xerr[valid],
                yerr=[yerr_low[valid], yerr_up[valid]],
                fmt=wp_styles[wp]["marker"],
                color=wp_styles[wp]["color"],
                capsize=3,
                label=label,
                markersize=6,
                alpha=0.8
            )

        # Style and labels
        ax.set_xlabel(vars_title[var])
        ax.set_ylabel("Efficiency")
        ax.set_ylim(0, 1.2)
        ax.grid(True)
        
        # CMS label
        utils.add_cms_label(ax, args.legend, loc=2)
        
        # Track finder info - position based on variable type
        if var != "eta":
            ax.text(0.98, 0.95, TFs[tf], transform=ax.transAxes,ha='right', va='top',fontsize=22)
        
        # Legend
        leg = ax.legend(loc='lower right', fontsize=20)
        
        # Axis scaling
        if var == "pt":
            ax.set_xscale("log")
            ax.set_xlim(1, 1000)
        elif var == "pt2":
            ax.set_xlim(0, 60)
        elif var == "phi":
            ax.set_xlim(-3.5, 3.5)
        elif var == "eta":
            ax.set_xlim(-2.5, 2.5)

        # Save plot
        utils.save_canvas(fig, output_dir, "eff_22_15_7_3", f"{tf}_{key}")
        plt.close(fig)

# ----------------------------------------------------------------------
# Close the input file
in_file.Close()
print(f"All plots created successfully! Stored in {output_dir}")