import ROOT
import argparse
import os
import utils
from utils import *

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--legend1', type=str, help='dataset legend')
parser.add_argument('--legend2', type=str, help='dataset legend')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('-i1', type=str, help='input dir1')
parser.add_argument('-i2', type=str, help='input dir2')
args = parser.parse_args()

dataset_legend1 = args.legend1
dataset_legend2 = args.legend2
output_dir = args.o
input_dir1 = args.i1
input_dir2 = args.i2

# Merge root files
# utils.merge_root_files(input_dir1)
# utils.merge_root_files(input_dir2)

in_file1 = ROOT.TFile(input_dir1 + "merged_total.root","READ")
in_file2 = ROOT.TFile(input_dir2 + "merged_total.root","READ")

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetOptTitle(0)

WPs = ["L1Mu22_22", "L1Mu5_5"]

wp_values = {
    "L1Mu22_22": {"quality": 12, "pt_l1": 22, "pt_reco": 26},
    "L1Mu5_5": {"quality": 8, "pt_l1": 5, "pt_reco": 9}
}

vars_title = {
    "eta": "#eta_{Reco}",
    "phi": "#phi_{Reco}",
    "pt": "p^{Reco}_{T} [GeV]",
    "pt2": "p^{Reco}_{T} [GeV]",
    #"nPV": "Number of Vertices"
}

# Create canvas, receive values for margins
c, L, R, T, B = utils.create_canvas("c")

