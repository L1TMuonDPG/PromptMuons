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

WPs = ["SingleMu_22"]

vars_title = {
    #"eta": "#eta_{Reco}",
    #"phi": "#phi_{Reco}",
    "pt": "p^{Reco}_{T} [GeV]",
    "pt2": "p^{Reco}_{T} [GeV]",
    #"nPV": "Number of Vertices"
}

# Create canvas, receive values for margins
c, L, R, T, B = utils.create_canvas("c")
dataset_legend, dataset_x1 = get_dataset_legend(args.legend, R)

for var in vars_title:
    key = "_" + var

    c.SetLogx(0)
    # Retrieve and draw histogram for uGMT
    h_passed_uGMT = in_file.Get("uGMT_" + key +"_passed")
    h_passed_uGMT = utils.add_overflow(h_passed_uGMT)
    h_total_uGMT = in_file.Get("uGMT_" + key + "_total")
    h_total_uGMT = utils.add_overflow(h_total_uGMT)
    h_misid_uGMT = ROOT.TEfficiency(h_passed_uGMT,h_total_uGMT)
    draw_hist(h_misid_uGMT, CMS_color_0, 20, "")

    # Add label and set the limits for the axes
    h_misid_uGMT.SetTitle(";" + vars_title[var] + ";Charge misidentification")
    c.Update()
    graph = h_misid_uGMT.GetPaintedGraph() 
    graph.SetMinimum(0)
    graph.SetMaximum(1.2)
    if var == "pt":
        c.SetLogx(1)
        graph.GetXaxis().SetLimits(1,1000)
        graph.GetXaxis().SetTitleOffset(1.3)
    if var == "pt2":
        graph.GetXaxis().SetLimits(0,60)
    if var == "nPV":
        graph.GetXaxis().SetLimits(0,70)
    c.Update()

    # Retrieve and draw histogram for BMTF
    h_passed_BMTF = in_file.Get("BMTF_" + key + "_passed")
    h_passed_BMTF = utils.add_overflow(h_passed_BMTF)
    h_total_BMTF = in_file.Get("BMTF_" + key + "_total")
    h_total_BMTF = utils.add_overflow(h_total_BMTF)
    h_misid_BMTF = ROOT.TEfficiency(h_passed_BMTF,h_total_BMTF)
    draw_hist(h_misid_BMTF, CMS_color_1, 21, "same")

    # Retrieve and draw histogram for OMTF
    h_passed_OMTF = in_file.Get("OMTF_" + key + "_passed")
    h_passed_OMTF = utils.add_overflow(h_passed_OMTF)
    h_total_OMTF = in_file.Get("OMTF_" + key + "_total")
    h_total_OMTF = utils.add_overflow(h_total_OMTF)
    h_misid_OMTF = ROOT.TEfficiency(h_passed_OMTF,h_total_OMTF)
    draw_hist(h_misid_OMTF, CMS_color_2, 22, "same")

    # Retrieve and draw histogram for EMTF
    h_passed_EMTF = in_file.Get("EMTF_" + key + "_passed")
    h_passed_EMTF = utils.add_overflow(h_passed_EMTF)
    h_total_EMTF = in_file.Get("EMTF_" + key + "_total")
    h_total_EMTF = utils.add_overflow(h_total_EMTF)
    h_misid_EMTF = ROOT.TEfficiency(h_passed_EMTF,h_total_EMTF)
    draw_hist(h_misid_EMTF, CMS_color_5, 23, "same")

    # Create legend
    leg = ROOT.TLegend(0.57, 0.9, 0.8, 0.65)
    leg.SetFillStyle(0)
    leg.AddEntry(h_misid_uGMT,"|#eta| #leq 2.4","lep")
    leg.AddEntry(h_misid_BMTF,"|#eta| #leq 0.83","lep")
    leg.AddEntry(h_misid_OMTF,"0.83 < |#eta| #leq 1.24","lep")
    leg.AddEntry(h_misid_EMTF,"1.24 < |#eta| #leq 2.4","lep")
    leg.Draw()

    latex.SetTextSize(0.04)
    latex.SetTextFont(42)
    latex.DrawLatexNDC(0.6,0.6,"L1T Quality #geq 12")
    utils.add_dataset_legend(dataset_x1, dataset_legend)
    utils.add_cms_label_in(L,T)

    c.SaveAs(output_dir + "misid" + key + ".png")
    c.SaveAs(output_dir + "misid" + key + ".pdf")

