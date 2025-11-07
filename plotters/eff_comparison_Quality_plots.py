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

# Define working points without quality suffix
base_WPs = {
    "L1Mu26": {"L1": r"$p^{\mu,L1}_{T} \geq 26$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 30$ GeV"},
    "L1Mu22": {"L1": r"$p^{\mu,L1}_{T} \geq 22$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 26$ GeV"},
    "L1Mu20": {"L1": r"$p^{\mu,L1}_{T} \geq 20$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 24$ GeV"},
    "L1Mu15": {"L1": r"$p^{\mu,L1}_{T} \geq 15$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 19$ GeV"},
    "L1Mu10": {"L1": r"$p^{\mu,L1}_{T} \geq 10$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 14$ GeV"},
    "L1Mu5": {"L1": r"$p^{\mu,L1}_{T} \geq 5$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 9$ GeV"},
    "L1Mu3": {"L1": r"$p^{\mu,L1}_{T} \geq 3$ GeV", "Reco": r"$p^{\mu,offline}_{T} \geq 7$ GeV"}
}

# Quality cuts to compare
qualities = ["12", "8", "4", "0"]

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
}

# Colors and markers for different quality cuts
quality_colors = {
    "12": "#5790fc",  # Blue
    "8": "#f89c20",   # Orange
    "4": "#e42536",   # Red
    "0": "#964a8b",   # Purple
}

quality_markers = {
    "12": "o",
    "8": "s",
    "4": "^",
    "0": "D",
}

quality_labels = {
    "12": "L1T Quality ≥ 12",
    "8": "L1T Quality ≥ 8",
    "4": "L1T Quality ≥ 4",
    "0": "L1T Quality ≥ 0",
}

# ----------------------------------------------------------------------
# Part 1: Quality comparison for each track finder and working point
print("Creating quality comparison plots by track finder...")

for var in vars_title:
    for tf in TFs:
        for base_wp in base_WPs:
            fig, ax = plt.subplots()
            key = f"_{var}"
            
            # Plot all quality cuts for this track finder and working point
            for qual in qualities:
                wp_with_qual = f"{base_wp}_{qual}"
                
                # Get histograms
                h_passed = in_file.Get(f"{tf}_{wp_with_qual}{key}_passed")
                h_total = in_file.Get(f"{tf}_{wp_with_qual}{key}_total")
                
                if not h_passed or not h_total:
                    print(f"Warning: Could not find {tf}_{wp_with_qual}{key} in file")
                    continue
                    
                h_passed = utils.add_overflow(h_passed)
                h_total = utils.add_overflow(h_total)
                h_eff = ROOT.TEfficiency(h_passed, h_total)
                
                # Extract efficiency data
                x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff)
                
                if x is None:
                    continue
                    
                valid = (y > 0) & (y <= 1)
                
                ax.errorbar(
                    x[valid], y[valid],
                    xerr=xerr[valid],
                    yerr=[yerr_low[valid], yerr_up[valid]],
                    fmt=quality_markers[qual],
                    color=quality_colors[qual],
                    capsize=2,
                    label=quality_labels[qual],
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
            
            # Track finder and working point info
            ax.text(0.98, 0.96, TFs[tf], transform=ax.transAxes, 
                    ha='right', va='top', fontsize=22)
            ax.text(0.98, 0.89, f"{base_WPs[base_wp]['L1']}, {base_WPs[base_wp]['Reco']}", 
                    transform=ax.transAxes, ha='right', va='top', fontsize=22)
            
            # Legend for quality cuts
            leg = ax.legend(loc='lower right', fontsize=16)
            
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
            utils.save_canvas(fig, output_dir, "eff_quality_comparison", f"{tf}_{base_wp}{key}")
            plt.close(fig)
# ----------------------------------------------------------------------
# Close the input file
in_file.Close()