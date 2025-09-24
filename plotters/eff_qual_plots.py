import ROOT
import argparse
import os
import utils
from utils import *

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--legend', type=str, help='Dataset legend')
parser.add_argument('-o', type=str, help='Output directory')
parser.add_argument('-i', type=str, help='Input directory')
args = parser.parse_args()

# Pass arguments
output_dir = args.o
input_dir = args.i
# utils.merge_root_files(input_dir)

in_file = ROOT.TFile(input_dir + "merged_total.root", "READ")

WPs = ["L1Mu22_12", "L1Mu22_13", "L1Mu22_14", "L1Mu22_15"]
# Define marker colors for each WP
marker_colors = [CMS_color_0, CMS_color_1, CMS_color_2, CMS_color_5]

vars_title = {
    "eta": "#eta_{Reco}",
    "phi": "#phi_{Reco}",
    "pt2": "p^{#mu,offline}_{T} [GeV]",
    "pt": "p^{#mu,offline}_{T} [GeV]"
}

# Create canvas, receive values for margins
c, L, R, T, B = utils.create_canvas("c")
dataset_legend, dataset_x1 = get_dataset_legend(args.legend, R)

# Loop over each variable
for var in vars_title:

    # Clear histograms list for each variable
    eff_histograms = []
    
    leg = ROOT.TLegend(0.4, 0.11, 0.83, 0.22)
    leg.SetNColumns(2)
    leg.SetFillStyle(0)

    for i, wp in enumerate(WPs):
        key = wp + "_" + var

        h_passed_BMTF = in_file.Get("BMTF_" + key + "_passed")
        h_passed_BMTF = utils.add_overflow(h_passed_BMTF)
        h_total_BMTF = in_file.Get("BMTF_" + key + "_total")
        h_total_BMTF = utils.add_overflow(h_total_BMTF)
        h_eff_BMTF = ROOT.TEfficiency(h_passed_BMTF, h_total_BMTF)
        marker_color = marker_colors[i % len(marker_colors)]  # Cycle through colors
        h_eff_BMTF.SetMarkerColor(marker_color)
        h_eff_BMTF.SetLineColor(marker_color)
        h_eff_BMTF.SetMarkerStyle(20 + i)  # Vary marker style
        h_eff_BMTF.SetTitle(";" + vars_title[var] + ";Efficiency")

        eff_histograms.append(h_eff_BMTF)

        # Generate legend entry label
        quality_threshold = 12 + i
        legend_entry_label = "Quality #geq {}".format(quality_threshold)

        # Add entry to legend
        leg.AddEntry(h_eff_BMTF, legend_entry_label, "lep")

    # Draw histograms for current variable
    c.cd()
    eff_histograms[0].Draw()
    for hist in eff_histograms[1:]:
        hist.Draw("same")

    # Draw legend and additional text
    leg.Draw()    
    utils.add_dataset_legend(dataset_x1, dataset_legend)
    
    latex.SetTextSize(0.035)
    latex.SetTextFont(42)
    latex.DrawLatexNDC(0.52, 0.23, "p^{#mu,L1}_{T} #geq 22 GeV")
    
    c.Update() 
    if var == "pt" or var == "pt2":# Ensure canvas is updated before modifying histogram settings
        eff_histograms[0].GetPaintedGraph().GetYaxis().SetRangeUser(0, 1.2)
        eff_histograms[0].GetPaintedGraph().GetXaxis().SetTitleOffset(1.2)
        utils.add_cms_label_in(L,T)
        if var == "pt":
            eff_histograms[0].GetPaintedGraph().GetXaxis().SetRangeUser(10, 160)
        else:
            eff_histograms[0].GetPaintedGraph().GetXaxis().SetRangeUser(0, 60)
    else:
        eff_histograms[0].GetPaintedGraph().GetYaxis().SetRangeUser(0, 1.1)
        utils.add_cms_label_out(L,T)
        if var == "eta":
            eff_histograms[0].GetPaintedGraph().GetXaxis().SetRangeUser(-0.9, 0.9)

    # Save canvas
    c.SaveAs(output_dir + "eff_qual_" + var + ".png")
    c.SaveAs(output_dir + "eff_qual_" + var + ".pdf")

# Close input file
in_file.Close()

