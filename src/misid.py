#! /usr/bin/env python

## script to make plots for muon charge misidentification using official NANOAOD

import math
import ROOT
from array import array
import argparse
import sys
import os.path
import FWCore.PythonUtilities.LumiList as LumiList

## Configuration settings
MAX_FILE = -1        ## Maximum number of input files (use "-1" for unlimited)
MAX_EVT  = -1    ## Maximum number of events to process
PRT_EVT  = 10000     ## Print every Nth event
MIN_dR_TP      = 0.4   ## Minimum dR for T&P matching (they need to be well separated)
MAX_dR_L1_T    = 0.1   ## Maximum dR for L1T-tag matching
MAX_dR_L1_P    = 0.2   ## Maximum dR for L1T-probe matching
TAG_PT         = 27    ## Minimum offline pT for tag muon
L1_QUAL        = 12    ## Minimum L1 quality for Tag matching
REQ_ZMASS = True
#######################

#------------------------------------------------------------------------------

## True if passed the trigger (bit indices 3 and 10)
def passedTrig(muon_eta, muon_phi, trg_eta, trg_phi, trg_id, filterBits):

  passed = False

  for idx, (trg_eta, trg_phi) in enumerate(zip(trg_eta,trg_phi)):
    if trg_id[idx] != 13: continue

    dphi = abs(math.acos(math.cos(trg_phi - muon_phi)))
    deta = abs(trg_eta - muon_eta)
    dr = math.sqrt(deta*deta+dphi*dphi)
    if dr <= 0.1: 
      if filterBits[idx]>>3&1 == 1 and filterBits[idx]>>10&1 == 1:
        passed = True

  return passed

def CalcDPhi( phi1, phi2 ):
  dPhi = math.acos( math.cos( phi1 - phi2 ) )
  if math.sin( phi1 - phi2 ) < 0: dPhi *= -1
  return dPhi

def CalcDR( eta1, phi1, eta2, phi2 ):
  return math.sqrt( math.pow(CalcDPhi(phi1, phi2), 2) + math.pow(eta1 - eta2, 2) )

#------------------------------------------------------------------------------

latex = ROOT.TLatex()
latex.SetTextSize(0.04)

## parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, help='input file')
parser.add_argument('-o', type=str, help='output dir')
parser.add_argument('--json', type=str, help='json file')
args = parser.parse_args()

input_file = args.i
if not input_file:
  sys.exit("No input file given")
output_dir = args.o

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetMarkerStyle(20)
ROOT.gStyle.SetMarkerSize(1)
ROOT.gStyle.SetTitleOffset(1.3)
ROOT.gROOT.ForceStyle()


## L1NTuple branches
tree  = ROOT.TChain('Events')

canvas = ROOT.TCanvas("c","c",750,750)
canvas.SetGridy()
canvas.SetGridx()

## Load input files
print ("Input file: ", input_file)
tree.Add(input_file)

#------------------------------------------------------------------------------

## Trigger settings
trig_WP = {}
trig_WP['SingleMu']  = [12]

trig_TF = {}
trig_TF['uGMT'] = [0.00, 2.40]
trig_TF['BMTF'] = [0.00, 0.83]
trig_TF['OMTF'] = [0.83, 1.24]
trig_TF['EMTF'] = [1.24, 2.40]


trg_pt = {}
trg_pt['SingleMu']  = [22]

#------------------------------------------------------------------------------

## ================ Histograms ======================
scale_pt_temp = [0, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20, 22, 25, 30, 35, 45, 60, 75, 100, 140, 160, 180, 200, 250, 300, 500, 1000]
scale_pt_temp_2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 55, 60]
scale_pt_2  = array('d', scale_pt_temp_2)
scale_pt  = array('d', scale_pt_temp)
scale_nPV_temp = [i for i in range(0,72,2)]
scale_nPV  = array('d', scale_nPV_temp)

eta_bins = [48, -2.4, 2.4]
phi_bins = [140, -3.5, 3.5]

