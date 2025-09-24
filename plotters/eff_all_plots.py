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

WPs = ["L1Mu26_12","L1Mu22_12","L1Mu20_12","L1Mu15_12","L1Mu10_12","L1Mu7_12","L1Mu5_12","L1Mu3_12", "L1Mu26_8","L1Mu22_8","L1Mu20_8","L1Mu15_8","L1Mu10_8","L1Mu7_8","L1Mu5_8","L1Mu3_8", "L1Mu26_4","L1Mu22_4","L1Mu20_4","L1Mu15_4","L1Mu10_4","L1Mu7_4","L1Mu5_4","L1Mu3_4", "L1Mu26_0","L1Mu22_0","L1Mu20_0","L1Mu15_0","L1Mu10_0","L1Mu7_0","L1Mu5_0","L1Mu3_0"]

wp_values = {
    "L1Mu26_12": {"quality": 12, "pt_l1": 26, "pt_reco": 30},
    "L1Mu22_12": {"quality": 12, "pt_l1": 22, "pt_reco": 26},
    "L1Mu20_12": {"quality": 12, "pt_l1": 20, "pt_reco": 24},
    "L1Mu15_12": {"quality": 12, "pt_l1": 15, "pt_reco": 19},
    "L1Mu10_12": {"quality": 12, "pt_l1": 10, "pt_reco": 14},
    "L1Mu7_12": {"quality": 12, "pt_l1": 7, "pt_reco": 11},
    "L1Mu5_12": {"quality": 12, "pt_l1": 5, "pt_reco": 9},
    "L1Mu3_12": {"quality": 12, "pt_l1": 3, "pt_reco": 7},
    "L1Mu26_8": {"quality": 8, "pt_l1": 26, "pt_reco": 30},
    "L1Mu22_8": {"quality": 8, "pt_l1": 22, "pt_reco": 26},
    "L1Mu20_8": {"quality": 8, "pt_l1": 20, "pt_reco": 24},
    "L1Mu15_8": {"quality": 8, "pt_l1": 15, "pt_reco": 19},
    "L1Mu10_8": {"quality": 8, "pt_l1": 10, "pt_reco": 14},
    "L1Mu7_8": {"quality": 8, "pt_l1": 7, "pt_reco": 11},
    "L1Mu5_8": {"quality": 8, "pt_l1": 5, "pt_reco": 9},
    "L1Mu3_8": {"quality": 8, "pt_l1": 3, "pt_reco": 7},
    "L1Mu26_4": {"quality": 4, "pt_l1": 26, "pt_reco": 30},
    "L1Mu22_4": {"quality": 4, "pt_l1": 22, "pt_reco": 26},
    "L1Mu20_4": {"quality": 4, "pt_l1": 20, "pt_reco": 24},
    "L1Mu15_4": {"quality": 4, "pt_l1": 15, "pt_reco": 19},
    "L1Mu10_4": {"quality": 4, "pt_l1": 10, "pt_reco": 14},
    "L1Mu7_4": {"quality": 4, "pt_l1": 7, "pt_reco": 11},
    "L1Mu5_4": {"quality": 4, "pt_l1": 5, "pt_reco": 9},
    "L1Mu3_4": {"quality": 4, "pt_l1": 3, "pt_reco": 7},
    "L1Mu26_0": {"quality": 0, "pt_l1": 26, "pt_reco": 30},
    "L1Mu22_0": {"quality": 0, "pt_l1": 22, "pt_reco": 26},
    "L1Mu20_0": {"quality": 0, "pt_l1": 20, "pt_reco": 24},
    "L1Mu15_0": {"quality": 0, "pt_l1": 15, "pt_reco": 19},
    "L1Mu10_0": {"quality": 0, "pt_l1": 10, "pt_reco": 14},
    "L1Mu7_0": {"quality": 0, "pt_l1": 7, "pt_reco": 11},
    "L1Mu5_0": {"quality": 0, "pt_l1": 5, "pt_reco": 9},
    "L1Mu3_0": {"quality": 0, "pt_l1": 3, "pt_reco": 7},
}

vars_title = {
    "eta": "#eta_{Reco}",
    "phi": "#phi_{Reco}",
    "pt": "p^{#mu,offline}_{T} [GeV]",
    "pt2": "p^{#mu,offline}_{T} [GeV]",
}

# Create canvas, receive values for margins
c, L, R, T, B = utils.create_canvas("c")
dataset_legend, dataset_x1 = get_dataset_legend(args.legend, R)