## eff vs var
## all regions
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        c.SetLogx(0)
        values = wp_values[wp]
        quality_label = f"L1T Quality #geq {values['quality']}"
        pt_l1_label = f"p^{{#mu,L1}}_{{T}} #geq {values['pt_l1']} GeV"
        pt_reco_label = f"p^{{#mu,Reco}}_{{T}} #geq {values['pt_reco']} GeV"

        if var == "eta":
            # Retrieve and draw histogram for BMTF, OMTF, EMTF
            h_passed_EMTF1 = in_file1.Get("EMTF_" + key + "_passed")
            h_passed_EMTF1 = utils.add_overflow(h_passed_EMTF1)
            h_total_EMTF1 = in_file1.Get("EMTF_" + key + "_total")
            h_total_EMTF1 = utils.add_overflow(h_total_EMTF1)

            h_passed_BMTF1 = in_file1.Get("BMTF_" + key + "_passed")
            h_passed_BMTF1 = utils.add_overflow(h_passed_BMTF1)
            h_total_BMTF1 = in_file1.Get("BMTF_" + key + "_total")
            h_total_BMTF1 = utils.add_overflow(h_total_BMTF1)

            h_passed_OMTF1 = in_file1.Get("OMTF_" + key + "_passed")
            h_passed_OMTF1 = utils.add_overflow(h_passed_OMTF1)
            h_total_OMTF1 = in_file1.Get("OMTF_" + key + "_total")
            h_total_OMTF1 = utils.add_overflow(h_total_OMTF1)

            # Handle overlap assignment without averaging
            # For |eta| ~ 0.83 (BMTF and OMTF overlap), assign to OMTF
            for i in range(1, h_total_BMTF1.GetNbinsX() + 1):
                eta_val = h_total_BMTF1.GetXaxis().GetBinCenter(i)
                if 0.8 < abs(eta_val) < 0.86:
                    # Move BMTF points to OMTF
                    passed_bmtf1 = h_passed_BMTF1.GetBinContent(i)
                    total_bmtf1 = h_total_BMTF1.GetBinContent(i)
                    
                    # Add BMTF counts to OMTF
                    h_passed_OMTF1.SetBinContent(i, h_passed_OMTF1.GetBinContent(i) + passed_bmtf1)
                    h_total_OMTF1.SetBinContent(i, h_total_OMTF1.GetBinContent(i) + total_bmtf1)
                    
                    # Optionally zero out the BMTF overlap bin if you don't want to keep it
                    h_passed_BMTF1.SetBinContent(i, 0)
                    h_total_BMTF1.SetBinContent(i, 0)

            # For |eta| ~ 1.24 (OMTF and EMTF overlap), assign to EMTF
            for i in range(1, h_total_OMTF1.GetNbinsX() + 1):
                eta_val = h_total_OMTF1.GetXaxis().GetBinCenter(i)
                if 1.23 < abs(eta_val) < 1.26:
                    # Move OMTF points to EMTF
                    passed_omtf1 = h_passed_OMTF1.GetBinContent(i)
                    total_omtf1 = h_total_OMTF1.GetBinContent(i)
                    
                    # Add OMTF counts to EMTF
                    h_passed_EMTF1.SetBinContent(i, h_passed_EMTF1.GetBinContent(i) + passed_omtf1)
                    h_total_EMTF1.SetBinContent(i, h_total_EMTF1.GetBinContent(i) + total_omtf1)

                    # Optionally zero out the OMTF overlap bin
                    h_passed_OMTF1.SetBinContent(i, 0)
                    h_total_OMTF1.SetBinContent(i, 0)
           
            # Retrieve and draw histogram for BMTF, OMTF, EMTF
            h_passed_EMTF2 = in_file2.Get("EMTF_" + key + "_passed")
            h_passed_EMTF2 = utils.add_overflow(h_passed_EMTF2)
            h_total_EMTF2 = in_file2.Get("EMTF_" + key + "_total")
            h_total_EMTF2 = utils.add_overflow(h_total_EMTF2)

            h_passed_BMTF2 = in_file2.Get("BMTF_" + key + "_passed")
            h_passed_BMTF2 = utils.add_overflow(h_passed_BMTF2)
            h_total_BMTF2 = in_file2.Get("BMTF_" + key + "_total")
            h_total_BMTF2 = utils.add_overflow(h_total_BMTF2)

            h_passed_OMTF2 = in_file2.Get("OMTF_" + key + "_passed")
            h_passed_OMTF2 = utils.add_overflow(h_passed_OMTF2)
            h_total_OMTF2 = in_file2.Get("OMTF_" + key + "_total")
            h_total_OMTF2 = utils.add_overflow(h_total_OMTF2)

            # Handle overlap assignment without averaging
            # For |eta| ~ 0.83 (BMTF and OMTF overlap), assign to OMTF
            for i in range(1, h_total_BMTF2.GetNbinsX() + 1):
                eta_val = h_total_BMTF2.GetXaxis().GetBinCenter(i)
                if 0.8 < abs(eta_val) < 0.86:
                    # Move BMTF points to OMTF
                    passed_bmtf2 = h_passed_BMTF2.GetBinContent(i)
                    total_bmtf2 = h_total_BMTF2.GetBinContent(i)
                    
                    # Add BMTF counts to OMTF
                    h_passed_OMTF2.SetBinContent(i, h_passed_OMTF2.GetBinContent(i) + passed_bmtf2)
                    h_total_OMTF2.SetBinContent(i, h_total_OMTF2.GetBinContent(i) + total_bmtf2)
                    
                    # Optionally zero out the BMTF overlap bin if you don't want to keep it
                    h_passed_BMTF2.SetBinContent(i, 0)
                    h_total_BMTF2.SetBinContent(i, 0)

            # For |eta| ~ 1.24 (OMTF and EMTF overlap), assign to EMTF
            for i in range(1, h_total_OMTF2.GetNbinsX() + 1):
                eta_val = h_total_OMTF2.GetXaxis().GetBinCenter(i)
                if 1.23 < abs(eta_val) < 1.26:
                    # Move OMTF points to EMTF
                    passed_omtf2 = h_passed_OMTF2.GetBinContent(i)
                    total_omtf2 = h_total_OMTF2.GetBinContent(i)
                    
                    # Add OMTF counts to EMTF
                    h_passed_EMTF2.SetBinContent(i, h_passed_EMTF2.GetBinContent(i) + passed_omtf2)
                    h_total_EMTF2.SetBinContent(i, h_total_EMTF2.GetBinContent(i) + total_omtf2)

                    # Optionally zero out the OMTF overlap bin
                    h_passed_OMTF2.SetBinContent(i, 0)
                    h_total_OMTF2.SetBinContent(i, 0)

            h_eff_EMTF1 = ROOT.TEfficiency(h_passed_EMTF1,h_total_EMTF1)
            h_eff_BMTF1 = ROOT.TEfficiency(h_passed_BMTF1,h_total_BMTF1)
            h_eff_OMTF1 = ROOT.TEfficiency(h_passed_OMTF1,h_total_OMTF1)
            h_eff_BMTF2 = ROOT.TEfficiency(h_passed_BMTF2,h_total_BMTF2)
            h_eff_OMTF2 = ROOT.TEfficiency(h_passed_OMTF2,h_total_OMTF2)
            h_eff_EMTF2 = ROOT.TEfficiency(h_passed_EMTF2,h_total_EMTF2)

            draw_hist(h_eff_EMTF1, CMS_color_4, 22, "", 1, 1.3)
            
            # Add label and set the limits for the axes
            h_eff_EMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
            c.Update()
            graph = h_eff_EMTF1.GetPaintedGraph()
            graph.SetMinimum(0)
            graph.SetMaximum(1.1)
            c.Update()

            draw_hist(h_eff_BMTF1, CMS_color_0, 20, "same")
            draw_hist(h_eff_OMTF1, CMS_color_2, 21, "same")
            draw_hist(h_eff_BMTF2, CMS_color_1, 24, "same")
            draw_hist(h_eff_OMTF2, CMS_color_3, 25, "same")
            draw_hist(h_eff_EMTF2, CMS_color_5, 26, "same")

            # Create legend 
            leg = ROOT.TLegend(0.62,0.13,0.88,0.35)
            leg.SetFillStyle(0)
            leg.SetNColumns(2)
            leg.AddEntry(0, f"{dataset_legend1}", "")
            leg.AddEntry(0, f"{dataset_legend2}", "")
            leg.AddEntry(h_eff_BMTF1,"BMTF  ","lep")
            leg.AddEntry(h_eff_BMTF2,"BMTF ","lep")
            leg.AddEntry(h_eff_OMTF1,"OMTF  ","lep")
            leg.AddEntry(h_eff_OMTF2,"OMTF ","lep")
            leg.AddEntry(h_eff_EMTF1,"EMTF  ","lep")
            leg.AddEntry(h_eff_EMTF2,"EMTF ","lep")

            leg.Draw()

            latex.SetTextSize(0.035)
            latex.SetTextFont(42)
            latex.DrawLatexNDC(0.14, 0.27, quality_label)
            latex.DrawLatexNDC(0.14, 0.21, pt_l1_label)
            latex.DrawLatexNDC(0.14, 0.15, pt_reco_label)
            utils.add_cms_label_out(L,T)

            c.SaveAs(output_dir + "eff_all_" + key + ".png")
            c.SaveAs(output_dir + "eff_all_" + key + ".pdf")
        else:
            # Retrieve and draw histogram for BMTF
            h_passed_BMTF1 = in_file1.Get("BMTF_" + key + "_passed")
            h_passed_BMTF1 = utils.add_overflow(h_passed_BMTF1)
            h_total_BMTF1 = in_file1.Get("BMTF_" + key + "_total")
            h_total_BMTF1 = utils.add_overflow(h_total_BMTF1)
            h_eff_BMTF1 = ROOT.TEfficiency(h_passed_BMTF1,h_total_BMTF1)
            draw_hist(h_eff_BMTF1, CMS_color_0, 20, "")
            
            # Add label and set the limits for the axes
            h_eff_BMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
            c.Update()
            graph = h_eff_BMTF1.GetPaintedGraph() 
            graph.SetMinimum(0)
            graph.SetMaximum(1.2)
            if var == "pt":
                c.SetLogx(1)
                graph.GetXaxis().SetLimits(1,1000)
                graph.GetXaxis().SetTitleOffset(1.3)
            if var == "nPV":
                graph.GetXaxis().SetLimits(0,70)
            c.Update()

            # Retrieve and draw histogram for OMTF
            h_passed_OMTF1 = in_file1.Get("OMTF_" + key + "_passed")
            h_passed_OMTF1 = utils.add_overflow(h_passed_OMTF1)
            h_total_OMTF1 = in_file1.Get("OMTF_" + key + "_total")
            h_total_OMTF1 = utils.add_overflow(h_total_OMTF1)
            h_eff_OMTF1 = ROOT.TEfficiency(h_passed_OMTF1,h_total_OMTF1)
            draw_hist(h_eff_OMTF1, CMS_color_2, 21, "same")

            # Retrieve and draw histogram for EMTF
            h_passed_EMTF1 = in_file1.Get("EMTF_" + key + "_passed")
            h_passed_EMTF1 = utils.add_overflow(h_passed_EMTF1)
            h_total_EMTF1 = in_file1.Get("EMTF_" + key + "_total")
            h_total_EMTF1 = utils.add_overflow(h_total_EMTF1)
            h_eff_EMTF1 = ROOT.TEfficiency(h_passed_EMTF1,h_total_EMTF1)
            draw_hist(h_eff_EMTF1, CMS_color_4, 22, "same", 1, 1.3)

            # Retrieve and draw histogram for BMTF
            h_passed_BMTF2 = in_file2.Get("BMTF_" + key + "_passed")
            h_passed_BMTF2 = utils.add_overflow(h_passed_BMTF2)
            h_total_BMTF2 = in_file2.Get("BMTF_" + key + "_total")
            h_total_BMTF2 = utils.add_overflow(h_total_BMTF2)
            h_eff_BMTF2 = ROOT.TEfficiency(h_passed_BMTF2,h_total_BMTF2)
            draw_hist(h_eff_BMTF2, CMS_color_1, 24, "same")
        
            # Retrieve and draw histogram for OMTF
            h_passed_OMTF2 = in_file2.Get("OMTF_" + key + "_passed")
            h_passed_OMTF2 = utils.add_overflow(h_passed_OMTF2)
            h_total_OMTF2 = in_file2.Get("OMTF_" + key + "_total")
            h_total_OMTF2 = utils.add_overflow(h_total_OMTF2)
            h_eff_OMTF2 = ROOT.TEfficiency(h_passed_OMTF2,h_total_OMTF2)
            draw_hist(h_eff_OMTF2, CMS_color_3, 25, "same")
            
            # Retrieve and draw histogram for EMTF
            h_passed_EMTF2 = in_file2.Get("EMTF_" + key + "_passed")
            h_passed_EMTF2 = utils.add_overflow(h_passed_EMTF2)
            h_total_EMTF2 = in_file2.Get("EMTF_" + key + "_total")
            h_total_EMTF2 = utils.add_overflow(h_total_EMTF2)
            h_eff_EMTF2 = ROOT.TEfficiency(h_passed_EMTF2,h_total_EMTF2)
            draw_hist(h_eff_EMTF2, CMS_color_5, 26, "same")

            # Create legend 
            leg = ROOT.TLegend(0.62,0.13,0.88,0.35)
            leg.SetFillStyle(0)
            leg.SetNColumns(2)
            leg.AddEntry(0, f"{dataset_legend1}", "")
            leg.AddEntry(0, f"{dataset_legend2}", "")
            leg.AddEntry(h_eff_BMTF1,"BMTF  ","lep")
            leg.AddEntry(h_eff_BMTF2,"BMTF ","lep")
            leg.AddEntry(h_eff_OMTF1,"OMTF  ","lep")
            leg.AddEntry(h_eff_OMTF2,"OMTF ","lep")
            leg.AddEntry(h_eff_EMTF1,"EMTF  ","lep")
            leg.AddEntry(h_eff_EMTF2,"EMTF ","lep")

            leg.Draw()

            latex.SetTextSize(0.035)
            latex.SetTextFont(42)
            if var == "phi" or var == "nPV":
                # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
                latex.DrawLatexNDC(0.65,0.85, quality_label)
                latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
                latex.DrawLatexNDC(0.45, 0.80, pt_reco_label)
            else:
                latex.DrawLatexNDC(0.65,0.85, quality_label)
                latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
            utils.add_cms_label_in(L,T)

            c.SaveAs(output_dir + "eff_all_" + key + ".png")
            c.SaveAs(output_dir + "eff_all_" + key + ".pdf")


