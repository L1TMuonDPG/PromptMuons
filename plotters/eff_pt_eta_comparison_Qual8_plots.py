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

WPs = {
    "L1Mu26": {"L1": "p^{#mu,L1}_{T} #geq 26", "Reco": "p^{#mu,offline}_{T} #geq 30"},
    "L1Mu22": {"L1": "p^{#mu,L1}_{T} #geq 22", "Reco": "p^{#mu,offline}_{T} #geq 26"},
    "L1Mu20": {"L1": "p^{#mu,L1}_{T} #geq 20", "Reco": "p^{#mu,offline}_{T} #geq 24"},
    "L1Mu15": {"L1": "p^{#mu,L1}_{T} #geq 15", "Reco": "p^{#mu,offline}_{T} #geq 19"},
    "L1Mu10": {"L1": "p^{#mu,L1}_{T} #geq 10", "Reco": "p^{#mu,offline}_{T} #geq 14"},
    "L1Mu5": {"L1": "p^{#mu,L1}_{T} #geq 5", "Reco": "p^{#mu,offline}_{T} #geq 9"},
    "L1Mu3": {"L1": "p^{#mu,L1}_{T} #geq 3", "Reco": "p^{#mu,offline}_{T} #geq 7"}
}
TFs = {
    "uGMT": "|#eta| #leq 2.4",
    "BMTF": "|#eta| #leq 0.83",
    "OMTF": "0.83 #leq |#eta| #leq 1.24",
    "EMTF": "1.24 #leq |#eta| #leq 2.4",
    "EMTF1": "1.24 #leq |#eta| #leq 1.6",
    "EMTF2": "1.6 #leq |#eta| #leq 2.1",
    "EMTF3": "2.1 #leq |#eta| #leq 2.4"
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

# Create plots for pt comparison
for var in vars_title:
    for tf in TFs:
        key="_" + var
        c.SetLogx(0)

        # Retrieve and draw histogram for {tf} for L1Mu22
        h_passed_22 = in_file.Get(f"{tf}_L1Mu22" + key + "_passed")
        h_passed_22 = utils.add_overflow(h_passed_22)
        h_total_22 = in_file.Get(f"{tf}_L1Mu22" + key + "_total")
        h_total_22 = utils.add_overflow(h_total_22)
        h_eff_22 = ROOT.TEfficiency(h_passed_22,h_total_22)
        draw_hist(h_eff_22, CMS_color_7, 21, "")

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

        # Retrieve and draw histogram for {tf} for L1Mu26
        h_passed_26 = in_file.Get(f"{tf}_L1Mu26" + key + "_passed")
        h_passed_26 = utils.add_overflow(h_passed_26)
        h_total_26 = in_file.Get(f"{tf}_L1Mu26" + key + "_total")
        h_total_26 = utils.add_overflow(h_total_26)
        h_eff_26 = ROOT.TEfficiency(h_passed_26,h_total_26)
        draw_hist(h_eff_26, CMS_color_6, 20, "same")

        # Retrieve and draw histogram for {tf} for L1Mu20
        h_passed_20 = in_file.Get(f"{tf}_L1Mu20" + key + "_passed")
        h_passed_20 = utils.add_overflow(h_passed_20)
        h_total_20 = in_file.Get(f"{tf}_L1Mu20" + key + "_total")
        h_total_20 = utils.add_overflow(h_total_20)
        h_eff_20 = ROOT.TEfficiency(h_passed_20,h_total_20)
        draw_hist(h_eff_20, CMS_color_8, 22, "same")

        # Retrieve and draw histogram for {tf} for L1Mu15
        h_passed_15 = in_file.Get(f"{tf}_L1Mu15" + key + "_passed")
        h_passed_15 = utils.add_overflow(h_passed_15)
        h_total_15 = in_file.Get(f"{tf}_L1Mu15" + key + "_total")
        h_total_15 = utils.add_overflow(h_total_15)
        h_eff_15 = ROOT.TEfficiency(h_passed_15,h_total_15)
        draw_hist(h_eff_15, CMS_color_9, 23, "same")

        # Retrieve and draw histogram for {tf} for L1Mu10
        h_passed_10 = in_file.Get(f"{tf}_L1Mu10" + key + "_passed")
        h_passed_10 = utils.add_overflow(h_passed_10)
        h_total_10 = in_file.Get(f"{tf}_L1Mu10" + key + "_total")
        h_total_10 = utils.add_overflow(h_total_10)
        h_eff_10 = ROOT.TEfficiency(h_passed_10,h_total_10)
        draw_hist(h_eff_10, CMS_color_10, 24, "same")

        # Retrieve and draw histogram for {tf} for L1Mu5
        h_passed_5 = in_file.Get(f"{tf}_L1Mu5" + key + "_passed")
        h_passed_5 = utils.add_overflow(h_passed_5)
        h_total_5 = in_file.Get(f"{tf}_L1Mu5" + key + "_total")
        h_total_5 = utils.add_overflow(h_total_5)
        h_eff_5 = ROOT.TEfficiency(h_passed_5,h_total_5)
        draw_hist(h_eff_5, CMS_color_11, 25, "same")

        # Retrieve and draw histogram for {tf} for L1Mu3
        h_passed_3 = in_file.Get(f"{tf}_L1Mu3" + key + "_passed")
        h_passed_3 = utils.add_overflow(h_passed_3)
        h_total_3 = in_file.Get(f"{tf}_L1Mu3" + key + "_total")
        h_total_3 = utils.add_overflow(h_total_3)
        h_eff_3 = ROOT.TEfficiency(h_passed_3,h_total_3)
        draw_hist(h_eff_3, CMS_color_12, 26, "same")

        # Create legend
        if var == "pt" or var == "pt2":
            leg = ROOT.TLegend(0.70,0.13,0.89,0.48)
            leg.SetFillStyle(0)
            leg.AddEntry(h_eff_26,"p^{#mu,L1}_{T} #geq 26","lep")
            leg.AddEntry(h_eff_22,"p^{#mu,L1}_{T} #geq 22","lep")
            leg.AddEntry(h_eff_20,"p^{#mu,L1}_{T} #geq 20","lep")
            leg.AddEntry(h_eff_15,"p^{#mu,L1}_{T} #geq 15","lep")
            leg.AddEntry(h_eff_10,"p^{#mu,L1}_{T} #geq 10","lep")
            leg.AddEntry(h_eff_5,"p^{#mu,L1}_{T} #geq 5","lep")
            leg.AddEntry(h_eff_3,"p^{#mu,L1}_{T} #geq 3","lep")
        else:
            leg = ROOT.TLegend(0.49,0.12,0.80,0.48)
            leg.SetFillStyle(0)
            leg.AddEntry(h_eff_26,"p^{#mu,L1}_{T} #geq 26, p^{#mu,offline}_{T} #geq 30","lep")
            leg.AddEntry(h_eff_22,"p^{#mu,L1}_{T} #geq 22, p^{#mu,offline}_{T} #geq 26","lep")
            leg.AddEntry(h_eff_20,"p^{#mu,L1}_{T} #geq 20, p^{#mu,offline}_{T} #geq 24","lep")
            leg.AddEntry(h_eff_15,"p^{#mu,L1}_{T} #geq 15, p^{#mu,offline}_{T} #geq 19","lep")
            leg.AddEntry(h_eff_10,"p^{#mu,L1}_{T} #geq 10, p^{#mu,offline}_{T} #geq 14","lep")
            leg.AddEntry(h_eff_5,"p^{#mu,L1}_{T} #geq 5, p^{#mu,offline}_{T} #geq 9","lep")
            leg.AddEntry(h_eff_3,"p^{#mu,L1}_{T} #geq 3, p^{#mu,offline}_{T} #geq 7","lep")
        leg.Draw()

        # Add text to show that the plot is for {tf} except in eta plot
        if var != "eta":
            latex.SetTextSize(0.035)
            latex.DrawLatexNDC(0.65, 0.80, "L1T Quality #geq 8")
            if tf == "uGMT":
                latex.DrawLatexNDC(0.775, 0.85, TFs[tf])
            elif tf == "BMTF":
                latex.DrawLatexNDC(0.76, 0.85, TFs[tf])
            else:
                latex.DrawLatexNDC(0.675, 0.85, TFs[tf])
        else:
            latex.SetTextSize(0.035)
            latex.DrawLatexNDC(0.6, 0.505, "L1T Quality #geq 8")

        utils.add_dataset_legend(dataset_x1, dataset_legend)
        utils.add_cms_label_in(L,T)

        c.SaveAs(output_dir + f"eff_pt_comparison_{tf}{key}.png")
        c.SaveAs(output_dir + f"eff_pt_comparison_{tf}{key}.pdf")

# ================================================================================

# Create canvas, receive values for margins
c2, L, R, T, B = utils.create_canvas("c2")
dataset_legend, dataset_x1 = get_dataset_legend(args.legend, R)

# Create plots for eta comparison
for var in vars_title:
    if var == "eta": continue  # Skip eta comparison for now
    for wp in WPs:
        key= wp + "_" + var
        c2.SetLogx(0)

        # Retrieve and draw histogram for BMTF for L1Mu22
        h_passed_BMTF = in_file.Get(f"BMTF_" + key + "_passed")
        h_passed_BMTF = utils.add_overflow(h_passed_BMTF)
        h_total_BMTF = in_file.Get(f"BMTF_" + key + "_total")
        h_total_BMTF = utils.add_overflow(h_total_BMTF)
        h_eff_BMTF = ROOT.TEfficiency(h_passed_BMTF,h_total_BMTF)
        draw_hist(h_eff_BMTF, CMS_color_7, 21, "")

        # Add label and set the limits for the axes
        h_eff_BMTF.SetTitle(";" + vars_title[var] + ";Efficiency")
        c2.Update()
        graph = h_eff_BMTF.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.2)
        if var == "pt":
            c2.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "pt2":
            graph.GetXaxis().SetLimits(0,60)
            graph.GetXaxis().SetTitleOffset(1.2)
        c2.Update()

        # Retrieve and draw histogram for OMTF
        h_passed_OMTF = in_file.Get(f"OMTF_" + key + "_passed")
        h_passed_OMTF = utils.add_overflow(h_passed_OMTF)
        h_total_OMTF = in_file.Get(f"OMTF_" + key + "_total")
        h_total_OMTF = utils.add_overflow(h_total_OMTF)
        h_eff_OMTF = ROOT.TEfficiency(h_passed_OMTF,h_total_OMTF)
        draw_hist(h_eff_OMTF, CMS_color_6, 20, "same")

        # Retrieve and draw histogram for EMTF
        h_passed_EMTF = in_file.Get(f"EMTF_" + key + "_passed")
        h_passed_EMTF = utils.add_overflow(h_passed_EMTF)
        h_total_EMTF = in_file.Get(f"EMTF_" + key + "_total")
        h_total_EMTF = utils.add_overflow(h_total_EMTF)
        h_eff_EMTF = ROOT.TEfficiency(h_passed_EMTF,h_total_EMTF)
        draw_hist(h_eff_EMTF, CMS_color_8, 22, "same")

        # Retrieve and draw histogram for EMTF1
        h_passed_EMTF1 = in_file.Get(f"EMTF1_" + key + "_passed")
        h_passed_EMTF1 = utils.add_overflow(h_passed_EMTF1)
        h_total_EMTF1 = in_file.Get(f"EMTF1_" + key + "_total")
        h_total_EMTF1 = utils.add_overflow(h_total_EMTF1)
        h_eff_EMTF1 = ROOT.TEfficiency(h_passed_EMTF1,h_total_EMTF1)
        draw_hist(h_eff_EMTF1, CMS_color_9, 23, "same")

        # Retrieve and draw histogram for EMTF2 
        h_passed_EMTF2 = in_file.Get(f"EMTF2_" + key + "_passed")
        h_passed_EMTF2 = utils.add_overflow(h_passed_EMTF2)
        h_total_EMTF2 = in_file.Get(f"EMTF2_" + key + "_total")
        h_total_EMTF2 = utils.add_overflow(h_total_EMTF2)
        h_eff_EMTF2 = ROOT.TEfficiency(h_passed_EMTF2,h_total_EMTF2)
        draw_hist(h_eff_EMTF2, CMS_color_10, 24, "same")

        # Retrieve and draw histogram for EMTF3
        h_passed_EMTF3 = in_file.Get(f"EMTF3_" + key + "_passed")
        h_passed_EMTF3 = utils.add_overflow(h_passed_EMTF3)
        h_total_EMTF3 = in_file.Get(f"EMTF3_" + key + "_total")
        h_total_EMTF3 = utils.add_overflow(h_total_EMTF3)
        h_eff_EMTF3 = ROOT.TEfficiency(h_passed_EMTF3,h_total_EMTF3)
        draw_hist(h_eff_EMTF3, CMS_color_11, 25, "same")

        # Retrieve and draw histogram for uGMT
        h_passed_uGMT = in_file.Get(f"uGMT_" + key + "_passed")
        h_passed_uGMT = utils.add_overflow(h_passed_uGMT)
        h_total_uGMT = in_file.Get(f"uGMT_" + key + "_total")
        h_total_uGMT = utils.add_overflow(h_total_uGMT)
        h_eff_uGMT = ROOT.TEfficiency(h_passed_uGMT,h_total_uGMT)
        draw_hist(h_eff_uGMT, CMS_color_12, 26, "same")

        # Create legend
        leg = ROOT.TLegend(0.52,0.13,0.89,0.48)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_BMTF, "0.00 #leq |#eta^{#mu}_{reco}| #leq 0.83","lep")
        leg.AddEntry(h_eff_OMTF, "0.83 #leq |#eta^{#mu}_{reco}| #leq 1.24","lep")
        leg.AddEntry(h_eff_EMTF, "1.24 #leq |#eta^{#mu}_{reco}| #leq 2.40","lep")
        leg.AddEntry(h_eff_EMTF1,"1.24 #leq |#eta^{#mu}_{reco}| #leq 1.60","lep")
        leg.AddEntry(h_eff_EMTF2,"1.60 #leq |#eta^{#mu}_{reco}| #leq 2.10","lep")
        leg.AddEntry(h_eff_EMTF3,"2.10 #leq |#eta^{#mu}_{reco}| #leq 2.40","lep")
        leg.AddEntry(h_eff_uGMT, "0.00 #leq |#eta^{#mu}_{reco}| #leq 2.40","lep")
        leg.Draw()

        # Add text to show that the plot is for {tf} except in eta plot
        latex.SetTextSize(0.035)
        latex.DrawLatexNDC(0.65, 0.80, "L1T Quality #geq 8")
        if wp == "L1Mu5" or wp == "L1Mu3":
            latex.DrawLatexNDC(0.765, 0.85, WPs[wp]["L1"])
            if var == "phi":
                latex.DrawLatexNDC(0.605, 0.85, WPs[wp]["Reco"] + ",")
        else:
            latex.DrawLatexNDC(0.75, 0.85, WPs[wp]["L1"])
            if var == "phi":
                latex.DrawLatexNDC(0.575, 0.85, WPs[wp]["Reco"] + ",")

        utils.add_dataset_legend(dataset_x1, dataset_legend)
        utils.add_cms_label_in(L,T)

        c2.SaveAs(output_dir + f"eff_eta_comparison_{key}.png")
        c2.SaveAs(output_dir + f"eff_eta_comparison_{key}.pdf")

# Close the input file
in_file.Close()