import ROOT
import argparse
import os
import utils
from utils import *

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--legend', type=str, help='dataset legend')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('-i', type=str, help='input dir dir')
args = parser.parse_args()

# Pass arguments
output_dir = args.o
input_dir = args.i
# utils.merge_root_files(input_dir)

in_file = ROOT.TFile(input_dir + "merged_total.root","READ")

WPs = ["L1Mu22","L1Mu15","L1Mu7","L1Mu3"]

TFs = {
    "uGMT": "|#eta| #leq 2.4",
    "BMTF": "|#eta| #leq 0.83",
    "OMTF": " 0.83 #leq |#eta| #leq 1.24",
    "EMTF": " 1.24 #leq |#eta| #leq 2.4"
}

wp_values = {
    "L1Mu22": {"quality": 12, "pt_l1": 22, "pt_reco": 26},
    "L1Mu15": {"quality": 8, "pt_l1": 15, "pt_reco": 19},
    "L1Mu7": {"quality": 4, "pt_l1": 7, "pt_reco": 11},
    "L1Mu3": {"quality": 0, "pt_l1": 3, "pt_reco": 7}
}

vars_title = {
    "eta": "#eta_{Reco}",
    "phi": "#phi_{Reco}",
    "pt": "p^{#mu,offline}_{T} [GeV]",
    "pt2": "p^{#mu,offline}_{T} [GeV]",
    #"nPV": "Number of Vertices"
}

# Create canvas, receive values for margins
c, L, R, T, B = utils.create_canvas("c")
dataset_legend, dataset_x1 = get_dataset_legend(args.legend, R)

for var in vars_title:
    for tf in TFs:
        key="_" + var
        c.SetLogx(0)

        # Retrieve and draw histogram for {tf} for L1Mu22
        h_passed_22 = in_file.Get(f"{tf}_L1Mu22_22" + key + "_passed")
        h_passed_22 = utils.add_overflow(h_passed_22)
        h_total_22 = in_file.Get(f"{tf}_L1Mu22_22" + key + "_total")
        h_total_22 = utils.add_overflow(h_total_22)
        h_eff_22 = ROOT.TEfficiency(h_passed_22,h_total_22)
        draw_hist(h_eff_22, CMS_color_0, 20, "")

        # Add label and set the limits for the axes
        h_eff_22.SetTitle(";" + vars_title[var] + ";Efficiency")
        c.Update()
        graph = h_eff_22.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.2)
        if var == "pt":
            c.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "pt2":
            graph.GetXaxis().SetLimits(0,60)
            graph.GetXaxis().SetTitleOffset(1.2)
        c.Update()

        # Retrieve and draw histogram for {tf} for L1Mu15
        h_passed_15 = in_file.Get(f"{tf}_L1Mu15_15" + key + "_passed")
        h_passed_15 = utils.add_overflow(h_passed_15)
        h_total_15 = in_file.Get(f"{tf}_L1Mu15_15" + key + "_total")
        h_total_15 = utils.add_overflow(h_total_15)
        h_eff_15 = ROOT.TEfficiency(h_passed_15,h_total_15)
        draw_hist(h_eff_15, CMS_color_1, 21, "same")

        # Retrieve and draw histogram for {tf} for L1Mu7
        h_passed_7 = in_file.Get(f"{tf}_L1Mu7_7" + key + "_passed")
        h_passed_7 = utils.add_overflow(h_passed_7)
        h_total_7 = in_file.Get(f"{tf}_L1Mu7_7" + key + "_total")
        h_total_7 = utils.add_overflow(h_total_7)
        h_eff_7 = ROOT.TEfficiency(h_passed_7,h_total_7)
        draw_hist(h_eff_7, CMS_color_2, 22, "same")

        # Retrieve and draw histogram for {tf} for L1Mu3
        h_passed_3 = in_file.Get(f"{tf}_L1Mu3_3" + key + "_passed")
        h_passed_3 = utils.add_overflow(h_passed_3)
        h_total_3 = in_file.Get(f"{tf}_L1Mu3_3" + key + "_total")
        h_total_3 = utils.add_overflow(h_total_3)
        h_eff_3 = ROOT.TEfficiency(h_passed_3,h_total_3)
        draw_hist(h_eff_3, CMS_color_3, 23, "same")

        # Create legend
        if var == "pt" or var == "pt2":
            leg = ROOT.TLegend(0.39,0.13,0.70,0.33)
            leg.SetFillStyle(0)
            leg.AddEntry(h_eff_22,"p^{#mu,L1}_{T} #geq 22, L1T Quality #geq 12","lep")
            leg.AddEntry(h_eff_15,"p^{#mu,L1}_{T} #geq 15, L1T Quality #geq 8","lep")
            leg.AddEntry(h_eff_7,"p^{#mu,L1}_{T} #geq 7, L1T Quality #geq 4","lep")
            leg.AddEntry(h_eff_3,"p^{#mu,L1}_{T} #geq 3, L1T Quality #geq 0","lep")
        else:
            leg = ROOT.TLegend(0.09,0.12,0.73,0.33)
            leg.SetFillStyle(0)
            leg.AddEntry(h_eff_22,"p^{#mu,L1}_{T} #geq 22, p^{#mu,offline}_{T} #geq 26, L1T Quality #geq 12","lep")
            leg.AddEntry(h_eff_15,"p^{#mu,L1}_{T} #geq 15, p^{#mu,offline}_{T} #geq 19, L1T Quality #geq 8","lep")
            leg.AddEntry(h_eff_7,"p^{#mu,L1}_{T} #geq 7, p^{#mu,offline}_{T} #geq 11, L1T Quality #geq 4","lep")
            leg.AddEntry(h_eff_3,"p^{#mu,L1}_{T} #geq 3, p^{#mu,offline}_{T} #geq 7, L1T Quality #geq 0","lep")
        leg.Draw()

        # Add text to show that the plot is for {tf} except in eta plot
        if var != "eta":
            if var == "phi":
                latex.SetTextSize(0.035)
                if tf == "uGMT" or tf == "BMTF":
                    latex.DrawLatexNDC(0.45, 0.35, TFs[tf])
                else:
                    latex.DrawLatexNDC(0.36, 0.35, TFs[tf])
            else:
                latex.SetTextSize(0.035)
                if tf == "uGMT" or tf == "BMTF":
                    latex.DrawLatexNDC(0.59, 0.35, TFs[tf])
                else:
                    latex.DrawLatexNDC(0.50, 0.35, TFs[tf])
        utils.add_dataset_legend(dataset_x1, dataset_legend)
        utils.add_cms_label_in(L,T)

        c.SaveAs(output_dir + f"eff_22_15_7_3_{tf}_{key}.png")
        c.SaveAs(output_dir + f"eff_22_15_7_3_{tf}_{key}.pdf")