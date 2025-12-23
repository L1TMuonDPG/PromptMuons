import ROOT
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import utils

plt.style.use(hep.style.CMS)

# ----------------------------------------------------------------------
# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--legend", type=str, help="dataset legend")
parser.add_argument("-o", type=str, help="output dir")
parser.add_argument("-i", type=str, help="input dir")
args = parser.parse_args()

output_dir = args.o
input_dir = args.i

# ----------------------------------------------------------------------
# Load merged ROOT file
in_file = ROOT.TFile.Open(os.path.join(input_dir, "merged_total.root"), "READ")

WPs = ["SingleMu_22"]

vars_title = {
    # "eta": r"$\eta^{\mu,offline}$",
    # "phi": r"$\phi^{\mu,offline}$ [rad]",
    "pt": r"$p_T^{\mu,offline}$ [GeV]",
    "pt2": r"$p_T^{\mu,offline}$ [GeV]",
}

legend_labels = {
    "uGMT": r"$|\eta| \leq 2.4$",
    "BMTF": r"$|\eta| \leq 0.83$",
    "OMTF": r"$0.83 < |\eta| \leq 1.24$",
    "EMTF": r"$1.24 < |\eta| \leq 2.4$",
}

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

# ----------------------------------------------------------------------
#1D charge misid
for var in vars_title:
    key = "_" + var
    fig, ax = plt.subplots()
    subsystems = ["uGMT", "BMTF", "OMTF", "EMTF"]

    for tf in subsystems:
        h_passed = utils.add_overflow(in_file.Get(f"{tf}_{key}_passed"))
        h_total = utils.add_overflow(in_file.Get(f"{tf}_{key}_total"))
        if not h_passed or not h_total:
            continue

        h_misid = ROOT.TEfficiency(h_passed, h_total)
        x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_misid)
        valid = (y > 0) & (y <= 1)

        ax.errorbar(
            x[valid],
            y[valid],
            xerr=xerr[valid],
            yerr=[yerr_low[valid], yerr_up[valid]],
            fmt=markers[tf],
            color=colors[tf],
            capsize=2,
            label=legend_labels[tf],
        )

    # ------------------------------------------------------------------
    # Style and labels
    ax.set_xlabel(vars_title[var])
    ax.set_ylabel("Charge misidentification probability")
    ax.set_ylim(0, 1.2)
    ax.legend(title="", loc="upper right")

    # Axis scaling
    if var == "pt":
        ax.set_xscale("log")
        ax.set_xlim(1, 1000)
    elif var == "pt2":
        ax.set_xlim(0, 60)

    # CMS label and text
    utils.add_cms_label(ax, args.legend, loc=0)
    ax.text(0.62, 0.68, r"L1T Quality $\geq 12$", transform=ax.transAxes)

    # Save
    utils.save_canvas(fig, output_dir, "misid", key)
    ax.clear()

# ----------------------------------------------------------------------
# 2D η–φ heatmap for misid
fig2, ax2 = plt.subplots()
plt.style.use(hep.style.CMS)

h_misid_uGMT = in_file.Get("h_misid_phi_etauGMT_")
if not h_misid_uGMT:
    raise RuntimeError("2D histogram 'h_misid_phi_etauGMT_' not found in file.")

temp_canvas = ROOT.TCanvas("temp", "temp", 800, 600)
h_misid_uGMT.Draw("colz")
temp_canvas.Update()
misid_histogram = h_misid_uGMT.GetPaintedHistogram()

# Get the efficiency values and bin information
nx = misid_histogram.GetNbinsX()
ny = misid_histogram.GetNbinsY()
probability = np.zeros((ny, nx))
x_edges = np.zeros(nx + 1)
y_edges = np.zeros(ny + 1)

for i in range(1, nx + 1):
    x_edges[i-1] = misid_histogram.GetXaxis().GetBinLowEdge(i)
    for j in range(1, ny + 1):
        y_edges[j-1] = misid_histogram.GetYaxis().GetBinLowEdge(j)
        probability[j-1, i-1] = misid_histogram.GetBinContent(i, j)
    
    # Set the last edges
    x_edges[-1] = misid_histogram.GetXaxis().GetBinUpEdge(nx)
    y_edges[-1] = misid_histogram.GetYaxis().GetBinUpEdge(ny)

mask_index = np.searchsorted(y_edges, 3.14, side='right')
h2d_masked = probability.copy()
h2d_masked[mask_index-1:, :] = np.nan # Set bins above 3.14 to NaN

hep.hist2dplot(h2d_masked.T, x_edges, y_edges, ax=ax2, cbar=True, flow='none', cbarextend=True)

fig2.get_axes()[-1].set_ylabel("Charge misidentification probability", fontsize=22)
utils.add_cms_label(ax2, args.legend, loc=0)

ax2.set_xlabel(r"$\eta^{\mu,offline}$")
ax2.set_ylabel(r"$\phi^{\mu,offline}$ [rad]")
ax2.set_xlim(-2.4, 2.4)
ax2.set_ylim(-3.14, 3.5)

# Add vertical lines to show regional boundaries
line_positions = [-1.24, -0.83, 0.83, 1.24]
for pos in line_positions:
    ax2.axvline(x=pos, color='red', linestyle='--', linewidth=2, alpha=1.0)

# Add text annotations
text_props = {'fontsize': 14, 'transform': ax2.transAxes}
ax2.text(0.464, 0.95, "BMTF", **text_props)
ax2.text(0.25, 0.95, "OMTF", **text_props)
ax2.text(0.08, 0.95, "EMTF", **text_props)
ax2.text(0.68, 0.95, "OMTF", **text_props)
ax2.text(0.85, 0.95, "EMTF", **text_props)

utils.save_canvas(fig2, output_dir, "misid", "_phi_eta")
plt.close(fig2)
temp_canvas.Close()
del temp_canvas

# ----------------------------------------------------------------------
in_file.Close()
