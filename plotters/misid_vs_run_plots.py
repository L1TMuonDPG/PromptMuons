import ROOT
import argparse
import re
import math
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import utils

plt.style.use(hep.style.CMS)

# ----------------------------------------------------------------------
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--legend", type=str, help="dataset legend")
parser.add_argument("-o", type=str, help="output dir")
parser.add_argument("-i", type=str, help="input dir dir")
args = parser.parse_args()

# Pass arguments
output_dir = args.o
input_dir = args.i
# Load input ROOT file
in_file = ROOT.TFile.Open(input_dir + "merged_total.root", "READ")

# ----------------------------------------------------------------------
# Find run numbers
run_numbers = set()
histos_list = in_file.GetListOfKeys()
for histo in histos_list:
    histo_name = histo.GetName()
    run_number = re.search(r"22_(.*)_phi", histo_name).group(1)
    run_numbers.add(int(run_number))
run_numbers = sorted(run_numbers)
# ----------------------------------------------------------------------
# Configuration
TFs = ["uGMT", "BMTF", "OMTF", "EMTF"]
WPs = ["SingleMu_22"]
vars = ["phi"]

colors = {
    "uGMT": "#5790fc",
    "BMTF": "#f89c20",
    "OMTF": "#e42536",
    "EMTF": "#964a8b",
}
markers = {
    "uGMT": "D",
    "BMTF": "o",
    "OMTF": "s",
    "EMTF": "^",
}

legend_labels = {
    "uGMT": r"$|\eta| \leq 2.4$",
    "BMTF": r"$|\eta| \leq 0.83$",
    "OMTF": r"$0.83 < |\eta| \leq 1.24$",
    "EMTF": r"$1.24 < |\eta| \leq 2.4$",
}

pt_l1_label = r"$p_T^{\mu,L1} \geq 22$ GeV"
pt_reco_label = r"$p_T^{\mu,offline} \geq 26$ GeV"
quality_label = r"L1T Quality $\geq 12$"

# ----------------------------------------------------------------------
# Store all TF results for overlay
overlay_data = {}

# Misid vs run loop
for tf in TFs:
    misid_values = []
    misid_err_low = []
    misid_err_high = []

    for run_number in run_numbers:
        misid, err_low, err_high = None, 0, 0

        for wp in WPs:
            for var in vars:
                key = f"{tf}_{wp}_{run_number}_{var}"
                h_passed = in_file.Get(key + "_passed")
                h_total = in_file.Get(key + "_total")

                if not h_passed or not h_total:
                    continue

                total = h_total.Integral()
                passed = h_passed.Integral()

                if total > 0:
                    misid = passed / total
                    misid_err = misid * math.sqrt(passed) / total
                    err_low = misid_err
                    err_high = min(misid_err, 1 - misid)
                else:
                    misid = 0
                    err_low = 0
                    err_high = 0

                misid_values.append(misid)
                misid_err_low.append(err_low)
                misid_err_high.append(err_high)

    # Convert lists to numpy arrays
    run_array = np.array(run_numbers)
    misid_values = np.array(misid_values)
    misid_err_low = np.array(misid_err_low)
    misid_err_high = np.array(misid_err_high)

    # Save data for overlay plot
    overlay_data[tf] = (run_array, misid_values, misid_err_low, misid_err_high)

    # ------------------------------------------------------------------
    # Plot individual TF
    fig, ax = plt.subplots()

    ax.errorbar(
        run_array,
        misid_values,
        yerr=[misid_err_low, misid_err_high],
        fmt=markers[tf],
        color=colors[tf],
        capsize=2,
    )

    ax.set_xlabel("Run Number")
    ax.set_ylabel("Charge misidentification probability")
    ax.set_ylim(0.0, 0.1)
    ax.set_xlim(min(run_numbers) - 10, max(run_numbers) + 10)
    ax.ticklabel_format(style="plain", axis="x")
    #ax.set_xticklabels(ax.get_xticks(), rotation=45, ha='right')

    # ------------------------------------------------------------------
    utils.add_cms_label(ax, args.legend, loc=2, text="Internal")

    # Text labels
    ax.text(0.98, 0.95, legend_labels.get(tf), transform=ax.transAxes, ha='right', va='top', fontsize=22)
    ax.text(0.98, 0.88, pt_l1_label, transform=ax.transAxes, ha='right', va='top', fontsize=22)
    ax.text(0.98, 0.81, pt_reco_label, transform=ax.transAxes, ha='right', va='top', fontsize=22)
    ax.text(0.98, 0.74, quality_label, transform=ax.transAxes, ha='right', va='top', fontsize=22)

    utils.save_canvas(fig, output_dir, "misid_vs_run", tf)
    plt.close(fig)

# ----------------------------------------------------------------------
# Combined overlay plot for all TFs
fig_all, ax_all = plt.subplots()

for tf in TFs:
    if tf not in overlay_data:
        continue
    run_array, misid_values, misid_err_low, misid_err_high = overlay_data[tf]
    ax_all.errorbar(
        run_array,
        misid_values,
        yerr=[misid_err_low, misid_err_high],
        fmt=markers[tf],
        color=colors[tf],
        capsize=2,
        label=legend_labels.get(tf, tf),
    )

ax_all.set_xlabel("Run Number")
ax_all.set_ylabel("Charge misidentification probability")
ax_all.set_ylim(0.0, 0.15)
ax_all.set_xlim(min(run_numbers) - 10, max(run_numbers) + 10)
ax_all.ticklabel_format(style="plain", axis="x")
#ax_all.set_xticklabels(ax_all.get_xticks(), rotation=45, ha='right')

ax_all.legend(title="", loc="upper right")

utils.add_cms_label(ax_all, args.legend, loc=0, text="Internal")
ax_all.text(0.05, 0.95, pt_l1_label, transform=ax_all.transAxes, ha='left', va='top', fontsize=22)
ax_all.text(0.05, 0.88, pt_reco_label, transform=ax_all.transAxes, ha='left', va='top', fontsize=22)
ax_all.text(0.05, 0.81, quality_label, transform=ax_all.transAxes, ha='left', va='top', fontsize=22)

utils.save_canvas(fig_all, output_dir, "misid_vs_run", "All_TFs")
plt.close(fig_all)

# ----------------------------------------------------------------------
in_file.Close()