## eff vs var
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        c.SetLogx(0)
        values = wp_values[wp]
        quality_label = f"L1T Quality #geq {values['quality']}"
        pt_l1_label = f"p^{{#mu,L1}}_{{T}} #geq {values['pt_l1']} GeV"
        pt_reco_label = f"p^{{#mu,Reco}}_{{T}} #geq {values['pt_reco']} GeV"

        if var == "eta":
            # Retrieve histograms for BMTF, OMTF, EMTF
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

            # uGMT histogram for comparison of the overlapped points
            # h_passed_uGMT = in_file.Get("uGMT_" + key + "_passed")
            # h_passed_uGMT = utils.add_overflow(h_passed_uGMT)
            # h_total_uGMT = in_file.Get("uGMT_" + key + "_total")
            # h_total_uGMT = utils.add_overflow(h_total_uGMT)
            # h_eff_uGMT = ROOT.TEfficiency(h_passed_uGMT,h_total_uGMT)
            # draw_hist(h_eff_uGMT, CMS_color_0, 20, "same")

            # Draw histograms
            draw_hist(h_eff_EMTF, CMS_color_5, 23, "")

            # Add label and set the limits for the axes
            h_eff_EMTF.SetTitle(";" + vars_title[var] + ";Efficiency")
            c.Update()
            graph = h_eff_EMTF.GetPaintedGraph() 
            graph.SetMinimum(0)
            graph.SetMaximum(1.1)
            c.Update()
            
            draw_hist(h_eff_BMTF, CMS_color_1, 21, "same")
            draw_hist(h_eff_OMTF, CMS_color_2, 22, "same")

            # Create legend
            leg = ROOT.TLegend(0.6,0.13,0.8,0.33)
            leg.SetFillStyle(0)
            leg.AddEntry(h_eff_BMTF,"|#eta| #leq 0.83","lep")
            leg.AddEntry(h_eff_OMTF,"0.83 < |#eta| #leq 1.24","lep")
            leg.AddEntry(h_eff_EMTF,"1.24 < |#eta| #leq 2.4","lep")
            leg.Draw()

            # Latex 
            utils.add_dataset_legend(dataset_x1, dataset_legend)
            latex.DrawLatexNDC(0.62, 0.48,quality_label)
            latex.DrawLatexNDC(0.62, 0.41, pt_l1_label)
            latex.DrawLatexNDC(0.62, 0.34, pt_reco_label)
            utils.add_cms_label_out(L,T)

        else:
            # Retrieve and draw histogram for uGMT
            h_passed_uGMT = in_file.Get("uGMT_" + key + "_passed")
            h_passed_uGMT = utils.add_overflow(h_passed_uGMT)
            h_total_uGMT = in_file.Get("uGMT_" + key + "_total")
            h_total_uGMT = utils.add_overflow(h_total_uGMT)
            h_eff_uGMT = ROOT.TEfficiency(h_passed_uGMT,h_total_uGMT)
            draw_hist(h_eff_uGMT, CMS_color_0, 20, "")

            # Add label and set the limits for the axes
            h_eff_uGMT.SetTitle(";" + vars_title[var] + ";Efficiency")
            c.Update()
            graph = h_eff_uGMT.GetPaintedGraph() 
            graph.SetMinimum(0)
            graph.SetMaximum(1.2)
            if var == "pt":
                c.SetLogx(1)
                graph.GetXaxis().SetLimits(1,2000)
                graph.GetXaxis().SetTitleOffset(1.3)
            if var == "pt2":
                if wp == "SingleMu2_5":
                    graph.GetXaxis().SetLimits(0,30)
                else:
                    graph.GetXaxis().SetLimits(0,60)
                graph.GetXaxis().SetTitleOffset(1.2)
            if var == "nPV":
                graph.GetXaxis().SetLimits(0,70)
            c.Update()
            
            # Retrieve and draw histogram for BMTF
            h_passed_BMTF = in_file.Get("BMTF_" + key + "_passed")
            h_passed_BMTF = utils.add_overflow(h_passed_BMTF)
            h_total_BMTF = in_file.Get("BMTF_" + key + "_total")
            h_total_BMTF = utils.add_overflow(h_total_BMTF)
            h_eff_BMTF = ROOT.TEfficiency(h_passed_BMTF,h_total_BMTF)
            draw_hist(h_eff_BMTF, CMS_color_1, 21, "same")

            # Retrieve and draw histogram for OMTF
            h_passed_OMTF = in_file.Get("OMTF_" + key + "_passed")
            h_passed_OMTF = utils.add_overflow(h_passed_OMTF)
            h_total_OMTF = in_file.Get("OMTF_" + key + "_total")
            h_total_OMTF = utils.add_overflow(h_total_OMTF)
            h_eff_OMTF = ROOT.TEfficiency(h_passed_OMTF,h_total_OMTF)
            draw_hist(h_eff_OMTF, CMS_color_2, 22, "same")

            # Retrieve and draw histogram for EMTF
            h_passed_EMTF = in_file.Get("EMTF_" + key + "_passed")
            h_passed_EMTF = utils.add_overflow(h_passed_EMTF)
            h_total_EMTF = in_file.Get("EMTF_" + key + "_total")
            h_total_EMTF = utils.add_overflow(h_total_EMTF)
            h_eff_EMTF = ROOT.TEfficiency(h_passed_EMTF,h_total_EMTF)
            draw_hist(h_eff_EMTF, CMS_color_5, 23, "same")

            # Create legend
            leg = ROOT.TLegend(0.61,0.13,0.8,0.38)
            leg.SetFillStyle(0)
            leg.AddEntry(h_eff_uGMT,"|#eta| #leq 2.4","lep")
            leg.AddEntry(h_eff_BMTF,"|#eta| #leq 0.83","lep")
            leg.AddEntry(h_eff_OMTF,"0.83 < |#eta| #leq 1.24","lep")
            leg.AddEntry(h_eff_EMTF,"1.24 < |#eta| #leq 2.4","lep")
            leg.Draw()

            # Latex
            utils.add_dataset_legend(dataset_x1, dataset_legend)
            if var == "phi" or var == "nPV":
                latex.DrawLatexNDC(0.64, 0.53, quality_label)
                latex.DrawLatexNDC(0.64, 0.46, pt_l1_label)
                latex.DrawLatexNDC(0.64, 0.39, pt_reco_label)
            else:
                latex.DrawLatexNDC(0.64, 0.44, quality_label)
                latex.DrawLatexNDC(0.64, 0.39, pt_l1_label)
            utils.add_cms_label_in(L,T)

        c.SaveAs(output_dir + "eff_" + key + ".png")
        c.SaveAs(output_dir + "eff_" + key + ".pdf")