# Create canvas, receive values for margins
c2, L, R, T, B = utils.create_canvas("c2")

## BMTF
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        c2.SetLogx(0)
        values = wp_values[wp]
        quality_label = f"L1T Quality #geq {values['quality']}"
        pt_l1_label = f"p^{{#mu,L1}}_{{T}} #geq {values['pt_l1']} GeV"
        pt_reco_label = f"p^{{#mu,Reco}}_{{T}} #geq {values['pt_reco']} GeV"

        # Retrieve and draw histogram for BMTF
        h_passed_BMTF1 = in_file1.Get("BMTF_" + key + "_passed")
        h_passed_BMTF1 = utils.add_overflow(h_passed_BMTF1)
        h_total_BMTF1 = in_file1.Get("BMTF_" + key + "_total")
        h_total_BMTF1 = utils.add_overflow(h_total_BMTF1)
        h_eff_BMTF1 = ROOT.TEfficiency(h_passed_BMTF1,h_total_BMTF1)
        draw_hist(h_eff_BMTF1, CMS_color_0, 20, "")

        # Add label and set the limits for the axes
        h_eff_BMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
        c2.Update()
        graph = h_eff_BMTF1.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.2)
        if var == "pt":
            c2.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "nPV":
            graph.GetXaxis().SetLimits(0,70)
        c2.Update()

        # Retrieve and draw histogram for BMTF
        h_passed_BMTF2 = in_file2.Get("BMTF_" + key + "_passed")
        h_passed_BMTF2 = utils.add_overflow(h_passed_BMTF2)
        h_total_BMTF2 = in_file2.Get("BMTF_" + key + "_total")
        h_total_BMTF2 = utils.add_overflow(h_total_BMTF2)
        h_eff_BMTF2 = ROOT.TEfficiency(h_passed_BMTF2,h_total_BMTF2)
        draw_hist(h_eff_BMTF2, CMS_color_1, 24, "same")
    
        # Create legend
        leg = ROOT.TLegend(0.62,0.13,0.8,0.24)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_BMTF1,f"{dataset_legend1}: BMTF","lep")
        leg.AddEntry(h_eff_BMTF2,f"{dataset_legend2}: BMTF","lep")
        leg.Draw()

        latex.SetTextSize(0.035)
        latex.SetTextFont(42)
        if var == "eta" or var == "phi" or var == "nPV":
            # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
            latex.DrawLatexNDC(0.65,0.85, quality_label)
            latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
            latex.DrawLatexNDC(0.45, 0.80, pt_reco_label)
        else:
            latex.DrawLatexNDC(0.65,0.85, quality_label)
            latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
        utils.add_cms_label_in(L,T)

        c2.SaveAs(output_dir + "eff_BMTF_" + key + ".png")
        c2.SaveAs(output_dir + "eff_BMTF_" + key + ".pdf")


# Create canvas, receive values for margins
c3, L, R, T, B = utils.create_canvas("c3")

