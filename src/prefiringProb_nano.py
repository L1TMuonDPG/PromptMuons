#! /usr/bin/env python

########################################################
## prefiring_prob.py   
## Ioannis Paraskevas <ioannis.paraskevas@cern.ch>
########################################################

import math
import ROOT
from array import array
import argparse
import sys
import os.path
import FWCore.PythonUtilities.LumiList as LumiList

## True if passed the trigger (bit index 3)
def passedTrig(muon_eta, muon_phi, trg_eta, trg_phi, trg_id, filterBits):

  passed = False

  for idx, (trg_eta, trg_phi) in enumerate(zip(trg_eta,trg_phi)):
    if trg_id[idx] != 13: continue

    dphi = abs(math.acos(math.cos(trg_phi - muon_phi)))
    deta = abs(trg_eta - muon_eta)
    dr = math.sqrt(deta*deta+dphi*dphi)
    if dr <= 0.1: 
      if filterBits[idx]>>3&1 == 1:
        passed = True

  return passed

## Configuration settings
MAX_EVT  = -1    ## Maximum number of events to process
PRT_EVT  = 10000     ## Print every Nth event
#######################

def CalcDPhi( phi1, phi2 ):
  dPhi = math.acos( math.cos( phi1 - phi2 ) )
  if math.sin( phi1 - phi2 ) < 0: dPhi *= -1
  return dPhi

def CalcDR( eta1, phi1, eta2, phi2 ):
  return math.sqrt( math.pow(CalcDPhi(phi1, phi2), 2) + math.pow(eta1 - eta2, 2) )

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

l1_pt_cuts = [10,22]

l1_qual_dict = {
  "tight": 12,
  "medium": 8,
  "loose": 4,
  "open": 0, 
}

trig_TF = {}
trig_TF['uGMT'] = [0.00, 2.40]

## absolute
trig_TF['BMTF'] = [0.00, 0.83]
trig_TF['OMTF'] = [0.83, 1.24]
trig_TF['EMTF'] = [1.24, 2.40]

## neg/pos
trig_TF['posBMTF'] = [0.00, 0.83]
trig_TF['negBMTF'] = [-0.83, 0.00]
trig_TF['posOMTF'] = [0.83, 1.24]
trig_TF['negOMTF'] = [-1.24, -0.83]
trig_TF['posEMTF'] = [1.24, 2.40]
trig_TF['negEMTF'] = [-2.40, -1.24]

## ================ Histograms ======================
# scale_pt_temp = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 55, 60]
# scale_pt_temp = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 100]
scale_pt_temp = [0,1000]
scale_pt  = array('d', scale_pt_temp)

h_l1_pt = ROOT.TH1F("h_l1_pt","",50,0,50)
h_l1_eta = ROOT.TH1F("h_l1_eta","",50,-2.5,2.5)
h_l1_phi = ROOT.TH1F("h_l1_phi","",80,-4,4)

h_reco_pt = ROOT.TH1F("h_reco_pt","",50,0,50)
h_reco_eta = ROOT.TH1F("h_reco_eta","",50,-2.5,2.5)
h_reco_phi = ROOT.TH1F("h_reco_phi","",80,-4,4)

h_prefiring_prob = {}
h_dR_reco_l1 = {}

## count unprefiriable events
h_n_unprefirable = ROOT.TH1F("h_n_unprefirable","",1,0,1)
h_n_events = ROOT.TH1F("h_n_events","",1,0,1)

for tf in trig_TF.keys():
  for pt_cut in l1_pt_cuts:
    key = str(pt_cut) + "_" + tf
    h_prefiring_prob[key] = ROOT.TEfficiency("h_prefiring_prob_"+key,";Reco p_{T} [GeV];Prefiring Probability", len(scale_pt_temp)-1,  scale_pt)
    h_prefiring_prob[key].GetPassedHistogram().SetName("h_prefiring_prob_" + key + "_passed")
    h_prefiring_prob[key].GetTotalHistogram().SetName("h_prefiring_prob_" + key + "_total")
    h_dR_reco_l1[key] = ROOT.TH1F("h_dR_reco_l1_"+key,"",100,0,1)
## ================================================

## load json file
json_file = LumiList.LumiList(filename = args.json)

n_unprefirible_events = 0
n_events = 0