## eta vs phi
ROOT.gStyle.SetPadTickY(1)
# Create canvas, receive values for margins
c2, L, R, T, B = utils.create_canvas("c2", 0.11, 0.15)
dataset_legend, dataset_x1 = get_dataset_legend(args.legend, R)

for wp in WPs:
    key = wp + "_phi_eta"

    # Retrieve and draw histogram for uGMT
    h_passed_uGMT = in_file.Get("uGMT_" + key + "_passed")
    h_total_uGMT =in_file.Get("uGMT_" + key + "_total")
    h_eff_uGMT = ROOT.TEfficiency(h_passed_uGMT,h_total_uGMT)
    h_eff_uGMT.SetTitle(";#eta_{Reco};#phi_{Reco} [rad];Efficiency")
    h_eff_uGMT.Draw("colz")
    c2.Update()

    # Set limits for X and Y axes
    h_eff_uGMT.GetPaintedHistogram().GetYaxis().SetRangeUser(-3.14, 3.6)
    h_eff_uGMT.GetPaintedHistogram().GetXaxis().SetRangeUser(-2.4, 2.4)
    c2.Update()

    # Move palette legend
    palette = h_eff_uGMT.GetPaintedHistogram().GetListOfFunctions().FindObject("palette")
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
    line.SetLineColor(ROOT.kBlack)
    line.SetLineStyle(9)
    line.Draw("same")
    line1 = ROOT.TLine(-0.83, -3.14, -0.83, 3.55)
    line1.SetLineWidth(2)
    line1.SetLineColor(ROOT.kBlack)
    line1.SetLineStyle(9)
    line1.Draw("same")
    line2 = ROOT.TLine(0.83, -3.14, 0.83, 3.55)
    line2.SetLineWidth(2)
    line2.SetLineColor(ROOT.kBlack)
    line2.SetLineStyle(9)
    line2.Draw("same")
    line3 = ROOT.TLine(1.24, -3.14, 1.24, 3.55)
    line3.SetLineWidth(2)
    line3.SetLineColor(ROOT.kBlack)
    line3.SetLineStyle(9)
    line3.Draw("same")

    latex.SetTextSize(0.021)
    latex.SetTextFont(42)
    latex.DrawLatexNDC(0.451,0.87,"BMTF")
    latex.DrawLatexNDC(0.293,0.87,"OMTF")
    latex.DrawLatexNDC(0.185,0.87,"EMTF")
    latex.DrawLatexNDC(0.61,0.87,"OMTF")
    latex.DrawLatexNDC(0.725,0.87,"EMTF")

    c2.SaveAs(output_dir + "eff_" + key + ".png")
    c2.SaveAs(output_dir + "eff_" + key + ".pdf")

# Close input file
in_file.Close()