import ROOT
import argparse
import utils
import os

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gStyle.SetTitleOffset(1.5,"Z")
ROOT.gStyle.SetPalette(ROOT.kBlueGreenYellow)
latex = ROOT.TLatex()
latex.SetTextSize(0.04)
latex.SetTextFont(42)
ROOT.gStyle.SetLegendTextSize(0.035)

# Colors
color_0 = ROOT.TColor.GetColor(87,144,252) #blue
color_1 = ROOT.TColor.GetColor(248,156,32) #orange
color_2 = ROOT.TColor.GetColor(228,37,54) #red
color_3 = ROOT.TColor.GetColor(150,74,139) #purple
color_4 = ROOT.TColor.GetColor(156,156,161) #gray
color_5 = ROOT.TColor.GetColor(122,33,221) #purple

#parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--legend', type=str, help='dataset legend')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('-i', type=str, help='input dir dir')
args = parser.parse_args()

if args.legend == '2024B':
    dataset_legend ='2024B (0.13 fb^{-1})'
    dataset_x1=0.64
    dataset_x2=0.59
elif args.legend == '2024C':
    dataset_legend ='2024C (7.24 fb^{-1})'
    dataset_x1=0.64
    dataset_x2=0.59
elif args.legend == '2024D':
    dataset_legend ='2024D (7.96 fb^{-1})'
    dataset_x1=0.64
    dataset_x2=0.59
elif args.legend == '2024E':
    dataset_legend ='2024E (11.32 fb^{-1})'
    dataset_x1=0.62
    dataset_x2=0.57
elif args.legend == '2024F':
    dataset_legend ='2024F (27.76 fb^{-1})'
    dataset_x1=0.62
    dataset_x2=0.57
elif args.legend == '2024G':
    dataset_legend ='2024G (37.77 fb^{-1})'
    dataset_x1=0.62
    dataset_x2=0.57
elif args.legend == '2024H':
    dataset_legend ='2024H (5.44 fb^{-1})'
    dataset_x1=0.64
    dataset_x2=0.59
elif args.legend == '2024I':
    dataset_legend ='2024I (11.47 fb^{-1})'
    dataset_x1=0.62
    dataset_x2=0.57
elif args.legend == '2024':
    dataset_legend ='109 fb^{-1} (13.6 TeV)'
    dataset_x1=0.62
    dataset_x2=0.57
else:
    dataset_legend = args.legend
    dataset_x1=0.80
    dataset_x2=0.75
output_dir = args.o
input_dir = args.i

## merge root files
# utils.merge_root_files(input_dir)

in_file = ROOT.TFile(input_dir + "merged_total.root","READ")
c = ROOT.TCanvas("c","c",800,800)
# c.SetLeftMargin(0.11)
# c.SetRightMargin(0.15)
c.SetGrid()

WPs = ["L1Mu1_11","L1Mu2_11"]

wp_values = {
    "L1Mu1_11": {"quality": 12, "pt_l1": 11, "pt_reco": 15},
    "L1Mu2_11": {"quality": 14, "pt_l1": 11, "pt_reco": 15}
}

vars_title = {
    "eta": "#eta_{Reco}",
    "phi": "#phi_{Reco}",
    "pt": "p^{Reco}_{T} [GeV]",
    "pt2": "p^{Reco}_{T} [GeV]",
    #"nPV": "Number of Vertices"
}

for var in vars_title:
    key="_" + var
    c.SetLogx(0)

    h_passed_BMTF_1 = in_file.Get("BMTF_SingleMu1_11" + key + "_passed")
    h_passed_BMTF_1 = utils.add_overflow(h_passed_BMTF_1)
    h_total_BMTF_1 = in_file.Get("BMTF_SingleMu1_11" + key + "_total")
    h_total_BMTF_1 = utils.add_overflow(h_total_BMTF_1)
    h_eff_BMTF_1 = ROOT.TEfficiency(h_passed_BMTF_1,h_total_BMTF_1)
    h_eff_BMTF_1.SetMarkerColor(color_0)
    h_eff_BMTF_1.SetLineColor(color_0)
    h_eff_BMTF_1.SetMarkerStyle(20)
    h_eff_BMTF_1.Draw()
    h_eff_BMTF_1.SetTitle(";" + vars_title[var] + ";Efficiency")
    c.Update()
    graph = h_eff_BMTF_1.GetPaintedGraph() 
    graph.SetMinimum(0)
    graph.SetMaximum(1.1)
    if var == "pt":
        c.SetLogx(1)
        graph.GetXaxis().SetLimits(1,1000)
        graph.GetXaxis().SetTitleOffset(1.3)
    c.Update()

    h_passed_BMTF_2 = in_file.Get("BMTF_SingleMu2_11" + key + "_passed")
    h_passed_BMTF_2 = utils.add_overflow(h_passed_BMTF_2)
    h_total_BMTF_2 = in_file.Get("BMTF_SingleMu2_11" + key + "_total")
    h_total_BMTF_2 = utils.add_overflow(h_total_BMTF_2)
    h_eff_BMTF_2 = ROOT.TEfficiency(h_passed_BMTF_2,h_total_BMTF_2)
    # h_eff_BMTF_2.SetMarkerColor(ROOT.kGreen+2)
    # h_eff_BMTF_2.SetLineColor(ROOT.kGreen+2)
    h_eff_BMTF_2.SetMarkerColor(color_1)
    h_eff_BMTF_2.SetLineColor(color_1)
    h_eff_BMTF_2.SetMarkerStyle(21)
    h_eff_BMTF_2.Draw("same")

    leg = ROOT.TLegend(0.62,0.13,0.8,0.23)
    leg.SetFillStyle(0)
    leg.AddEntry(h_eff_BMTF_1,"Quality #geq 12","lep")
    leg.AddEntry(h_eff_BMTF_2,"Quality #geq 14","lep")
    leg.Draw()

    latex.SetTextSize(0.04)
    latex.DrawLatexNDC(dataset_x1,0.91,dataset_legend)
    latex.SetTextSize(0.035)
    if var == "eta":
        # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
        latex.DrawLatexNDC(0.64, 0.31, "p^{#mu,L1}_{T} #geq 11 GeV")
        latex.DrawLatexNDC(0.64, 0.25, "p^{#mu,Reco}_{T} #geq 15 GeV")
    elif var == "phi" or var == "nPV":
        latex.DrawLatexNDC(0.64, 0.31, "p^{#mu,L1}_{T} #geq 11 GeV")
        latex.DrawLatexNDC(0.64, 0.25, "p^{#mu,Reco}_{T} #geq 15 GeV")
        latex.DrawLatexNDC(0.68, 0.37, "|#eta| #leq 0.83")
    else:
        latex.DrawLatexNDC(0.64, 0.25, "p^{#mu,L1}_{T} #geq 11 GeV")
        latex.DrawLatexNDC(0.68, 0.31, "|#eta| #leq 0.83")
    latex.SetTextSize(0.045)
    latex.DrawLatexNDC(0.1, 0.91, "#font[61]{CMS}")
    latex.SetTextSize(0.0346)
    latex.DrawLatexNDC(0.195, 0.91, "#font[52]{Internal}")

    c.SaveAs(output_dir + "eff_11_doublequal" + key + ".png")
    c.SaveAs(output_dir + "eff_11_doublequal" + key + ".pdf")