h_dr ={}
h_misid_pt = {}
h_misid_pt_2={}
h_misid_phi_eta ={}
h_misid_l1_phi_eta ={}

for TF in trig_TF.keys():
  key = TF + '_' 

  h_dr[key] = ROOT.TH1F("h_dr_%s" % key,";#DeltaR;",100,0,1)

  h_misid_pt[key] = ROOT.TEfficiency("h_misid_pt_%s" % key,";Reco p_{T} [GeV];Charge misidentification", len(scale_pt_temp)-1,  scale_pt)
  h_misid_pt_2[key] = ROOT.TEfficiency("h_misid_pt2_%s" % key,";Reco p_{T} [GeV];Charge misidentification", len(scale_pt_temp_2)-1,  scale_pt_2)
  h_misid_phi_eta[key] = ROOT.TEfficiency("h_misid_phi_eta%s" % key,";#eta;#phi [rad]", eta_bins[0], eta_bins[1], eta_bins[2], phi_bins[0], phi_bins[1], phi_bins[2])
  h_misid_l1_phi_eta[key] = ROOT.TEfficiency("h_misid_l1_phi_eta%s" % key,";#eta;#phi [rad]", eta_bins[0], eta_bins[1], eta_bins[2], phi_bins[0], phi_bins[1], phi_bins[2])
      

  h_misid_pt[key].SetDirectory(0)
  h_misid_pt_2[key].SetDirectory(0)
  h_misid_phi_eta[key].SetDirectory(0)
  h_misid_l1_phi_eta[key].SetDirectory(0)
## =========================================

## load json file
if args.json is not None:
    json_file = LumiList.LumiList(filename=args.json)
else:
    json_file = None

# Loop over over events in TFile
for iEvt in range(tree.GetEntries()):
  if MAX_EVT > 0 and iEvt > MAX_EVT: break
  if iEvt % PRT_EVT == 0: print ('Event #', iEvt)

  tree.GetEntry(iEvt)

  run = tree.run
  luminosityBlock = tree.luminosityBlock
  if json_file is not None:
    if not json_file.contains(run,luminosityBlock): 
      continue


  # Require HLT muon trigger
  if tree.HLT_IsoMu27 != 1 or tree.HLT_Mu50 != 1: continue

  # good vertex
  if tree.Flag_goodVertices != 1: continue

  nPV = tree.PV_npvs

  #################################################################
  ###  Loop over RECO and L1 muons to find valid matched muons  ###
  #################################################################
  for i in range(tree.nMuon):

    recoCharge = tree.Muon_charge[i]
    recoPt = tree.Muon_pt[i]

    ##Compute offline muon coordinates
    recoEta = tree.Muon_eta[i]
    recoPhi = tree.Muon_phi[i]

    ##Require to be valid
    recoAbsEta = abs(recoEta)

    if recoAbsEta > 2.5: continue

    ## Require muon to pass Muon POG tight ID
    recoIsTight = tree.Muon_tightId[i]
    recoIsLoose = tree.Muon_looseId[i]
    if not recoIsTight: continue

    ## Require prompt muons
    recoDxy = tree.Muon_dxy[i]
    recoDz  = tree.Muon_dz[i]
    if abs(recoDxy) > 0.2 or abs(recoDz) > 0.5: continue

    # ##Require muon to pass trigger 
    # muon_passed_trigger = passedTrig(recoEta, recoPhi, tree.TrigObj_eta, tree.TrigObj_phi, tree.TrigObj_id, tree.TrigObj_filterBits)
    # if not muon_passed_trigger: continue

    ## Require muon to pass pT and isolation cuts
    #if tree.Muon_pt[i]  < TAG_PT: continue

    # find matching L1 muon
    # for iL1 in range(tree.nL1Mu):
    for iL1 in range(len(tree.L1Mu_pt)):
      if tree.L1Mu_hwQual[iL1] < L1_QUAL: continue  # Minimum quality of 12
      if tree.L1Mu_bx[iL1] != 0: continue           # Bunch Crossing = 0 
      #if tree.L1Mu_pt[iL1]   < TAG_PT - 4.01: continue

      l1_phi = tree.L1Mu_phiAtVtx[iL1]
      l1_eta = tree.L1Mu_etaAtVtx[iL1]
      l1_pt = tree.L1Mu_pt[iL1]
      l1_charge = tree.L1Mu_hwCharge[iL1]

      #For some reason charges at L1 level are messed up. If q = 0 change it to +1 and if q = 1 change it to -1 
      if l1_charge == 0:
        l1_charge = 1
      else:
        l1_charge = -1

      #Matching condition
      if CalcDR( l1_eta, l1_phi, recoEta, recoPhi ) < 0.1:
        if recoCharge == l1_charge:
          wrong_charge = False
        else:
          wrong_charge = True
        for TF in trig_TF.keys():
          ## Only consider reco muons in TF eta range
          if not (recoAbsEta > trig_TF[TF][0] and recoAbsEta < trig_TF[TF][1]): continue
          key = TF + '_' 

          h_dr[key].Fill(CalcDR( l1_eta, l1_phi, recoEta, recoPhi ))

          h_misid_pt[key].Fill(wrong_charge,recoPt)
          h_misid_pt_2[key].Fill(wrong_charge,recoPt)
          h_misid_phi_eta[key].Fill(wrong_charge,recoEta,recoPhi)
          h_misid_l1_phi_eta[key].Fill(wrong_charge, l1_eta, l1_phi)

  ## End loop: for i in range(reco_tree.Muon.nMuons):

