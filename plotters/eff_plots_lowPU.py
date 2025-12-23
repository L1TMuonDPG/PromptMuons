
#!/usr/bin/env python3
import ROOT
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import utils_mpl as utils
import warnings
warnings.filterwarnings("ignore", message=".*not allowed to get flow bins.*")
warnings.filterwarnings("ignore", message=".*Adding colorbar to a different Figure.*")

plt.style.use(hep.style.CMS)

# ----------------------------------------------------------------------
# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--legend', type=str, help='dataset legend')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('-i', type=str, help='input dir')
args = parser.parse_args()

output_dir = args.o 
input_dir = args.i 

# Load merged ROOT file
in_file = ROOT.TFile(os.path.join(input_dir, "merged_total.root"), "READ")

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
}

legend_labels = {
    "uGMT": r"$|\eta| \leq 2.4$",
    "BMTF": r"$|\eta| \leq 0.83$",
    "OMTF": r"$0.83 < |\eta| \leq 1.24$",
    "EMTF": r"$1.24 < |\eta| \leq 2.4$",
}

# PU regions to plot together (Option B)
pu_regions = {
    "all": {"label": "Baseline", "color": "k", "marker": "D"},            # baseline
    "low_5_7": {"label": r"$5 \leq nPV \leq 7$", "color": "#5790fc", "marker": "o"},   # blue
    "pu_0_10": {"label": r"$0 \leq nPV \leq 10$", "color": "#f89c20", "marker": "s"},  # green
    "pu_10_20": {"label": r"$10 \leq nPV \leq 20$", "color": "#e42536", "marker": "^"},# red
}

# Markers per TF
tf_markers = {"uGMT": "D", "BMTF": "o", "OMTF": "s", "EMTF": "^"}
#tf_order = ["uGMT", "BMTF", "OMTF", "EMTF"]
tf_order = ["OMTF"]

