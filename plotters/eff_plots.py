import ROOT
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import utils
import warnings
# warnings.filterwarnings("ignore", message=".*not allowed to get flow bins.*")
# warnings.filterwarnings("ignore", message=".*Adding colorbar to a different Figure.*")

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
in_file = ROOT.TFile(input_dir + "merged_total.root", "READ")

# Working points
WPs = ["L1Mu22_12"]#, "L1Mu5_8"]
wp_values = {
    "L1Mu22_12": {"quality": 12, "pt_l1": 22, "pt_reco": 26},
    "L1Mu5_8": {"quality": 8, "pt_l1": 5, "pt_reco": 9},
}

vars_title = {
    "eta": r"$\eta^{\mu,offline}$",
    "phi": r"$\phi^{\mu,offline}$ [rad]",
    "pt": r"$p_T^{\mu,offline}$ [GeV]",
    "pt2": r"$p_T^{\mu,offline}$ [GeV]",
    "nPV": "Number of Vertices"
}

legend_labels = {
    "uGMT": r"$|\eta| \leq 2.4$",
    "BMTF": r"$|\eta| \leq 0.83$",
    "OMTF": r"$0.83 < |\eta| \leq 1.24$",
    "EMTF": r"$1.24 < |\eta| \leq 2.4$",
}
# ----------------------------------------------------------------------
# Main plotting loop
for wp in WPs:
    for var in vars_title:
        fig, ax = plt.subplots()
        key = f"{wp}_{var}"
        values = wp_values[wp]
        quality_label = f"L1T Quality ≥ {values['quality']}"
        pt_l1_label = f"$p_T^{{μ,L1}} ≥ {values['pt_l1']}$ GeV"
        pt_reco_label = f"$p_T^{{μ,offline}} ≥ {values['pt_reco']}$ GeV"

        if var == "eta":
            h_passed_EMTF = in_file.Get("EMTF_" + key + "_passed")
            h_passed_EMTF = utils.add_overflow(h_passed_EMTF)
            h_total_EMTF = in_file.Get("EMTF_" + key + "_total")
            h_total_EMTF = utils.add_overflow(h_total_EMTF)

            h_passed_BMTF = in_file.Get("BMTF_" + key + "_passed")
            h_passed_BMTF = utils.add_overflow(h_passed_BMTF)
            h_total_BMTF = in_file.Get("BMTF_" + key + "_total")
            h_total_BMTF = utils.add_overflow(h_total_BMTF)

            h_passed_OMTF = in_file.Get("OMTF_" + key + "_passed")
            h_passed_OMTF = utils.add_overflow(h_passed_OMTF)
            h_total_OMTF = in_file.Get("OMTF_" + key + "_total")
            h_total_OMTF = utils.add_overflow(h_total_OMTF)

            # Handle overlap assignment without averaging
            # For |eta| ~ 0.83 (BMTF and OMTF overlap), assign to OMTF
            for i in range(1, h_total_BMTF.GetNbinsX() + 1):
                eta_val = h_total_BMTF.GetXaxis().GetBinCenter(i)
                if 0.8 < abs(eta_val) < 0.86:
                    # Move BMTF points to OMTF
                    passed_bmtf = h_passed_BMTF.GetBinContent(i)
                    total_bmtf = h_total_BMTF.GetBinContent(i)
                    
                    # Add BMTF counts to OMTF
                    h_passed_OMTF.SetBinContent(i, h_passed_OMTF.GetBinContent(i) + passed_bmtf)
                    h_total_OMTF.SetBinContent(i, h_total_OMTF.GetBinContent(i) + total_bmtf)
                    
                    # Optionally zero out the BMTF overlap bin if you don't want to keep it
                    h_passed_BMTF.SetBinContent(i, 0)
                    h_total_BMTF.SetBinContent(i, 0)

            # For |eta| ~ 1.24 (OMTF and EMTF overlap), assign to EMTF
            for i in range(1, h_total_OMTF.GetNbinsX() + 1):
                eta_val = h_total_OMTF.GetXaxis().GetBinCenter(i)
                if 1.23 < abs(eta_val) < 1.26:
                    # Move OMTF points to EMTF
                    passed_omtf = h_passed_OMTF.GetBinContent(i)
                    total_omtf = h_total_OMTF.GetBinContent(i)
                    
                    # Add OMTF counts to EMTF
                    h_passed_EMTF.SetBinContent(i, h_passed_EMTF.GetBinContent(i) + passed_omtf)
                    h_total_EMTF.SetBinContent(i, h_total_EMTF.GetBinContent(i) + total_omtf)

                    # Optionally zero out the OMTF overlap bin
                    h_passed_OMTF.SetBinContent(i, 0)
                    h_total_OMTF.SetBinContent(i, 0)

            # Recreate TEfficiency objects after modification of histograms
            h_eff_EMTF = ROOT.TEfficiency(h_passed_EMTF, h_total_EMTF)
            h_eff_BMTF = ROOT.TEfficiency(h_passed_BMTF, h_total_BMTF)
            h_eff_OMTF = ROOT.TEfficiency(h_passed_OMTF, h_total_OMTF)

            markers = {
                "BMTF": "o",
                "OMTF": "s",
                "EMTF": "^",
            }
            colors = {
                "BMTF": "#f89c20",
                "OMTF": "#e42536",
                "EMTF": "#964a8b",
            }

            # Pack the TEff objects into a dict for iteration
            teff_map = {
                "BMTF": h_eff_BMTF,
                "OMTF": h_eff_OMTF,
                "EMTF": h_eff_EMTF,
            }

            # Loop and plot each TF
            for tf in ["BMTF", "OMTF", "EMTF"]:
                teff = teff_map.get(tf)
                if not teff:
                    continue
                x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(teff)
                if x is None:
                    continue
                valid = (y > 0) & (y <= 1)

                ax.errorbar(
                    x[valid], y[valid],
                    xerr=xerr[valid],
                    yerr=[yerr_low[valid], yerr_up[valid]],
                    fmt=markers[tf],
                    color=colors.get(tf),
                    capsize=2,
                    label=legend_labels.get(tf, tf),
                )

            # ------------------------------------------------------------------
            # Style and labels for eta plot
            ax.set_ylim(0, 1.1)
            ax.set_xlabel(vars_title[var])
            ax.set_ylabel("Efficiency")
            ax.grid(True)

            # Legend (only BMTF/OMTF/EMTF will be present)
            ax.legend(title="", loc="lower right")

            # CMS & dataset labels
            utils.add_cms_label(ax, args.legend, loc=0, text="Internal")
            # place quality and pT text (same layout as before)
            ax.text(0.62, 0.38, quality_label, transform=ax.transAxes)
            ax.text(0.62, 0.31, pt_l1_label, transform=ax.transAxes)
            ax.text(0.62, 0.24, pt_reco_label, transform=ax.transAxes)

            # x-axis limits for eta
            ax.set_xlim(-2.5, 2.5)
        
        else:
            # List of trigger subsystems to loop over
            subsystems = {
                "uGMT": "D",
                "BMTF": "o",
                "OMTF": "s",
                "EMTF": "^",
            }

            # Plot all TF efficiencies
            for tf, marker in subsystems.items():
                h_passed = utils.add_overflow(in_file.Get(f"{tf}_{key}_passed"))
                h_total = utils.add_overflow(in_file.Get(f"{tf}_{key}_total"))
                if not h_passed or not h_total:
                    continue
                h_eff = ROOT.TEfficiency(h_passed, h_total)
                x, y, yerr_low, yerr_up, xerr = utils.efficiency_to_vector(h_eff)
                valid = (y > 0) & (y <= 1)
                ax.errorbar(
                    x[valid], y[valid],
                    xerr=xerr[valid],
                    yerr=[yerr_low[valid], yerr_up[valid]],
                    fmt=marker,
                    capsize=2,
                    label=legend_labels.get(tf, tf),
                )

            # ------------------------------------------------------------------
            # Style and labels
            ax.set_ylim(0, 1.2)
            ax.set_xlabel(vars_title[var])
            ax.set_ylabel("Efficiency")
            ax.legend(title="", loc="lower right")
            ax.grid(True)

            # CMS & dataset labels
            utils.add_cms_label(ax, args.legend, loc=2, text="Internal")
            if var == "phi":
                ax.text(0.62, 0.44, quality_label, transform=ax.transAxes)
                ax.text(0.62, 0.37, pt_l1_label, transform=ax.transAxes)
                ax.text(0.62, 0.30, pt_reco_label, transform=ax.transAxes)
            else:
                ax.text(0.62, 0.37, quality_label, transform=ax.transAxes)
                ax.text(0.62, 0.30, pt_l1_label, transform=ax.transAxes)
            # ------------------------------------------------------------------
            # Axis scaling
            if var == "pt":
                ax.set_xscale("log")
                ax.set_xlim(1, 2000)
            elif var == "pt2":
                ax.set_xlim(0, 60)
            elif var == "phi":
                ax.set_xlim(-3.5, 3.5)
            # ------------------------------------------------------------------
        # Save plots
        utils.save_canvas(fig, output_dir, "eff", key)
        ax.clear()