## EMTF
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        c3.SetLogx(0)
        values = wp_values[wp]
        quality_label = f"L1T Quality #geq {values['quality']}"
        pt_l1_label = f"p^{{#mu,L1}}_{{T}} #geq {values['pt_l1']} GeV"
        pt_reco_label = f"p^{{#mu,Reco}}_{{T}} #geq {values['pt_reco']} GeV"

        # Retrieve and draw histogram for EMTF
        h_passed_EMTF1 = in_file1.Get("EMTF_" + key + "_passed")
        h_passed_EMTF1 = utils.add_overflow(h_passed_EMTF1)
        h_total_EMTF1 = in_file1.Get("EMTF_" + key + "_total")
        h_total_EMTF1 = utils.add_overflow(h_total_EMTF1)
        h_eff_EMTF1 = ROOT.TEfficiency(h_passed_EMTF1,h_total_EMTF1)
        draw_hist(h_eff_EMTF1, CMS_color_4, 22, "", 1, 1.3)

        # Add label and set the limits for the axes
        h_eff_EMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
        c3.Update()
        graph = h_eff_EMTF1.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.2)
        if var == "pt":
            c3.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "nPV":
            graph.GetXaxis().SetLimits(0,70)
        c3.Update()

        # Retrieve and draw histogram for EMTF
        h_passed_EMTF2 = in_file2.Get("EMTF_" + key + "_passed")
        h_passed_EMTF2 = utils.add_overflow(h_passed_EMTF2)
        h_total_EMTF2 = in_file2.Get("EMTF_" + key + "_total")
        h_total_EMTF2 = utils.add_overflow(h_total_EMTF2)
        h_eff_EMTF2 = ROOT.TEfficiency(h_passed_EMTF2,h_total_EMTF2)
        draw_hist(h_eff_EMTF2, CMS_color_5, 26, "same")

        # Create legend
        leg = ROOT.TLegend(0.62,0.13,0.8,0.24)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_EMTF1,f"{dataset_legend1}: EMTF","lep")
        leg.AddEntry(h_eff_EMTF2,f"{dataset_legend2}: EMTF","lep")
        leg.Draw()

        latex.SetTextSize(0.035)
        latex.SetTextFont(42)
        if var == "eta" or var == "phi" or var == "nPV":
            # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
            latex.DrawLatexNDC(0.65,0.85, quality_label)
            latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
            latex.DrawLatexNDC(0.45, 0.80, pt_reco_label)
        else:
            latex.DrawLatexNDC(0.65,0.85, quality_label)
            latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
        utils.add_cms_label_in(L,T)


        c3.SaveAs(output_dir + "eff_EMTF_" + key + ".png")
        c3.SaveAs(output_dir + "eff_EMTF_" + key + ".pdf")

# Create canvas, receive values for margins
c4, L, R, T, B = utils.create_canvas("c4")

## OMTF
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        c4.SetLogx(0)
        values = wp_values[wp]
        quality_label = f"L1T Quality #geq {values['quality']}"
        pt_l1_label = f"p^{{#mu,L1}}_{{T}} #geq {values['pt_l1']} GeV"
        pt_reco_label = f"p^{{#mu,Reco}}_{{T}} #geq {values['pt_reco']} GeV"

        # Retrieve and draw histogram for OMTF
        h_passed_OMTF1 = in_file1.Get("OMTF_" + key + "_passed")
        h_passed_OMTF1 = utils.add_overflow(h_passed_OMTF1)
        h_total_OMTF1 = in_file1.Get("OMTF_" + key + "_total")
        h_total_OMTF1 = utils.add_overflow(h_total_OMTF1)
        h_eff_OMTF1 = ROOT.TEfficiency(h_passed_OMTF1,h_total_OMTF1)
        draw_hist(h_eff_OMTF1, CMS_color_2, 21, "")
        
        # Add label and set the limits for the axes
        h_eff_OMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
        c4.Update()
        graph = h_eff_OMTF1.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.2)
        if var == "pt":
            c4.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "nPV":
            graph.GetXaxis().SetLimits(0,70)
        c4.Update()

        h_passed_OMTF2 = in_file2.Get("OMTF_" + key + "_passed")
        h_passed_OMTF2 = utils.add_overflow(h_passed_OMTF2)
        h_total_OMTF2 = in_file2.Get("OMTF_" + key + "_total")
        h_total_OMTF2 = utils.add_overflow(h_total_OMTF2)
        h_eff_OMTF2 = ROOT.TEfficiency(h_passed_OMTF2,h_total_OMTF2)
        draw_hist(h_eff_OMTF2, CMS_color_3, 25, "same")

        # Create legend
        leg = ROOT.TLegend(0.62,0.13,0.8,0.24)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_OMTF1,f"{dataset_legend1}: OMTF","lep")
        leg.AddEntry(h_eff_OMTF2,f"{dataset_legend2}: OMTF","lep")
        leg.Draw()

        latex.SetTextSize(0.035)
        latex.SetTextFont(42)
        if var == "eta" or var == "phi" or var == "nPV":
            # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
            latex.DrawLatexNDC(0.65,0.85, quality_label)
            latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
            latex.DrawLatexNDC(0.45, 0.80, pt_reco_label)
        else:
            latex.DrawLatexNDC(0.65,0.85, quality_label)
            latex.DrawLatexNDC(0.685, 0.80, pt_l1_label)
        utils.add_cms_label_in(L,T)


        c4.SaveAs(output_dir + "eff_OMTF_" + key + ".png")
        c4.SaveAs(output_dir + "eff_OMTF_" + key + ".pdf")

