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
parser.add_argument('--legend', type=str, help='Dataset legend')
parser.add_argument('-o', type=str, help='Output directory')
parser.add_argument('-i', type=str, help='Input directory')
args = parser.parse_args()

output_dir = args.o
input_dir = args.i

# Load merged ROOT file
in_file = ROOT.TFile(input_dir + "merged_total.root", "READ")

WPs = ["L1Mu22_12", "L1Mu22_13", "L1Mu22_14", "L1Mu22_15"]

# Define colors for each WP (using similar colors to your CMS_color_X)
wp_colors = {
    "L1Mu22_12": "#5790fc",  # Similar to CMS_color_0 (blue)
    "L1Mu22_13": "#f89c20",  # Similar to CMS_color_1 (orange)
    "L1Mu22_14": "#e42536",  # Similar to CMS_color_2 (red)
    "L1Mu22_15": "#964a8b",  # Similar to CMS_color_5 (purple)
}

wp_markers = {
    "L1Mu22_12": "o",
    "L1Mu22_13": "s",
    "L1Mu22_14": "^",
    "L1Mu22_15": "D",
}

# Quality thresholds for each WP
quality_thresholds = {
    "L1Mu22_12": 12,
    "L1Mu22_13": 13,
    "L1Mu22_14": 14,
    "L1Mu22_15": 15,
}

vars_title = {
    "eta": r"$\eta^{\mu,offline}$",
    "phi": r"$\phi^{\mu,offline}$ [rad]",
    "pt2": r"$p_T^{\mu,offline}$ [GeV]",
    "pt": r"$p_T^{\mu,offline}$ [GeV]",
    "nPV": "Number of Vertices"
}

# ----------------------------------------------------------------------
# Main plotting loop
for var in vars_title:
    fig, ax = plt.subplots()
    
    # Plot all working points for BMTF and current variable
    for i, wp in enumerate(WPs):
        key = f"{wp}_{var}"
        
        # Get BMTF histograms
        h_passed_BMTF = in_file.Get(f"BMTF_{key}_passed")
        h_total_BMTF = in_file.Get(f"BMTF_{key}_total")
        
        if not h_passed_BMTF or not h_total_BMTF:
            print(f"Warning: Could not find BMTF_{key} in file")
            continue
            
        h_passed_BMTF = utils.add_overflow(h_passed_BMTF)
        h_total_BMTF = utils.add_overflow(h_total_BMTF)
        h_eff_BMTF = ROOT.TEfficiency(h_passed_BMTF, h_total_BMTF)
        
        # Extract efficiency data
        x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff_BMTF)
        valid = (y > 0) & (y <= 1)
        
        # Generate legend entry label
        quality = quality_thresholds[wp]
        legend_label = f"L1T Quality ≥ {quality}"
        
        ax.errorbar(
            x[valid], y[valid],
            xerr=xerr[valid],
            yerr=[yerr_low[valid], yerr_up[valid]],
            fmt=wp_markers[wp],
            color=wp_colors[wp],
            capsize=3,
            label=legend_label,
            markersize=6,
            alpha=0.8
        )

    # Style and labels
    ax.set_xlabel(vars_title[var])
    ax.set_ylabel("Efficiency")
    ax.set_ylim(0, 1.2)
    ax.grid(True)
    
    utils.add_cms_label(ax, args.legend, loc=2)
    # CMS label - position based on variable type
    if var == "eta" or var == "phi":
        leg = ax.legend(loc='upper right', ncol=2, fontsize=18)
        ax.text(0.98, 0.03, r"$p^{\mu,L1}_{T} \geq 22$ GeV, $p^{\mu,offline}_{T} \geq 26$ GeV", 
            transform=ax.transAxes, ha='right', va='bottom', fontsize=22)
    else:
        leg = ax.legend(loc='lower right', ncol=2, fontsize=18) 
        ax.text(0.98, 0.90, r"$p^{\mu,L1}_{T} \geq 22$ GeV", 
            transform=ax.transAxes, ha='right', va='bottom', fontsize=22)
    
    # Axis scaling and limits
    if var == "pt":
        ax.set_xlim(10, 160)
    elif var == "pt2":
        ax.set_xlim(0, 60)
    elif var == "eta":
        ax.set_xlim(-0.9, 0.9)
    elif var == "phi":
        ax.set_xlim(-3.5, 3.5)
    
    # Adjust layout to make room for bottom legend
    plt.tight_layout()    
    # Save plot
    utils.save_canvas(fig, output_dir, "eff_qual", var)
    plt.close(fig)

# ----------------------------------------------------------------------
# Close the input file
in_file.Close()
print(f"All quality plots created successfully! Stored in {output_dir}")