# ----------------------------------------------------------------------
# Main plotting loop: for each WP and variable create plots with all PU curves
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
        key_base = f"{wp}_{var}"
        values = wp_values.get(wp, {})
        quality_label = f"L1T Quality \u2265 {values.get('quality', '')}"
        pt_l1_label = f"$p_T^{{\\mu,L1}} \\geq {values.get('pt_l1','')}$ GeV"
        pt_reco_label = f"$p_T^{{\\mu,offline}} \\geq {values.get('pt_reco','')}$ GeV"

        # For eta we need TF separation and overlap logic; for others we plot each TF directly
        for tf in tf_order:
            print(tf)
            # For each PU region (including baseline 'all')
            for pu_key, pu_info in pu_regions.items():
                marker = pu_regions[pu_key]['marker']
                pu_suffix = ""
                if pu_key == "low_5_7":
                    pu_suffix = "LowPU_5_7"
                elif pu_key == "pu_0_10":
                    pu_suffix = "PU_0_10"
                elif pu_key == "pu_10_20":
                    pu_suffix = "PU_10_20"
                elif pu_key == "all":
                    pu_suffix = ""  # baseline names have no extra suffix

                # load TEff
                teff = utils.load_teff(in_file, tf, key_base, pu_suffix)
                if not teff:
                    continue

                # If var == eta, we will postpone plotting after overlap handling;
                # here we just store the hist objects for that PU region/TF
                # if var == "eta":
                #     # collect histograms for overlap work
                #     pass

                # For non-eta, directly convert and plot
                if var != "nPV":
                    x, y, ylow, yup, xerr = utils.efficiency_to_vector(teff)
                    if x is None:
                        continue
                    valid = (y > 0) & (y <= 1)
                    #valid = (y > -1e-6) & (y <= 1.0001)  # include 0..1
                    # style
                    color = pu_info["color"]
                    label = pu_info["label"]  # only label PU once per TF set
                    # to avoid duplicate labels for same pu across TFs, only label when tf == 'uGMT'
                    ax.errorbar(
                        x[valid], y[valid],
                        xerr=xerr[valid],
                        yerr=[ylow[valid], yup[valid]],
                        linestyle='',            # ← FIX
                        marker=marker,  
                        color=color,
                        mec=color,
                        mfc=color,
                        capsize=2,
                        label=f"{pu_info['label']}",
                    )

            # # ---------- Special handling for eta: build TEffs for each PU and apply overlap ----------
            # if var == "eta":
            #     # For each PU region build dictionaries of hist pairs
            #     for pu_key, pu_info in pu_regions.items():
            #         pu_suffix = ""
            #         if pu_key == "low_5_7":
            #             pu_suffix = "LowPU_5_7"
            #         elif pu_key == "pu_0_10":
            #             pu_suffix = "PU_0_10"
            #         elif pu_key == "pu_10_20":
            #             pu_suffix = "PU_10_20"
            #         elif pu_key == "all":
            #             pu_suffix = ""

            #         # load raw passed/total histograms for BMTF/OMTF/EMTF
            #         hpb = in_file.Get(f"BMTF_{key_base}"+(f"_{pu_suffix}" if pu_suffix else "")+ "_passed")
            #         htb = in_file.Get(f"BMTF_{key_base}"+(f"_{pu_suffix}" if pu_suffix else "")+ "_total")
            #         hpo = in_file.Get(f"OMTF_{key_base}"+(f"_{pu_suffix}" if pu_suffix else "")+ "_passed")
            #         hto = in_file.Get(f"OMTF_{key_base}"+(f"_{pu_suffix}" if pu_suffix else "")+ "_total")
            #         hpe = in_file.Get(f"EMTF_{key_base}"+(f"_{pu_suffix}" if pu_suffix else "")+ "_passed")
            #         hte = in_file.Get(f"EMTF_{key_base}"+(f"_{pu_suffix}" if pu_suffix else "")+ "_total")

            #         if not (hpb and htb and hpo and hto and hpe and hte):
            #             continue

            #         # add overflow
            #         hpb = utils.add_overflow(hpb)
            #         htb = utils.add_overflow(htb)
            #         hpo = utils.add_overflow(hpo)
            #         hto = utils.add_overflow(hto)
            #         hpe = utils.add_overflow(hpe)
            #         hte = utils.add_overflow(hte)

            #         # apply overlap reassignment
            #         hpb, htb, hpo, hto, hpe, hte = utils.apply_eta_overlap(hpb, htb, hpo, hto, hpe, hte)

            #         # recreate TEff objects
            #         teff_b = ROOT.TEfficiency(hpb, htb)
            #         teff_o = ROOT.TEfficiency(hpo, hto)
            #         teff_e = ROOT.TEfficiency(hpe, hte)

            #     # plot each TF for this PU region
            #     for tf, teff in zip(["BMTF","OMTF","EMTF"], [teff_b, teff_o, teff_e]):
            #         x, y, ylow, yup, xerr = utils.efficiency_to_vector(teff)
            #         if x is None:
            #             continue
            #         valid = (y > 0) & (y <= 1)
            #         #valid = (y > -1e-6) & (y <= 1.0001)
            #         color = pu_regions[pu_key]["color"]
            #         marker = pu_regions[pu_key]['marker']
            #         ax.errorbar(
            #             x[valid], y[valid],
            #             xerr=xerr[valid],
            #             yerr=[ylow[valid], yup[valid]],
            #             linestyle='',            # ← FIX
            #             marker=marker,  
            #             color=color,
            #             mec=color,
            #             mfc=color,
            #             capsize=2,
            #             label=f"{pu_regions[pu_key]['label']}"
            #         )

            # ------------------------------------------------------------------
            # Style and labels
            ax.set_ylim(0, 1.2)
            ax.set_xlabel(vars_title[var])
            ax.set_ylabel("Efficiency")
            ax.grid(True)

            # Legend: reduce duplicate labels
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), loc="lower right")

            # CMS & dataset labels
            utils.add_cms_label(ax, args.legend, loc=2, text="Internal")
            if var == "phi":
                ax.text(0.62, 0.44, quality_label, transform=ax.transAxes)
                ax.text(0.62, 0.37, pt_l1_label, transform=ax.transAxes)
                ax.text(0.62, 0.30, pt_reco_label, transform=ax.transAxes)
            else:
                ax.text(0.62, 0.37, quality_label, transform=ax.transAxes)
                ax.text(0.62, 0.30, pt_l1_label, transform=ax.transAxes)

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

            # Save
            fname = os.path.join(output_dir, f"eff_{key_base}_{tf}_PUcomp.png")
            utils.save_canvas(fig, output_dir, "eff", key_base + "_" + tf + "_PUcomp")
            plt.close(fig)

in_file.Close()