# Loop over over events in TFile
for iEvt in range(tree.GetEntries()):
  if MAX_EVT > 0 and iEvt > MAX_EVT: break
  if iEvt % PRT_EVT == 0: print ('Event #', iEvt)
  n_events += 1

  tree.GetEntry(iEvt)

  run = tree.run
  luminosityBlock = tree.luminosityBlock
  if not json_file.contains(run,luminosityBlock): continue

  # if not (tree.L1_UnprefireableEvent or tree.L1_FirstBunchInTrain): continue
  if not tree.L1_UnprefireableEvent: continue
  n_unprefirible_events += 1

  ##### CONTROL PLOTS #####
  for l1mu in range(tree.nL1Mu):
    l1_eta = tree.L1Mu_etaAtVtx[l1mu]
    l1_phi = tree.L1Mu_phiAtVtx[l1mu]
    l1_bx = tree.L1Mu_bx[l1mu]
    l1_pt = tree.L1Mu_pt[l1mu]

    h_l1_pt.Fill(l1_pt)
    h_l1_eta.Fill(l1_phi)
    h_l1_phi.Fill(l1_eta)

  for iTag in range(tree.nMuon):

    ## Compute tag muon coordinates at 2nd station, require to be valid
    recoEta = tree.Muon_eta[iTag]
    recoPhi = tree.Muon_phi[iTag]
    recoPt = tree.Muon_pt[iTag]

    recoAbsEta = abs(recoEta)

    if recoAbsEta > 2.5: continue
    if tree.Muon_tightId[iTag] != 1:   continue
    if tree.Muon_isTracker[iTag] != 1:   continue

    h_reco_pt.Fill(recoPt)
    h_reco_eta.Fill(recoEta)
    h_reco_phi.Fill(recoPhi)
  #########################

  if tree.nMuon < 2: continue

  for tf in trig_TF.keys():
    for pt_cut in l1_pt_cuts:
      key = str(pt_cut) + "_" + tf

      iTags = []
      iProbes = []
      iL1_matched = []

      ## find all tag muons
      for iTag in range(tree.nMuon):

        recoEta = tree.Muon_eta[iTag]
        recoPhi = tree.Muon_phi[iTag]
        recoPt = tree.Muon_pt[iTag]
        
        recoAbsEta = abs(recoEta)

        if recoAbsEta > 2.5: continue
        if recoPt < 30: continue
        if tree.Muon_tightId[iTag] != 1:   continue
        if tree.Muon_isTracker[iTag] != 1:   continue

        muon_passed_trigger = passedTrig(tree.Muon_eta[iTag], tree.Muon_phi[iTag], tree.TrigObj_eta, tree.TrigObj_phi, tree.TrigObj_id, tree.TrigObj_filterBits)
        if not muon_passed_trigger: continue

        if tree.Muon_highPurity[iTag] != 1: continue
        iTags.append(iTag)

      ## find all probe muons
      for iProbe in range(tree.nMuon):

        recoEta = tree.Muon_eta[iProbe]
        recoPhi = tree.Muon_phi[iProbe]

        recoAbsEta = abs(recoEta)

        if recoAbsEta > 2.5: continue

        matched = False

        for iL1 in range(tree.nL1Mu):
          l1_etaAtVtx = tree.L1Mu_etaAtVtx[iL1]
          l1_phiAtVtx = tree.L1Mu_phiAtVtx[iL1]
          l1_eta = tree.L1Mu_eta[iL1]
          l1_phi = tree.L1Mu_phi[iL1]
          l1_pt = tree.L1Mu_pt[iL1]
          l1_bx = tree.L1Mu_bx[iL1]
          l1_qual = tree.L1Mu_hwQual[iL1]
          # if l1_qual < l1_qual_dict[qual]: continue
          if l1_qual < 12: continue
          if l1_pt <= pt_cut: continue
          
          if tf in ["BMTF","OMTF","EMTF","uGMT"]:
            if not (abs(l1_eta) > trig_TF[tf][0] and abs(l1_eta) < trig_TF[tf][1]): continue    
          else:
            if not (l1_eta > trig_TF[tf][0] and l1_eta < trig_TF[tf][1]): continue

          dR_reco_l1 = CalcDR(l1_etaAtVtx,l1_phiAtVtx,recoEta,recoPhi)
          h_dR_reco_l1[key].Fill(dR_reco_l1)

          if dR_reco_l1 < 0.1:
            matched = True
            iL1_matched.append(iL1)
        
        if tree.Muon_tightId[iProbe] != 1: continue
        if tree.Muon_tkIsoId[iProbe] != 2: continue # tight tracker isolation
        if not matched: continue
        iProbes.append(iProbe)


      if len(iTags) == 0 or len(iProbes) == 0: continue

      ## consider tag-probe pairs
      for iTag in iTags:
        for iProbe in iProbes:
          if iTag == iProbe: continue

          for iL1 in iL1_matched:
            h_prefiring_prob[key].GetTotalHistogram().Fill(tree.Muon_pt[iProbe])
            if tree.L1Mu_bx[iL1] < 0:
              h_prefiring_prob[key].GetPassedHistogram().Fill(tree.Muon_pt[iProbe])

h_n_unprefirable.SetBinContent(1,n_unprefirible_events)
h_n_events.SetBinContent(1,n_events)

## write output to root file
out_file = ROOT.TFile(output_dir + "/" + os.path.basename(input_file), "RECREATE")
out_file.cd()

for tf in trig_TF.keys():
  for pt_cut in l1_pt_cuts:
    key = str(pt_cut) + "_" + tf

    h_prefiring_prob[key].GetPassedHistogram().Write()
    h_prefiring_prob[key].GetTotalHistogram().Write()
    h_prefiring_prob[key].Write()
    h_dR_reco_l1[key].Write()

h_l1_pt.Write()
h_l1_eta.Write()
h_l1_phi.Write()

h_reco_pt.Write()
h_reco_eta.Write()
h_reco_phi.Write()

h_n_unprefirable.Write()
h_n_events.Write()

out_file.Write()