# ----------------------------------------------------------------------
# 2D efficiency (eta vs phi)
for wp in WPs:
    fig2, ax2 = plt.subplots()
    key = f"{wp}_phi_eta"
    h_passed_uGMT = in_file.Get(f"uGMT_{key}_passed")
    h_total_uGMT = in_file.Get(f"uGMT_{key}_total")
    h_eff_uGMT = ROOT.TEfficiency(h_passed_uGMT, h_total_uGMT)
    temp_canvas = ROOT.TCanvas("temp", "temp", 800, 600)
    h_eff_uGMT.Draw("colz")
    temp_canvas.Update()
    eff_histogram = h_eff_uGMT.GetPaintedHistogram()
        
    # Get the efficiency values and bin information
    nx = eff_histogram.GetNbinsX()
    ny = eff_histogram.GetNbinsY()
    efficiency = np.zeros((ny, nx))
    x_edges = np.zeros(nx + 1)
    y_edges = np.zeros(ny + 1)

    for i in range(1, nx + 1):
        x_edges[i-1] = eff_histogram.GetXaxis().GetBinLowEdge(i)
        for j in range(1, ny + 1):
            y_edges[j-1] = eff_histogram.GetYaxis().GetBinLowEdge(j)
            efficiency[j-1, i-1] = eff_histogram.GetBinContent(i, j)
        
        # Set the last edges
        x_edges[-1] = eff_histogram.GetXaxis().GetBinUpEdge(nx)
        y_edges[-1] = eff_histogram.GetYaxis().GetBinUpEdge(ny)

    mask_index = np.searchsorted(y_edges, 3.14, side='right')
    efficiency_masked = efficiency.copy()
    efficiency_masked[mask_index-1:, :] = np.nan  # Set bins above 3.14 to NaN

    hep.hist2dplot(efficiency_masked.T, x_edges, y_edges, ax=ax2, cbar=True, flow='none')

    # h_mpl.plot(ax=ax2, cbarextend=True, flow='none')
    fig2.get_axes()[-1].set_ylabel("Efficiency", fontsize=22)
    utils.add_cms_label(ax2, args.legend, loc=0, text="Internal")
    ax2.set_xlabel(r"$\eta^{\mu,offline}$")
    ax2.set_ylabel(r"$\phi^{\mu,offline}$ [rad]")

    ax2.set_xlim(-2.4, 2.4)
    ax2.set_ylim(-3.14, 3.5)

    # Add vertical lines
    line_positions = [-1.24, -0.83, 0.83, 1.24]
    for pos in line_positions:
        ax2.axvline(x=pos, color='black', linestyle='--', linewidth=2, alpha=0.7)
    
    # Add text annotations
    text_props = {'fontsize': 14, 'transform': ax2.transAxes}
    ax2.text(0.464, 0.95, "BMTF", **text_props)
    ax2.text(0.25, 0.95, "OMTF", **text_props)
    ax2.text(0.08, 0.95, "EMTF", **text_props)
    ax2.text(0.68, 0.95, "OMTF", **text_props)
    ax2.text(0.85, 0.95, "EMTF", **text_props)

    utils.save_canvas(fig2, output_dir, "eff", key)
    plt.close(fig2)
    temp_canvas.Close()
    del temp_canvas


# ----------------------------------------------------------------------
in_file.Close()