##----------------------------------------------------------------------------------------------
## Ratio plots
## BMTF
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        cr1= ROOT.TCanvas("canvas_ratio_1" + key, "cr1" + key, 800, 800)
        cr1.SetLogx(0)
        values = wp_values[wp]
        quality_label = f"L1T Quality #geq {values['quality']}"
        pt_l1_label = f"p^{{#mu,L1}}_{{T}} #geq {values['pt_l1']} GeV"
        pt_reco_label = f"p^{{#mu,Reco}}_{{T}} #geq {values['pt_reco']} GeV"

        #xlow, ylow, xup, yup
        pad1 = ROOT.TPad("pad1_1" + key, "pad1_1" + key, 0, 0.29, 1, 1)
        pad1.SetBottomMargin(0.02)  # Set bottom margin for pad1
        #pad1.SetLogx(0) 
        pad1.SetFrameLineWidth(2)
        pad1.SetGridx()
        pad1.SetGridy()
        pad1.Draw()
        pad1.cd()

        h_passed_BMTF1 = in_file1.Get("BMTF_" + key + "_passed")
        h_passed_BMTF1 = utils.add_overflow(h_passed_BMTF1)
        h_total_BMTF1 = in_file1.Get("BMTF_" + key + "_total")
        h_total_BMTF1 = utils.add_overflow(h_total_BMTF1)
        h_eff_BMTF1 = ROOT.TEfficiency(h_passed_BMTF1,h_total_BMTF1)
        h_eff_BMTF1.SetMarkerColor(CMS_color_0)
        h_eff_BMTF1.SetLineColor(CMS_color_0)
        h_eff_BMTF1.SetMarkerStyle(20)
        h_eff_BMTF1.Draw()
        #h_eff_BMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
        cr1.Update()
        graph = h_eff_BMTF1.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.1)
        if var == "pt":
            pad1.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "nPV":
            graph.GetXaxis().SetLimits(0,70)
        graph.GetXaxis().SetTitle("")
        graph.GetXaxis().SetLabelSize(0)
        cr1.Update()

        h_passed_BMTF2 = in_file2.Get("BMTF_" + key + "_passed")
        h_passed_BMTF2 = utils.add_overflow(h_passed_BMTF2)
        h_total_BMTF2 = in_file2.Get("BMTF_" + key + "_total")
        h_total_BMTF2 = utils.add_overflow(h_total_BMTF2)
        h_eff_BMTF2 = ROOT.TEfficiency(h_passed_BMTF2,h_total_BMTF2)
        h_eff_BMTF2.SetMarkerColor(CMS_color_1)
        h_eff_BMTF2.SetLineColor(CMS_color_1)
        h_eff_BMTF2.SetMarkerStyle(24)
        h_eff_BMTF2.Draw("same")

        leg = ROOT.TLegend(0.7,0.05,0.82,0.16)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_BMTF1,f"{dataset_legend1}: BMTF","lep")
        leg.AddEntry(h_eff_BMTF2,f"{dataset_legend2}: BMTF","lep")
        leg.Draw()

        latex.SetTextSize(0.035)
        #latex.DrawLatexNDC(0.80,0.91,dataset_legend)
        if var == "eta" or var == "phi" or var == "nPV":
            # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
            latex.DrawLatexNDC(0.14, 0.19, quality_label)
            latex.DrawLatexNDC(0.14, 0.12, pt_l1_label)
            latex.DrawLatexNDC(0.14, 0.06, pt_reco_label)
        else:
            latex.DrawLatexNDC(0.74, 0.18, pt_l1_label)
            latex.DrawLatexNDC(0.71, 0.25, quality_label)
        # utils.add_cms_label_out(L,T)
        latex.SetTextSize(0.0585)
        latex.DrawLatexNDC(0.1, 0.91, "#font[61]{CMS}")
        latex.SetTextSize(0.045)
        latex.DrawLatexNDC(0.185, 0.91, "#font[52]{Preliminary}")

        pad1.Update()
        cr1.cd()
        pad2 = ROOT.TPad("pad2_1" + key, "pad2_1" + key, 0, 0, 1, 0.29)
        pad2.SetTopMargin(0.03)  # Set top margin for pad2
        pad2.SetBottomMargin(0.3)  # Set bottom margin for pad2
        pad2.SetGridy()  # Add horizontal grid lines to pad2
        pad2.SetFrameLineWidth(2)
        pad2.Draw()
        pad2.cd()

        hist1_eff = h_eff_BMTF1.Clone()
        hist2_eff = h_eff_BMTF2.Clone()
        efficiency_values1, error_low_values1, error_up_values1 = utils.efficiency_to_vector(hist1_eff)
        efficiency_values2, error_low_values2, error_up_values2 = utils.efficiency_to_vector(hist2_eff)
        ratio_values, ratio_errors_low, ratio_errors_up = utils.calculate_ratio_with_error(
        efficiency_values2, error_low_values2, error_up_values2,
        efficiency_values1, error_low_values1, error_up_values1) 

        graph1 = ROOT.TGraphAsymmErrors(len(ratio_values))

        if var == 'eta':
            bin = [
                -2.4, -2.3, -2.2, -2.1, -2.0, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0, -0.9,
                -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
                0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4
            ]
        elif var == 'phi':
            bin = [
                -3.5, -3.45, -3.4, -3.35, -3.3, -3.25, -3.2, -3.15, -3.1, -3.05,
                -3.0, -2.95, -2.9, -2.85, -2.8, -2.75, -2.7, -2.65, -2.6, -2.55,
                -2.5, -2.45, -2.4, -2.35, -2.3, -2.25, -2.2, -2.15, -2.1, -2.05,
                -2.0, -1.95, -1.9, -1.85, -1.8, -1.75, -1.7, -1.65, -1.6, -1.55,
                -1.5, -1.45, -1.4, -1.35, -1.3, -1.25, -1.2, -1.15, -1.1, -1.05,
                -1.0, -0.95, -0.9, -0.85, -0.8, -0.75, -0.7, -0.65, -0.6, -0.55,
                -0.5, -0.45, -0.4, -0.35, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05,
                0.0,  0.05,  0.1,  0.15,  0.2,  0.25,  0.3,  0.35,  0.4,  0.45,
                0.5,  0.55,  0.6,  0.65,  0.7,  0.75,  0.8,  0.85,  0.9,  0.95,
                1.0,  1.05,  1.1,  1.15,  1.2,  1.25,  1.3,  1.35,  1.4,  1.45,
                1.5,  1.55,  1.6,  1.65,  1.7,  1.75,  1.8,  1.85,  1.9,  1.95,
                2.0,  2.05,  2.1,  2.15,  2.2,  2.25,  2.3,  2.35,  2.4,  2.45,
                2.5,  2.55,  2.6,  2.65,  2.7,  2.75,  2.8,  2.85,  2.9,  2.95,
                3.0,  3.05,  3.1,  3.15,  3.2,  3.25,  3.3,  3.35,  3.4,  3.45,
                3.5
            ]
        elif var == 'pt':
            bin = [0, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20, 22, 25, 30, 35, 45, 60, 75, 100, 140, 160, 180, 200, 250, 300, 500, 1000]
        elif var == 'pt2':
            bin = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 55, 60]

        for i in range(len(ratio_values)):
            if i < len(bin) -1:
                x_value = (bin[i] + bin[i + 1]) / 2
                #x_value = bin[i]
                graph1.SetPoint(i, x_value, ratio_values[i])
                graph1.SetPointError(i, 0.0, 0.0, ratio_errors_low[i], ratio_errors_up[i])
        graph1.SetMarkerStyle(2)
        graph1.SetMarkerColor(ROOT.kBlack)
        graph1.GetYaxis().SetRangeUser(0.85, 1.15)
        graph1.GetXaxis().SetTitle(vars_title[var])
        graph1.GetYaxis().SetTitleSize(0.05)
        graph1.GetXaxis().SetLabelSize(0.09)
        graph1.GetXaxis().SetTitleSize(0.09)
        graph1.GetYaxis().SetNdivisions(505)
        graph1.GetYaxis().SetLabelSize(0.09)
        if var == 'pt2':
            graph1.GetXaxis().SetLimits(0, 65.65)
        elif var == 'pt':
            pad2.SetLogx(1)
            graph1.GetXaxis().SetLimits(1,1000)
            graph1.GetYaxis().SetRangeUser(0.85, 1.15)
            graph1.GetXaxis().SetTitleOffset(1.3)
        elif var =='phi':
            graph1.GetXaxis().SetLimits(-3.84,3.84)
        elif var == 'eta':
            graph1.GetXaxis().SetLimits(-1.08,1.08)
        graph1.Draw("AP")

        latex2 = ROOT.TLatex()
        latex2.SetTextFont(42)
        latex2.SetTextSize(0.095)
        latex2.SetTextAngle(90)
        latex2.DrawLatexNDC(0.04, 0.37, f"{dataset_legend2}/{dataset_legend1}")

        pad2.Update()

        # Update the canvas
        cr1.Update()

        cr1.SaveAs(output_dir + "ratio_BMTF_" + key + ".png")

