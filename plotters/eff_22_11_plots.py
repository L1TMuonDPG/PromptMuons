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

WPs = ["SingleMu1_22","SingleMu2_11"]

wp_values = {
    "SingleMu1_22": {"quality": 12, "pt_l1": 22, "pt_reco": 26},
    "SingleMu2_11": {"quality": 14, "pt_l1": 11, "pt_reco": 15}
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
    key="_" + var
    c.SetLogx(0)

    # Retrieve and draw histogram for BMTF for SingleMu1_22
    h_passed_BMTF_1 = in_file.Get("BMTF_SingleMu1_22" + key + "_passed")
    h_passed_BMTF_1 = utils.add_overflow(h_passed_BMTF_1)
    h_total_BMTF_1 = in_file.Get("BMTF_SingleMu1_22" + key + "_total")
    h_total_BMTF_1 = utils.add_overflow(h_total_BMTF_1)
    h_eff_BMTF_1 = ROOT.TEfficiency(h_passed_BMTF_1,h_total_BMTF_1)
    draw_hist(h_eff_BMTF_1, CMS_color_0, 20, "")

    # Add label and set the limits for the axes
    h_eff_BMTF_1.SetTitle(";" + vars_title[var] + ";Efficiency")
    c.Update()
    graph = h_eff_BMTF_1.GetPaintedGraph() 
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

    # Retrieve and draw histogram for BMTF for SingleMu2_11
    h_passed_BMTF_2 = in_file.Get("BMTF_SingleMu2_11" + key + "_passed")
    h_passed_BMTF_2 = utils.add_overflow(h_passed_BMTF_2)
    h_total_BMTF_2 = in_file.Get("BMTF_SingleMu2_11" + key + "_total")
    h_total_BMTF_2 = utils.add_overflow(h_total_BMTF_2)
    h_eff_BMTF_2 = ROOT.TEfficiency(h_passed_BMTF_2,h_total_BMTF_2)
    draw_hist(h_eff_BMTF_2, ROOT.kRed, 21, "same")

    # Create legend
    if var == "eta" or var == "phi":
        leg = ROOT.TLegend(0.17,0.13,0.8,0.23)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_BMTF_1,"p^{#mu,L1}_{T} #geq 22, p^{#mu, offline}_{T} #geq 26, L1T Quality #geq 12","lep")
        leg.AddEntry(h_eff_BMTF_2,"p^{#mu,L1}_{T} #geq 11, p^{#mu, offline}_{T} #geq 15, L1T Quality #geq 14","lep")
        if var != "eta":
            latex.SetTextFont(42)
            latex.SetTextSize(0.035)
            latex.DrawLatexNDC(0.75, 0.83, "|#eta| #leq 0.83")
    else:
        leg = ROOT.TLegend(0.43,0.13,0.8,0.23)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_BMTF_1,"p^{#mu,L1}_{T} #geq 22, L1T Quality #geq 12","lep")
        leg.AddEntry(h_eff_BMTF_2,"p^{#mu,L1}_{T} #geq 11, L1T Quality #geq 14","lep")
        latex.SetTextFont(42)
        latex.SetTextSize(0.035)
        latex.DrawLatexNDC(0.64, 0.25, "|#eta| #leq 0.83")
    leg.Draw()
        
    utils.add_dataset_legend(dataset_x1, dataset_legend)
    utils.add_cms_label_in(L,T)

    c.SaveAs(output_dir + "eff_22_11" + key + ".png")
    c.SaveAs(output_dir + "eff_22_11" + key + ".pdf")