## eta vs phi
ROOT.gStyle.SetPadTickY(1)
# Create canvas, receive values for margins
c2, L, R, T, B = utils.create_canvas("c2", 0.11, 0.15)
dataset_legend, dataset_x1 = get_dataset_legend(args.legend, R)

key2 = "_phi_eta"

# Retrieve and draw histogram for uGMT
h_misid_uGMT = in_file.Get("h_misid_phi_etauGMT_" )
h_misid_uGMT.SetTitle(";#eta_{Reco};#phi_{Reco} [rad]; Charge misidentification")
h_misid_uGMT.Draw("colz")
c2.Update()

# Set limits for X and Y axes
h_misid_uGMT.GetPaintedHistogram().GetYaxis().SetRangeUser(-3.14, 3.6)
h_misid_uGMT.GetPaintedHistogram().GetXaxis().SetRangeUser(-2.4, 2.4)
c2.Update()

# Move palette legend
palette = h_misid_uGMT.GetPaintedHistogram().GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.865)  # New left x-coordinate of the palette (move right)
palette.SetX2NDC(0.9)    # New right x-coordinate of the palette
palette.SetY1NDC(0.1)    # New bottom y-coordinate of the palette
palette.SetY2NDC(0.9)    # New top y-coordinate of the palette
c2.Update()

# Latex
utils.add_dataset_legend(dataset_x1, dataset_legend)
utils.add_cms_label_out(L,T)

line = ROOT.TLine(-1.24, -3.14, -1.24, 3.55)
line.SetLineWidth(2)
line.SetLineColor(ROOT.kRed)
line.SetLineStyle(9)
line.Draw("same")
line1 = ROOT.TLine(-0.83, -3.14, -0.83, 3.55)
line1.SetLineWidth(2)
line1.SetLineColor(ROOT.kRed)
line1.SetLineStyle(9)
line1.Draw("same")
line2 = ROOT.TLine(0.83, -3.14, 0.83, 3.55)
line2.SetLineWidth(2)
line2.SetLineColor(ROOT.kRed)
line2.SetLineStyle(9)
line2.Draw("same")
line3 = ROOT.TLine(1.24, -3.14, 1.24, 3.55)
line3.SetLineWidth(2)
line3.SetLineColor(ROOT.kRed)
line3.SetLineStyle(9)
line3.Draw("same")

latex.SetTextSize(0.021)
latex.SetTextFont(42)
latex.DrawLatexNDC(0.451,0.87,"BMTF")
latex.DrawLatexNDC(0.293,0.87,"OMTF")
latex.DrawLatexNDC(0.185,0.87,"EMTF")
latex.DrawLatexNDC(0.61,0.87,"OMTF")
latex.DrawLatexNDC(0.725,0.87,"EMTF")

c2.SaveAs(output_dir + "misid" + key2 + ".png")
c2.SaveAs(output_dir + "misid" + key2 + ".pdf")

# Close input file
in_file.Close()

# I was curious if we receive the same result using reco eta/phi vs l1 eta/phi. Unnecessary for the DPG plots

##l1 eta vs l1 phi