## OMTF
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        cr1= ROOT.TCanvas("canvas_ratio_2_" + key, "cr2" + key, 800, 800)
        cr1.SetLogx(0)

        #xlow, ylow, xup, yup
        pad1 = ROOT.TPad("pad1_1" + key, "pad1_1" + key, 0, 0.29, 1, 1)
        pad1.SetBottomMargin(0.02)  # Set bottom margin for pad1
        #pad1.SetLogx(0) 
        pad1.SetFrameLineWidth(2)
        pad1.SetGridx()
        pad1.SetGridy()
        pad1.Draw()
        pad1.cd()


        h_passed_OMTF1 = in_file1.Get("OMTF_" + key + "_passed")
        h_passed_OMTF1 = utils.add_overflow(h_passed_OMTF1)
        h_total_OMTF1 = in_file1.Get("OMTF_" + key + "_total")
        h_total_OMTF1 = utils.add_overflow(h_total_OMTF1)
        h_eff_OMTF1 = ROOT.TEfficiency(h_passed_OMTF1,h_total_OMTF1)
        h_eff_OMTF1.SetMarkerColor(CMS_color_2)
        h_eff_OMTF1.SetLineColor(CMS_color_2)
        h_eff_OMTF1.SetMarkerStyle(21)
        h_eff_OMTF1.Draw()
        #h_eff_OMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
        cr1.Update()
        graph = h_eff_OMTF1.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.1)
        if var == "pt":
            pad1.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "nPV":
            graph.GetXaxis().SetLimits(0,70)
        graph.GetXaxis().SetTitle("")
        graph.GetXaxis().SetLabelSize(0)
        cr1.Update()

        h_passed_OMTF2 = in_file2.Get("OMTF_" + key + "_passed")
        h_passed_OMTF2 = utils.add_overflow(h_passed_OMTF2)
        h_total_OMTF2 = in_file2.Get("OMTF_" + key + "_total")
        h_total_OMTF2 = utils.add_overflow(h_total_OMTF2)
        h_eff_OMTF2 = ROOT.TEfficiency(h_passed_OMTF2,h_total_OMTF2)
        h_eff_OMTF2.SetMarkerColor(CMS_color_3)
        h_eff_OMTF2.SetLineColor(CMS_color_3)
        h_eff_OMTF2.SetMarkerStyle(25)
        h_eff_OMTF2.Draw("same")


        leg = ROOT.TLegend(0.7,0.05,0.82,0.16)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_OMTF1,f"{dataset_legend1}: OMTF","lep")
        leg.AddEntry(h_eff_OMTF2,f"{dataset_legend2}: OMTF","lep")


        leg.Draw()

        latex.SetTextSize(0.035)
        #latex.DrawLatexNDC(0.80,0.91,dataset_legend)
        if var == "eta" or var == "phi" or var == "nPV":
            # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
            latex.DrawLatexNDC(0.14, 0.19, quality_label)
            latex.DrawLatexNDC(0.14, 0.12, pt_l1_label)
            latex.DrawLatexNDC(0.14, 0.06, pt_reco_label)
        else:
            latex.DrawLatexNDC(0.74, 0.18, pt_l1_label)
            latex.DrawLatexNDC(0.71, 0.25, quality_label)
        # utils.add_cms_label_out(L,T)
        latex.SetTextSize(0.0585)
        latex.DrawLatexNDC(0.1, 0.91, "#font[61]{CMS}")
        latex.SetTextSize(0.045)
        latex.DrawLatexNDC(0.185, 0.91, "#font[52]{Preliminary}")

        pad1.Update()
        cr1.cd()
        pad2 = ROOT.TPad("pad2_1" + key, "pad2_1" + key, 0, 0, 1, 0.29)
        pad2.SetTopMargin(0.03)  # Set top margin for pad2
        pad2.SetBottomMargin(0.3)  # Set bottom margin for pad2
        pad2.SetGridy()  # Add horizontal grid lines to pad2
        pad2.SetFrameLineWidth(2)
        pad2.Draw()
        pad2.cd()

        hist1_eff = h_eff_OMTF1.Clone()
        hist2_eff = h_eff_OMTF2.Clone()
        efficiency_values1, error_low_values1, error_up_values1 = utils.efficiency_to_vector(hist1_eff)
        efficiency_values2, error_low_values2, error_up_values2 = utils.efficiency_to_vector(hist2_eff)
        ratio_values, ratio_errors_low, ratio_errors_up = utils.calculate_ratio_with_error(
        efficiency_values2, error_low_values2, error_up_values2,
        efficiency_values1, error_low_values1, error_up_values1) 

        graph1 = ROOT.TGraphAsymmErrors(len(ratio_values))

        if var == 'eta':
            bin = [
                -2.4, -2.3, -2.2, -2.1, -2.0, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0, -0.9,
                -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
                0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4
            ]
        elif var == 'phi':
            bin = [
                -3.5, -3.45, -3.4, -3.35, -3.3, -3.25, -3.2, -3.15, -3.1, -3.05,
                -3.0, -2.95, -2.9, -2.85, -2.8, -2.75, -2.7, -2.65, -2.6, -2.55,
                -2.5, -2.45, -2.4, -2.35, -2.3, -2.25, -2.2, -2.15, -2.1, -2.05,
                -2.0, -1.95, -1.9, -1.85, -1.8, -1.75, -1.7, -1.65, -1.6, -1.55,
                -1.5, -1.45, -1.4, -1.35, -1.3, -1.25, -1.2, -1.15, -1.1, -1.05,
                -1.0, -0.95, -0.9, -0.85, -0.8, -0.75, -0.7, -0.65, -0.6, -0.55,
                -0.5, -0.45, -0.4, -0.35, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05,
                0.0,  0.05,  0.1,  0.15,  0.2,  0.25,  0.3,  0.35,  0.4,  0.45,
                0.5,  0.55,  0.6,  0.65,  0.7,  0.75,  0.8,  0.85,  0.9,  0.95,
                1.0,  1.05,  1.1,  1.15,  1.2,  1.25,  1.3,  1.35,  1.4,  1.45,
                1.5,  1.55,  1.6,  1.65,  1.7,  1.75,  1.8,  1.85,  1.9,  1.95,
                2.0,  2.05,  2.1,  2.15,  2.2,  2.25,  2.3,  2.35,  2.4,  2.45,
                2.5,  2.55,  2.6,  2.65,  2.7,  2.75,  2.8,  2.85,  2.9,  2.95,
                3.0,  3.05,  3.1,  3.15,  3.2,  3.25,  3.3,  3.35,  3.4,  3.45,
                3.5
            ]
        elif var == 'pt':
            bin = [0, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20, 22, 25, 30, 35, 45, 60, 75, 100, 140, 160, 180, 200, 250, 300, 500, 1000]
        elif var == 'pt2':
            bin = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 55, 60]

        for i in range(len(ratio_values)):
            if i < len(bin) -1:
                x_value = (bin[i] + bin[i + 1]) / 2
                #x_value = bin[i]
                graph1.SetPoint(i, x_value, ratio_values[i])
                graph1.SetPointError(i, 0.0, 0.0, ratio_errors_low[i], ratio_errors_up[i])
        graph1.SetMarkerStyle(2)
        graph1.SetMarkerColor(ROOT.kBlack)
        graph1.GetYaxis().SetRangeUser(0.85, 1.15)
        graph1.GetXaxis().SetTitle(vars_title[var])
        graph1.GetYaxis().SetTitleSize(0.05)
        graph1.GetXaxis().SetLabelSize(0.09)
        graph1.GetXaxis().SetTitleSize(0.09)
        graph1.GetYaxis().SetNdivisions(505)
        graph1.GetYaxis().SetLabelSize(0.09)
        if var == 'pt2':
            graph1.GetXaxis().SetLimits(0, 65.65)
        elif var == 'pt':
            pad2.SetLogx(1)
            graph1.GetXaxis().SetLimits(1,1000)
            graph1.GetYaxis().SetRangeUser(0.85, 1.15)
            graph1.GetXaxis().SetTitleOffset(1.3)
        elif var =='phi':
            graph1.GetXaxis().SetLimits(-3.84,3.84)
        elif var == 'eta':
            graph1.GetXaxis().SetLimits(-1.56,1.56)
        graph1.Draw("AP")

        latex2 = ROOT.TLatex()
        latex2.SetTextFont(42)
        latex2.SetTextSize(0.095)
        latex2.SetTextAngle(90)
        latex2.DrawLatexNDC(0.04, 0.37, f"{dataset_legend2}/{dataset_legend1}")

        pad2.Update()

        # Update the canvas
        cr1.Update()

        cr1.SaveAs(output_dir + "ratio_OMTF_" + key + ".png")