## End loop: for iEvt in range(tree.GetEntries()):

## write output to root file
out_file = ROOT.TFile(output_dir + "/" + os.path.basename(input_file), "RECREATE")
out_file.cd()


for tf in trig_TF:
  key = tf + '_' 

  # pt2
  h_misid_pt_2[key].Draw()
  h_misid_pt_2[key].Write()
      
  h_passed_pt2 = h_misid_pt_2[key].GetPassedHistogram()
  h_passed_pt2.SetName(key + "_pt2_passed")
  h_passed_pt2.Write()
  h_total_pt2 = h_misid_pt_2[key].GetTotalHistogram()
  h_total_pt2.SetName(key + "_pt2_total")
  h_total_pt2.Write()

  # pt
  h_misid_pt[key].Draw()
  h_misid_pt[key].Write()

  h_passed_pt = h_misid_pt[key].GetPassedHistogram()
  h_passed_pt.SetName(key + "_pt_passed")
  h_passed_pt.Write()
  h_total_pt = h_misid_pt[key].GetTotalHistogram()
  h_total_pt.SetName(key + "_pt_total")
  h_total_pt.Write()

  # phi_eta
  h_misid_phi_eta[key].Draw()
  h_misid_phi_eta[key].Write()

  h_passed_phi_eta = h_misid_phi_eta[key].GetPassedHistogram()
  h_passed_phi_eta.SetName(key + "_phi_eta_passed")
  h_passed_phi_eta.Write()
  h_total_phi_eta = h_misid_phi_eta[key].GetTotalHistogram()
  h_total_phi_eta.SetName(key + "_phi_eta_total")
  h_total_phi_eta.Write()

  # l1_phi_eta
  h_misid_l1_phi_eta[key].Draw()
  h_misid_l1_phi_eta[key].Write()

  h_passed_l1_phi_eta = h_misid_l1_phi_eta[key].GetPassedHistogram()
  h_passed_l1_phi_eta.SetName(key + "l1_phi_eta_passed")
  h_passed_l1_phi_eta.Write()
  h_total_l1_phi_eta = h_misid_l1_phi_eta[key].GetTotalHistogram()
  h_total_l1_phi_eta.SetName(key + "l1_phi_eta_total")
  h_total_l1_phi_eta.Write()

  h_dr[key].Draw()
  h_dr[key].Write()

out_file.Write()