# h_l1_misid_uGMT = in_file.Get("h_misid_l1_phi_etauGMT_" )
# h_l1_misid_uGMT.SetTitle(";L1#eta;L1#phi [rad]; Charge misidentification")
# h_l1_misid_uGMT.Draw("colz")
# latex.SetTextSize(0.04)
# latex.DrawLatexNDC(dataset_x2,0.91,dataset_legend)
# latex.SetTextSize(0.045)
# latex.DrawLatexNDC(0.11, 0.91, "#font[61]{CMS}")
# latex.SetTextSize(0.0346)
# latex.DrawLatexNDC(0.205, 0.91, "#font[52]{Internal}")
# line = ROOT.TLine(-1.24, -4, -1.24, 4)
# line.SetLineWidth(2)
# line.SetLineColor(ROOT.kRed)
# line.SetLineStyle(9)
# line.Draw("same")
# line1 = ROOT.TLine(-0.83, -4, -0.83, 4)
# line1.SetLineWidth(2)
# line1.SetLineColor(ROOT.kRed)
# line1.SetLineStyle(9)
# line1.Draw("same")
# line2 = ROOT.TLine(0.83, -4, 0.83, 4)
# line2.SetLineWidth(2)
# line2.SetLineColor(ROOT.kRed)
# line2.SetLineStyle(9)
# line2.Draw("same")
# line3 = ROOT.TLine(1.24, -4, 1.24, 4)
# line3.SetLineWidth(2)
# line3.SetLineColor(ROOT.kRed)
# line3.SetLineStyle(9)
# line3.Draw("same")

# latex.SetTextSize(0.021)
# latex.DrawLatexNDC(0.46,0.87,"BMTF")
# latex.DrawLatexNDC(0.30,0.87,"OMTF")
# latex.DrawLatexNDC(0.18,0.87,"EMTF")
# latex.DrawLatexNDC(0.605,0.87,"OMTF")
# latex.DrawLatexNDC(0.73,0.87,"EMTF")
# c2.SaveAs(output_dir + "misid_l1" + key2 + ".png")
# c2.SaveAs(output_dir + "misid_l1" + key2 + ".pdf")

# #Difference of eta_phi reco vs eta_phi L1

# # Convert TEfficiency histograms to TH2F histograms
# h_hist1 = h_misid_uGMT.CreateHistogram()
# h_hist2 = h_l1_misid_uGMT.CreateHistogram()

# hist_difference = h_hist1.Clone("hist_difference")
# hist_difference.Add(h_hist2, -1)
# hist_difference.SetTitle(";#eta;#phi [rad]; Charge misidentification")
# hist_difference.Draw("colz")
# latex.SetTextSize(0.04)
# latex.DrawLatexNDC(dataset_x2,0.91,dataset_legend)
# latex.SetTextSize(0.045)
# latex.DrawLatexNDC(0.11, 0.91, "#font[61]{CMS}")
# latex.SetTextSize(0.0346)
# latex.DrawLatexNDC(0.205, 0.91, "#font[52]{Internal}")
# line = ROOT.TLine(-1.24, -4, -1.24, 4)
# line.SetLineWidth(2)
# line.SetLineColor(ROOT.kBlack)
# line.SetLineStyle(9)
# line.Draw("same")
# line1 = ROOT.TLine(-0.83, -4, -0.83, 4)
# line1.SetLineWidth(2)
# line1.SetLineColor(ROOT.kBlack)
# line1.SetLineStyle(9)
# line1.Draw("same")
# line2 = ROOT.TLine(0.83, -4, 0.83, 4)
# line2.SetLineWidth(2)
# line2.SetLineColor(ROOT.kBlack)
# line2.SetLineStyle(9)
# line2.Draw("same")
# line3 = ROOT.TLine(1.24, -4, 1.24, 4)
# line3.SetLineWidth(2)
# line3.SetLineColor(ROOT.kBlack)
# line3.SetLineStyle(9)
# line3.Draw("same")

# latex.SetTextSize(0.021)
# latex.DrawLatexNDC(0.46,0.87,"BMTF")
# latex.DrawLatexNDC(0.30,0.87,"OMTF")
# latex.DrawLatexNDC(0.18,0.87,"EMTF")
# latex.DrawLatexNDC(0.605,0.87,"OMTF")
# latex.DrawLatexNDC(0.73,0.87,"EMTF")
# c2.SaveAs(output_dir + "misid_difference.png")