## EMTF
for wp in WPs:
    for var in vars_title:
        key = wp + "_" + var
        cr1= ROOT.TCanvas("canvas_ratio_3_" + key, "cr2" + key, 800, 800)
        cr1.SetLogx(0)

        #xlow, ylow, xup, yup
        pad1 = ROOT.TPad("pad1_1" + key, "pad1_1" + key, 0, 0.29, 1, 1)
        pad1.SetBottomMargin(0.02)  # Set bottom margin for pad1
        #pad1.SetLogx(0) 
        pad1.SetFrameLineWidth(2)
        pad1.SetGridx()
        pad1.SetGridy()
        pad1.Draw()
        pad1.cd()

        h_passed_EMTF1 = in_file1.Get("EMTF_" + key + "_passed")
        h_passed_EMTF1 = utils.add_overflow(h_passed_EMTF1)
        h_total_EMTF1 = in_file1.Get("EMTF_" + key + "_total")
        h_total_EMTF1 = utils.add_overflow(h_total_EMTF1)
        h_eff_EMTF1 = ROOT.TEfficiency(h_passed_EMTF1,h_total_EMTF1)
        h_eff_EMTF1.SetMarkerColor(CMS_color_4)
        h_eff_EMTF1.SetLineColor(CMS_color_4)
        h_eff_EMTF1.SetMarkerStyle(22)
        h_eff_EMTF1.SetMarkerSize(1.3)
        h_eff_EMTF1.Draw()
        #h_eff_EMTF1.SetTitle(";" + vars_title[var] + ";Efficiency")
        cr1.Update()
        graph = h_eff_EMTF1.GetPaintedGraph() 
        graph.SetMinimum(0)
        graph.SetMaximum(1.1)
        if var == "pt":
            pad1.SetLogx(1)
            graph.GetXaxis().SetLimits(1,1000)
            graph.GetXaxis().SetTitleOffset(1.3)
        if var == "nPV":
            graph.GetXaxis().SetLimits(0,70)
        graph.GetXaxis().SetTitle("")
        graph.GetXaxis().SetLabelSize(0)
        cr1.Update()

        h_passed_EMTF2 = in_file2.Get("EMTF_" + key + "_passed")
        h_passed_EMTF2 = utils.add_overflow(h_passed_EMTF2)
        h_total_EMTF2 = in_file2.Get("EMTF_" + key + "_total")
        h_total_EMTF2 = utils.add_overflow(h_total_EMTF2)
        h_eff_EMTF2 = ROOT.TEfficiency(h_passed_EMTF2,h_total_EMTF2)
        h_eff_EMTF2.SetMarkerColor(CMS_color_5)
        h_eff_EMTF2.SetLineColor(CMS_color_5)
        h_eff_EMTF2.SetMarkerStyle(26)
        h_eff_EMTF2.Draw("same")


        leg = ROOT.TLegend(0.7,0.05,0.82,0.16)
        leg.SetFillStyle(0)
        leg.AddEntry(h_eff_EMTF1,f"{dataset_legend1}: EMTF","lep")
        leg.AddEntry(h_eff_EMTF2,f"{dataset_legend2}: EMTF","lep")
        leg.Draw()

        latex.SetTextSize(0.035)
        #latex.DrawLatexNDC(0.80,0.91,dataset_legend)
        if var == "eta" or var == "phi" or var == "nPV":
            # latex.DrawLatexNDC(0.54, 0.41, "p^{#mu,Reco}_{T} #geq 5 GeV")
            latex.DrawLatexNDC(0.14, 0.19, quality_label)
            latex.DrawLatexNDC(0.14, 0.12, pt_l1_label)
            latex.DrawLatexNDC(0.14, 0.06, pt_reco_label)
        else:
            latex.DrawLatexNDC(0.74, 0.18, pt_l1_label)
            latex.DrawLatexNDC(0.71, 0.25, quality_label)
        # utils.add_cms_label_out(L,T)
        latex.SetTextSize(0.0585)
        latex.DrawLatexNDC(0.1, 0.91, "#font[61]{CMS}")
        latex.SetTextSize(0.045)
        latex.DrawLatexNDC(0.185, 0.91, "#font[52]{Preliminary}")

        pad1.Update()
        cr1.cd()
        pad2 = ROOT.TPad("pad2_1" + key, "pad2_1" + key, 0, 0, 1, 0.29)
        pad2.SetTopMargin(0.03)  # Set top margin for pad2
        pad2.SetBottomMargin(0.3)  # Set bottom margin for pad2
        pad2.SetGridy()  # Add horizontal grid lines to pad2
        pad2.SetFrameLineWidth(2)
        pad2.Draw()
        pad2.cd()

        hist1_eff = h_eff_EMTF1.Clone()
        hist2_eff = h_eff_EMTF2.Clone()
        efficiency_values1, error_low_values1, error_up_values1 = utils.efficiency_to_vector(hist1_eff)
        efficiency_values2, error_low_values2, error_up_values2 = utils.efficiency_to_vector(hist2_eff)
        ratio_values, ratio_errors_low, ratio_errors_up = utils.calculate_ratio_with_error(
        efficiency_values2, error_low_values2, error_up_values2,
        efficiency_values1, error_low_values1, error_up_values1) 

        graph1 = ROOT.TGraphAsymmErrors(len(ratio_values))

        if var == 'eta':
            bin = [
                -2.4, -2.3, -2.2, -2.1, -2.0, -1.9, -1.8, -1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1.0, -0.9,
                -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
                0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4
            ]
        elif var == 'phi':
            bin = [
                -3.5, -3.45, -3.4, -3.35, -3.3, -3.25, -3.2, -3.15, -3.1, -3.05,
                -3.0, -2.95, -2.9, -2.85, -2.8, -2.75, -2.7, -2.65, -2.6, -2.55,
                -2.5, -2.45, -2.4, -2.35, -2.3, -2.25, -2.2, -2.15, -2.1, -2.05,
                -2.0, -1.95, -1.9, -1.85, -1.8, -1.75, -1.7, -1.65, -1.6, -1.55,
                -1.5, -1.45, -1.4, -1.35, -1.3, -1.25, -1.2, -1.15, -1.1, -1.05,
                -1.0, -0.95, -0.9, -0.85, -0.8, -0.75, -0.7, -0.65, -0.6, -0.55,
                -0.5, -0.45, -0.4, -0.35, -0.3, -0.25, -0.2, -0.15, -0.1, -0.05,
                0.0,  0.05,  0.1,  0.15,  0.2,  0.25,  0.3,  0.35,  0.4,  0.45,
                0.5,  0.55,  0.6,  0.65,  0.7,  0.75,  0.8,  0.85,  0.9,  0.95,
                1.0,  1.05,  1.1,  1.15,  1.2,  1.25,  1.3,  1.35,  1.4,  1.45,
                1.5,  1.55,  1.6,  1.65,  1.7,  1.75,  1.8,  1.85,  1.9,  1.95,
                2.0,  2.05,  2.1,  2.15,  2.2,  2.25,  2.3,  2.35,  2.4,  2.45,
                2.5,  2.55,  2.6,  2.65,  2.7,  2.75,  2.8,  2.85,  2.9,  2.95,
                3.0,  3.05,  3.1,  3.15,  3.2,  3.25,  3.3,  3.35,  3.4,  3.45,
                3.5
            ]
        elif var == 'pt':
            bin = [0, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20, 22, 25, 30, 35, 45, 60, 75, 100, 140, 160, 180, 200, 250, 300, 500, 1000]
        elif var == 'pt2':
            bin = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 55, 60]

        for i in range(len(ratio_values)):
            if i < len(bin) -1:
                x_value = (bin[i] + bin[i + 1]) / 2
                #x_value = bin[i]
                graph1.SetPoint(i, x_value, ratio_values[i])
                graph1.SetPointError(i, 0.0, 0.0, ratio_errors_low[i], ratio_errors_up[i])
        graph1.SetMarkerStyle(2)
        graph1.SetMarkerColor(ROOT.kBlack)
        graph1.GetYaxis().SetRangeUser(0.85, 1.15)
        graph1.GetXaxis().SetTitle(vars_title[var])
        graph1.GetYaxis().SetTitleSize(0.05)
        graph1.GetXaxis().SetLabelSize(0.09)
        graph1.GetXaxis().SetTitleSize(0.09)
        graph1.GetYaxis().SetNdivisions(505)
        graph1.GetYaxis().SetLabelSize(0.09)
        if var == 'pt2':
            graph1.GetXaxis().SetLimits(0, 65.65)
        elif var == 'pt':
            pad2.SetLogx(1)
            graph1.GetXaxis().SetLimits(1,1000)
            graph1.GetYaxis().SetRangeUser(0.85, 1.15)
            graph1.GetXaxis().SetTitleOffset(1.3)
        elif var =='phi':
            graph1.GetXaxis().SetLimits(-3.84,3.84)
        elif var == 'eta':
            graph1.GetXaxis().SetLimits(-2.88,2.88)
        graph1.Draw("AP")

        latex2 = ROOT.TLatex()
        latex2.SetTextFont(42)
        latex2.SetTextSize(0.095)
        latex2.SetTextAngle(90)
        latex2.DrawLatexNDC(0.04, 0.37, f"{dataset_legend2}/{dataset_legend1}")

        pad2.Update()

        # Update the canvas
        cr1.Update()

        cr1.SaveAs(output_dir + "ratio_EMTF_" + key + ".png")