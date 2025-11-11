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

WPs = ["L1Mu22_12", "L1Mu15_8"]

wp_values = {
    "L1Mu22_12": {"quality": 12, "pt_l1": 22, "pt_reco": 26},
    "L1Mu15_8": {"quality": 8, "pt_l1": 15, "pt_reco": 19}
}

vars_title = {
    "eta": r"$\eta^{\mu,offline}$",
    "phi": r"$\phi^{\mu,offline}$ [rad]",
    "pt": r"$p_T^{\mu,offline}$ [GeV]",
    "pt2": r"$p_T^{\mu,offline}$ [GeV]",
}

# Colors and markers for the two working points
wp_styles = {
    "L1Mu22_12": {
        "color": "#5790fc", 
        "marker": "o", 
        "label_short": r"$p^{\mu,L1}_{T} \geq 22$ GeV, L1T Quality $\geq 12$",
        "label_long": r"$p^{\mu,L1}_{T} \geq 22$ GeV, $p^{\mu,offline}_{T} \geq 26$ GeV, L1T Quality $\geq 12$"
    },
    "L1Mu15_8": {
        "color": "#e42536", 
        "marker": "s", 
        "label_short": r"$p^{\mu,L1}_{T} \geq 15$ GeV, L1T Quality $\geq 8$",
        "label_long": r"$p^{\mu,L1}_{T} \geq 15$ GeV, $p^{\mu,offline}_{T} \geq 19$ GeV, L1T Quality $\geq 8$"
    }
}

# ----------------------------------------------------------------------
# Main plotting loop
for var in vars_title:
    fig, ax = plt.subplots()
    
    # Plot both working points for uGMT and current variable
    for wp in WPs:
        hist_base = f"uGMT_{wp}_{var}"
        
        # Get uGMT histograms
        h_passed = in_file.Get(f"{hist_base}_passed")
        h_total = in_file.Get(f"{hist_base}_total")
        
        if not h_passed or not h_total:
            print(f"Warning: Could not find {hist_base} in file")
            continue
            
        h_passed = utils.add_overflow(h_passed)
        h_total = utils.add_overflow(h_total)
        h_eff = ROOT.TEfficiency(h_passed, h_total)
        
        # Extract efficiency data
        x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff)
            
        valid = (y > 0) & (y <= 1)
        
        # Choose label based on variable type
        if var == "pt" or var == "pt2":
            label = wp_styles[wp]["label_short"]
        else:
            label = wp_styles[wp]["label_long"]
        
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
    utils.add_cms_label(ax, args.legend, loc=2, text="Internal")
    leg = ax.legend(loc='lower right', fontsize=17)
    
    if var != "eta":
        ax.text(0.98, 0.93, r"$|\eta| \leq 2.4$", transform=ax.transAxes,ha='right', va='top', fontsize=22)
       
    # Axis scaling and limits
    if var == "pt":
        ax.set_xscale("log")
        ax.set_xlim(1, 1000)
    elif var == "pt2":
        ax.set_xlim(0, 60)
    elif var == "phi":
        ax.set_xlim(-3.5, 3.5)
    elif var == "eta":
        ax.set_xlim(-2.5, 2.5)  # uGMT full range

    # Save plot
    utils.save_canvas(fig, output_dir, "eff_22_15", var)
    plt.close(fig)

# ----------------------------------------------------------------------
# Close the input file
in_file.Close()
print("All uGMT comparison plots created successfully!")