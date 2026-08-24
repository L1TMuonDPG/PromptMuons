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
# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--legend', type=str, help='dataset legend')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('-i', type=str, help='input dir')  # This can be removed if not needed
args = parser.parse_args()

output_dir = args.o

# Load ROOT files for different eras
era_files = {
    "2024B": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024B/eff/merged_total.root", "READ"),
    "2024C": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024C/eff/merged_total.root", "READ"),
    "2024D": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024D/eff/merged_total.root", "READ"),
    "2024E": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024E/eff/merged_total.root", "READ"),
    "2024F": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024F/eff/merged_total.root", "READ"),
    "2024G": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024G/eff/merged_total.root", "READ"),
    "2024H": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024H/eff/merged_total.root", "READ"),
    "2024I": ROOT.TFile("/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/nplastir/PromptMuons/2024/files/2024I/eff/merged_total.root", "READ")
}

# Working points
pt_groups = {
    12: [26, 22, 20, 15, 10, 7, 5, 3],
    8:  [26, 22, 20, 15, 10, 7, 5, 3],
    4:  [26, 22, 20, 15, 10, 7, 5, 3],
    0:  [26, 22, 20, 15, 10, 7, 5, 3],
}

# Auto-generate WPs
WPs = [f"L1Mu{pt}_{q}" for q, pts in pt_groups.items() for pt in pts]
wp_values = {}

vars_title = {
    "eta": r"$\eta^{\mu,offline}$",
    "phi": r"$\phi^{\mu,offline}$ [rad]",
    "pt": r"$p_T^{\mu,offline}$ [GeV]",
    "pt2": r"$p_T^{\mu,offline}$ [GeV]",
    "nPV": "Number of Vertices",
}

# Define colors and markers for different eras
era_styles = {
    "2024B": {"marker": "o", "label": r"2024B (0.13 $\mathrm{fb}^{-1}$)", "color": "#1845fb"},
    "2024C": {"marker": "o", "label": r"2024C (7.26 $\mathrm{fb}^{-1}$)", "color": "#ff5f02"}, 
    "2024D": {"marker": "s", "label": r"2024D (7.98 $\mathrm{fb}^{-1}$)", "color": "#c91f16"},
    "2024E": {"marker": "^", "label": r"2024E (11.42 $\mathrm{fb}^{-1}$)", "color": "#c849a8"},
    "2024F": {"marker": "D", "label": r"2024F (28.04 $\mathrm{fb}^{-1}$)", "color": "#adad7d"},
    "2024G": {"marker": "v", "label": r"2024G (38.07 $\mathrm{fb}^{-1}$)", "color": "#86c8dd"},
    "2024H": {"marker": "v", "label": r"2024H (5.49 $\mathrm{fb}^{-1}$)", "color": "#578cff"},
    "2024I": {"marker": "v", "label": r"2024I (11.56 $\mathrm{fb}^{-1}$)", "color": "#656364"}
}

# Track finder information
track_finders = {
    "BMTF": {
        "eta_range": r"$|\eta| \leq 0.83$",
        "legend_loc": "lower right"
    },
    "OMTF": {
        "eta_range": r"$0.83 < |\eta| \leq 1.24$", 
        "legend_loc": "lower right"
    },
    "EMTF": {
        "eta_range": r"$1.24 < |\eta| \leq 2.4$",
        "legend_loc": "lower right"
    },
    "uGMT": {
        "eta_range": r"$|\eta| \leq 2.4$",
        "legend_loc": "lower right"
    }
}

# ----------------------------------------------------------------------
# Main plotting loop - for each track finder
for tf in track_finders:
    tf_info = track_finders[tf]
    
    for wp in WPs:
        pt = int(wp.split('_')[0].replace("L1Mu",""))
        q  = int(wp.split('_')[1])
        wp_values[wp] = {
            "quality": q,
            "pt_l1": pt,
            "pt_reco": pt + 4
        }
        for var in vars_title:
            fig, ax = plt.subplots()
            key = f"{wp}_{var}"
            values = wp_values[wp]
            quality_label = f"L1T Quality ≥ {values['quality']}"
            pt_l1_label = f"$p_T^{{\mu,L1}} ≥ {values['pt_l1']}$ GeV"
            pt_reco_label = f"$p_T^{{\mu,offline}} ≥ {values['pt_reco']}$ GeV"

            # Plot efficiencies for all eras for this track finder
            for era, era_file in era_files.items():
                style = era_styles[era]
                
                # Get histograms for this track finder and era
                h_passed = utils.add_overflow(era_file.Get(f"{tf}_{key}_passed"))
                h_total = utils.add_overflow(era_file.Get(f"{tf}_{key}_total"))
                
                if not h_passed or not h_total:
                    print(f"Warning: Could not find {tf}_{key} in {era}")
                    continue
                    
                h_eff = ROOT.TEfficiency(h_passed, h_total)
                x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff)
                
                if x is None:
                    continue
                    
                valid = (y > 0) & (y <= 1)
                
                ax.errorbar(
                    x[valid], y[valid],
                    xerr=xerr[valid],
                    yerr=[yerr_low[valid], yerr_up[valid]],
                    fmt=style["marker"],
                    color=style["color"],
                    capsize=2,
                    label=style["label"],
                    markersize=5,
                )

            # ------------------------------------------------------------------
            # Style and labels
            ax.set_xlabel(vars_title[var])
            ax.set_ylabel("Efficiency")
            ax.legend(title="", loc=tf_info["legend_loc"])
            ax.grid(True)

            # CMS & dataset labels
            if var == "eta":
                ax.set_ylim(0, 1.1)
                utils.add_cms_label(ax, "2024", loc=0, text="Preliminary")
            else:
                ax.set_ylim(0, 1.2)
                utils.add_cms_label(ax, "2024", loc=2, text="Preliminary")
                # Add eta range for this track finder
                ax.text(0.85, 0.58, tf_info["eta_range"], transform=ax.transAxes,ha='right', va='top', fontsize=24)
                
            # Add quality and pT labels
            # if var == "phi" or var == "eta":
            #     ax.text(0.62, 0.58, quality_label, transform=ax.transAxes)
            #     ax.text(0.62, 0.51, pt_l1_label, transform=ax.transAxes)
            #     ax.text(0.62, 0.44, pt_reco_label, transform=ax.transAxes)
            # else:
            #     ax.text(0.62, 0.51, quality_label, transform=ax.transAxes)
            #     ax.text(0.62, 0.44, pt_l1_label, transform=ax.transAxes)

            if var == "phi" or var == "eta" or var == "nPV":
                ax.text(0.05, 0.19, quality_label, transform=ax.transAxes)
                ax.text(0.05, 0.12, pt_l1_label, transform=ax.transAxes)
                ax.text(0.05, 0.05, pt_reco_label, transform=ax.transAxes)
            else:
                ax.text(0.62, 0.92, quality_label, transform=ax.transAxes)
                ax.text(0.62, 0.85, pt_l1_label, transform=ax.transAxes)

            # ------------------------------------------------------------------
            # Axis scaling
            if var == "pt":
                ax.set_xscale("log")
                ax.set_xlim(1, 2000)
            elif var == "pt2":
                ax.set_xlim(0, 60)
            elif var == "phi":
                ax.set_xlim(-3.5, 3.5)
            elif var == "eta":
                ax.set_xlim(-2.5, 2.5)

            # ------------------------------------------------------------------
            # Save plots
            utils.save_canvas(fig, output_dir, "eff", f"{key}_{tf}_eras")
            plt.close(fig)

# ----------------------------------------------------------------------
# Close all files
for era_file in era_files.values():
    era_file.Close()