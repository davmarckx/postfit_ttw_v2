#########################################################################
# plot and compare multiple theory distributions to a data distribution #
#########################################################################

import ROOT
import sys
import os
sys.path.append('../Tools/')
import histtools as ht
import plottools as pt
import matplotlib.pyplot as plt
from scipy import stats
from array import array

def plotdifferential(
    theoryhists,
    datahist,
    systhists=None,
    statdatahist=None,
    datahist_oviedo=None,
    statdatahist_oviedo=None,
    figname=None, title=None, xaxtitle=None, yaxtitle=None,
    dolegend=True, labellist=None, 
    colorlist=None,
    logy=False, ymaxlinfactor=1.6, yminlogfactor=0.2, ymaxlogfactor=100,
    drawoptions='', 
    lumitext='', extracmstext = 'Preliminary',
    ratiorange=None, ylims=None, yminzero=False,
    extrainfos=['testinfo'], infosize=None, infoleft=None, infotop=None,
    chi2info_old=['',''],
    chi2info_improved=['',''],
    writeuncs=False, 
    onlyoviedo=False,
    horizontal=False,
    two_ratiopannels=False):

    ### plot multiple overlaying histograms (e.g. for shape comparison)
    # note: the ratio plot will show ratios w.r.t. the first histogram in the list!
    # arguments:
    # - theoryhists, colorlist, labellist: lists of TH1, ROOT colors and labels respectively
    # - systhists: list of TH1 with systematic uncertainties on theoryhists
    # - datahist: TH1 with the measurement values
    # - statdatahist: TH1 with same bin contents as datahist but statistical-only errors
    # - figname: name of the figure to save (if None, do not save but return plot dictionary)
    # - title, xaxtitle, yaxtitle, figname: self-explanatory
    # - dolegend: boolean whether to make a legend (histogram title is used if no labellist)
    # - logy: boolean whether to make y-axis logarithmic
    # - ymaxlinfactor: factor by which to multiply maximum y value (for linear y-axis)
    # - yminlogfactor and ymaxlogfactor: same as above but for log scale
    # - drawoptions: string passed to TH1.Draw
    #   see https://root.cern/doc/master/classTHistPainter.html for a full list of options
    # - lumitext and extracmstext: luminosity value and extra text
    # - ratiorange: a tuple of (ylow,yhigh) for the ratio pad, default (0,2)
    # - ylims: a tuple of (ylow,yhigh) for the upper pad
    # - yminzero: whether to clip minimum y to zero.
    # - extrainfos is a list of strings with extra info to display
    # - infosize: font size of extra info
    # - infoleft: left border of extra info text (default leftmargin + 0.05)
    # - infotop: top border of extra info text (default 1 - topmargin - 0.1)

    pt.setTDRstyle()
    ROOT.gStyle.SetEndErrorSize(3)
    #ROOT.gStyle.SetErrorX()  
    ROOT.gROOT.SetBatch(ROOT.kTRUE)

    #for hist in theoryhists:
    #  hist.SetAxisRange(hist.GetBinLowEdge(1)+10,hist.GetBinLowEdge(-1)-0.1)

    #for hist in systhists:
    #  hist.SetAxisRange(hist.GetBinLowEdge(1)+10,hist.GetBinLowEdge(-1)-0.1)

    ### parse arguments
    if colorlist is None:
        colorlist = ([ROOT.kRed, ROOT.kAzure-3, ROOT.kGreen+1, ROOT.kAzure+6, ROOT.kViolet, ROOT.kMagenta-9,
                      ROOT.kOrange, ROOT.kGreen-1])
    if( len(theoryhists)>len(colorlist) ):
        raise Exception('ERROR in plotdifferential:'
	    +' theory histogram list is longer than color list')
    if(labellist is not None and len(labellist)!=len(theoryhists)):
        raise Exception('ERROR in plotdifferential:'
            +' length of label list does not agree with theory histogram list')
    if( systhists is not None and len(systhists)!=len(theoryhists) ):
        raise Exception('ERROR in plotdifferential:'
            +' length of systematic histogram list does not agree with theory histogram list')

    plotoviedo = False
    if statdatahist_oviedo != None and datahist_oviedo != None:
      plotoviedo = True
    ### define global parameters for size and positioning
    cheight = 600 # height of canvas
    cwidth = 600 # width of canvas
    rfrac = 0.25 # fraction of bottom plot showing the ratio
    # fonts and sizes:
    labelfont = 4; labelsize = 22
    axtitlefont = 4; axtitlesize = 26
    infofont = 4
    if infosize is None: infosize = 21
    legendfont = 4
    # margins and title offsets
    ytitleoffset = 1.5
    p1topmargin = 0.07 
    p1bottommargin = 0.03
    xtitleoffset = 4.5
    p2topmargin = 0.01
    p2bottommargin = 0.4
    leftmargin = 0.15
    rightmargin = 0.05
    # legend box
    pentryheight = 0.08
    nentries = 2 + len(theoryhists)
    if nentries>3: pentryheight = pentryheight*0.8
    plegendbox = ([leftmargin+0.25,1-p1topmargin-0.03-pentryheight*nentries,
                    1-rightmargin-0.01,1-p1topmargin-0.03])
    # extra info box parameters
    if infoleft is None: infoleft = leftmargin+0.05
    if infotop is None: infotop = 1-p1topmargin-0.1
    # marker properties for data
    markerstyle = 20
    markercolor = 1
    markersize = 1.05

    ### style operations on theory histograms
    for i,hist in enumerate(theoryhists):
        if hist is not None:
            hist.SetLineWidth(2)
            hist.SetLineColor(colorlist[i])
        if i == 0:
            hist.SetLineColorAlpha(colorlist[0], 0.8)
            hist.SetLineWidth(3)
            hist.SetLineStyle(9)

    ### style operations on uncertainty histograms (only for improved FxFx)
    if systhists is not None:
        for i,hist in enumerate(systhists):
            if hist is not None and i==1:
                hist.SetLineWidth(0)
                hist.SetMarkerStyle(0)
                hist.SetFillStyle(1001)#3254 is crossed
                hist.SetFillColorAlpha(ROOT.kAzure-9,1.)
                hist.SetMarkerSize(0)

    ### plotting seems not to handle histograms with zero error correctly,
    # so replace zero error by a small value
    if systhists is not None:
        for i,hist in enumerate(systhists):
            if hist is not None:
                for i in range(0,hist.GetNbinsX()+2):
                    if hist.GetBinError(i)==0:
                        hist.SetBinError(i, hist.GetBinContent(i)/1e6)

    ### style operations on data histogram
    datahist.SetMarkerStyle(markerstyle)
    datahist.SetMarkerColor(ROOT.kCyan+3)
    datahist.SetMarkerSize(markersize)
    datahist.SetLineColor(ROOT.kCyan+3)
    datahist.SetLineWidth(3)
    statdatahist.SetMarkerSize(0)
    statdatahist.SetLineColor(ROOT.kCyan+3)
    statdatahist.SetLineWidth(3)

    datahist_marker = datahist.Clone()
    datahist_marker.SetLineWidth(0)
    x = []
    y = []
    ex = []
    ey = []
    for i in range(1,datahist_marker.GetNbinsX()+1):
      y.append(datahist_marker.GetBinContent(i))
      x.append(datahist_marker.GetBinCenter(i))
      ey.append(0)
      ex.append(datahist_marker.GetBinWidth(i)/2)

    datahist_horizontal = ROOT.TGraphErrors(datahist_marker.GetNbinsX(),array( 'f',x),array( 'f',y),array( 'f',ex),array( 'f',ey))

    datahist_horizontal.SetLineColor(ROOT.kCyan+3)
    datahist_horizontal.SetLineWidth(3)

    if onlyoviedo:
     datahist.SetMarkerStyle(20)
     datahist.SetMarkerColor(ROOT.kBlue+3)
     datahist.SetMarkerSize(markersize)
     datahist.SetLineColor(ROOT.kBlue+3)
     datahist.SetLineWidth(3)
     statdatahist.SetMarkerSize(0)
     statdatahist.SetLineColor(ROOT.kBlue+3)
     statdatahist.SetLineWidth(3)

     datahist_marker.SetMarkerColor(ROOT.kWhite)
     datahist_marker.SetMarkerStyle(20)
     datahist_marker.SetMarkerSize(markersize-0.13)
    
     datahist_horizontal.SetLineColor(ROOT.kBlue+3)
     datahist_horizontal.SetLineWidth(3) 

    if plotoviedo:
     datahist_oviedo.SetMarkerStyle(20)#33
     datahist_oviedo.SetMarkerColor(ROOT.kBlue+3)
     datahist_oviedo.SetMarkerSize(markersize)#+0.8
     datahist_oviedo.SetLineColor(ROOT.kBlue+3)
     datahist_oviedo.SetLineWidth(3)
     statdatahist_oviedo.SetMarkerSize(0)
     statdatahist_oviedo.SetLineColor(ROOT.kBlue+3)
     statdatahist_oviedo.SetLineWidth(3)

     datahist_oviedo_marker = datahist_oviedo.Clone()
     datahist_oviedo_marker.SetLineWidth(0)
     datahist_oviedo_marker.SetMarkerColor(ROOT.kWhite)
     datahist_oviedo_marker.SetMarkerStyle(20)
     datahist_oviedo_marker.SetMarkerSize(markersize-0.13)




    ### make ratio histograms
    ratiohistlist = [h.Clone() for h in theoryhists]
    ratiohistlist_2 = [h.Clone() for h in theoryhists]

    ratiodatahist = datahist.Clone()
    ratiodatahist_marker = datahist_marker.Clone()
    ratiostatdatahist = statdatahist.Clone()

    allratiohists = ratiohistlist+[ratiodatahist]+[ratiostatdatahist]+[ratiodatahist_marker]
    
    # if we add oviedo to the same ratio plot
    if plotoviedo and not two_ratiopannels:
      ratiodatahist_oviedo = datahist_oviedo.Clone()
      ratiostatdatahist_oviedo = statdatahist_oviedo.Clone()
      ratiodatahist_oviedo_marker = datahist_oviedo_marker.Clone()
      ratiohistlist += [ratiodatahist_oviedo_marker]
      allratiohists += [ratiodatahist_oviedo]+[ratiostatdatahist_oviedo]+[ratiodatahist_oviedo_marker]

    # if we make a second ratio plot for oviedo
    allratiohists_2 = []
    if two_ratiopannels and not onlyoviedo and plotoviedo:
      ratiodatahist_oviedo = datahist_oviedo.Clone()
      ratiostatdatahist_oviedo = statdatahist_oviedo.Clone()
      ratiodatahist_oviedo_marker = datahist_oviedo_marker.Clone()
      allratiohists_2 = ratiohistlist_2 + [ratiodatahist_oviedo]+[ratiostatdatahist_oviedo]+[ratiodatahist_oviedo_marker]

    ratiosysthists = None
    ratiosysthists_2 = None
    if systhists is not None:
        ratiosysthists = []
        ratiosysthists_2 = []
        for hist in systhists:
            if hist is not None: 
                ratiosysthists.append(hist.Clone())
                if two_ratiopannels and not onlyoviedo and plotoviedo:ratiosysthists_2.append(hist.Clone()) 
            else: ratiosysthists.append(None)
        allratiohists += ratiosysthists
        allratiohists_2 += ratiosysthists_2

    # normalize both to same value
    if (not two_ratiopannels or onlyoviedo) and not plotoviedo:
      for hist in allratiohists:
        for j in range(0,hist.GetNbinsX()+2):
            scale = datahist.GetBinContent(j)                #change here to normalize to a different value(theoryhists[1])
            if scale<1e-12:
                hist.SetBinContent(j,0)
                hist.SetBinError(j,10)
            else:
                hist.SetBinContent(j,hist.GetBinContent(j)/scale)
                hist.SetBinError(j,hist.GetBinError(j)/scale)
    elif not two_ratiopannels or onlyoviedo:
      for hist in allratiohists:
        for j in range(0,hist.GetNbinsX()+2):
            scale = datahist_oviedo.GetBinContent(j)                #change here to normalize to a different value(theoryhists[1])
            if scale<1e-12:
                hist.SetBinContent(j,0)
                hist.SetBinError(j,10)
            else:
                hist.SetBinContent(j,hist.GetBinContent(j)/scale)
                hist.SetBinError(j,hist.GetBinError(j)/scale)

    else:
      # normalize to mva
      for hist in allratiohists:
        for j in range(0,hist.GetNbinsX()+2):
            scale = datahist.GetBinContent(j)                #change here to normalize to a different value
            if scale<1e-12:
                hist.SetBinContent(j,0)
                hist.SetBinError(j,10)
            else:
                hist.SetBinContent(j,hist.GetBinContent(j)/scale)
                hist.SetBinError(j,hist.GetBinError(j)/scale)

      # normalize to counting
      for hist in allratiohists_2:
        for j in range(0,hist.GetNbinsX()+2):
            scale = datahist_oviedo.GetBinContent(j)                #change here to normalize to a different value
            if scale<1e-12:
                hist.SetBinContent(j,0)
                hist.SetBinError(j,10)
            else:
                hist.SetBinContent(j,hist.GetBinContent(j)/scale)
                hist.SetBinError(j,hist.GetBinError(j)/scale)

    (ratiomin,ratiomax) = ht.getminmax(allratiohists, includebinerror=True)
    if ratiomin < 0 : ratiomin = 0.1
    print(ratiomin)
    print(ratiomax)
    ratiorange = (round(ratiomin, 1)-0.0999,round(ratiomax, 1)+0.09999)
    
    # special case when data histogram was empty (e.g. for only plotting MC)
    if datahist.Integral() < 1e-12:
        for hist in allratiohists: hist.Reset()
 
    ### make legend for upper plot and add all histograms
    legend = ROOT.TLegend(plegendbox[0],plegendbox[1],plegendbox[2],plegendbox[3])
    legend.SetNColumns(1)
    legend.SetFillStyle(0)
    legend.SetTextFont(10*legendfont+3)
    legend.SetBorderSize(0)

    if onlyoviedo:
      name = 'Data (Counting method) ' + chi2info_improved[1] + " " + chi2info_old[1] + " " #+ stats.chi2.pdf( , )'Data (Counting method) '
    else:
      name = 'Data (MVA-based method) ' + chi2info_improved[0] + " " + chi2info_old[0] + " " #+ 'Data (MVA-based method) improved '

    legend.AddEntry(datahist,name,"pe1")
    
    if plotoviedo:
     legend.AddEntry(datahist_oviedo,'Data (Counting method) ' + chi2info_improved[1] + " " + chi2info_old[1],"pe1")

    emptycopy = datahist.Clone()
    emptycopy.SetLineColor(ROOT.kWhite)
    legend.AddEntry(emptycopy,'aMC@NLO+PY8:',"l")
    for i,hist in enumerate(theoryhists):
        label = hist.GetTitle()
        if labellist is not None: label = labellist[i]
        legend.AddEntry(hist,'FxFx arXiv:1209.6215',"lpf")
        break
    if not systhists is None:
        systhists[1].SetLineWidth(2)
        systhists[1].SetLineColor(colorlist[1])
        legend.AddEntry(systhists[1],"FxFx arXiv:2108.07826","lpf") #Fchange to lpf and comment 2 above lines to have both as one entry in legend

    # if two data hists exist and tworatioplots is turned on, we define other pads
    if two_ratiopannels and not onlyoviedo and plotoviedo:
      print('this would be split')
      rfrac = 0.2
      cheight = int((1+rfrac)*cheight)
      

    ### make canvas and pads
    c1 = ROOT.TCanvas("c1","c1")
    c1.SetCanvasSize(cwidth,cheight)

    if two_ratiopannels and not onlyoviedo and plotoviedo:
      pad1 = ROOT.TPad("pad1","",0.,1.6*rfrac,1.,1.)
      pad1.SetTopMargin(p1topmargin)
      pad1.SetBottomMargin(p1bottommargin)
      pad1.SetLeftMargin(leftmargin)
      pad1.SetRightMargin(rightmargin)
      pad1.SetTicks(1,1)
      pad1.SetFrameLineWidth(2)
      #pad1.SetGrid()
      pad1.Draw()

      pad2 = ROOT.TPad("pad2","",0.,rfrac,1.,rfrac*1.6)
      pad2.SetTopMargin(p2topmargin)
      pad2.SetBottomMargin(p1bottommargin)
      pad2.SetLeftMargin(leftmargin)
      pad2.SetRightMargin(rightmargin)
      pad2.SetTicks(1,1)
      pad2.SetFrameLineWidth(2)
      #pad2.SetGrid()
      pad2.Draw()

      pad3 = ROOT.TPad("pad3","",0.,0.,1.,rfrac)
      pad3.SetTopMargin(p2topmargin)
      pad3.SetBottomMargin(p2bottommargin)
      pad3.SetLeftMargin(leftmargin)
      pad3.SetRightMargin(rightmargin)
      pad3.SetTicks(1,1)
      pad3.SetFrameLineWidth(2)
      #pad3.SetGrid()
      pad3.Draw()
    else:
      pad1 = ROOT.TPad("pad1","",0.,rfrac,1.,1.)
      pad1.SetTopMargin(p1topmargin)
      pad1.SetBottomMargin(p1bottommargin)
      pad1.SetLeftMargin(leftmargin)
      pad1.SetRightMargin(rightmargin)
      pad1.SetTicks(1,1)
      pad1.SetFrameLineWidth(2)
      #pad1.SetGrid()
      pad1.Draw()

      pad2 = ROOT.TPad("pad2","",0.,0.,1.,rfrac)
      pad2.SetTopMargin(p2topmargin)
      pad2.SetBottomMargin(p2bottommargin)
      pad2.SetLeftMargin(leftmargin)
      pad2.SetRightMargin(rightmargin)
      pad2.SetTicks(1,1)
      pad2.SetFrameLineWidth(2)
      #pad2.SetGrid()
      pad2.Draw()

    ### make upper part of the plot
    pad1.cd()

    # get x-limits (for later use)
    nbins = datahist.GetNbinsX()
    xlims = (datahist.GetBinLowEdge(1),
	     datahist.GetBinLowEdge(nbins)+datahist.GetBinWidth(nbins))
    # get and set y-limits
    datahists = [datahist]
    if not datahist_oviedo is None: datahists.append(datahist_oviedo)
    (totmin,totmax) = ht.getminmax(theoryhists+datahists)
    # in case of log scale
    if logy:
        pad1.SetLogy()
        if ylims is None: ylims = (totmin*yminlogfactor, totmax*ymaxlogfactor)
    # in case of lin scale
    else:
        if any(substring in figname for substring in ["HT","jetPtLeading","leptonPtSum","dR", "leptonMaxEta"]): ymaxlinfactor *= 1.1
        if onlyoviedo and ("leptonPtSum" in figname): ymaxlinfactor *= 1.1
        if ylims is None: ylims = (0.,totmax*ymaxlinfactor)
    if yminzero and ylims[0]<0: ylims = (0.,ylims[1])
    theoryhists[0].SetMaximum(ylims[1])
    theoryhists[0].SetMinimum(ylims[0])

    # X-axis layout
    xax = theoryhists[0].GetXaxis()
    xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelSize(0)
    # Y-axis layout
    yax = theoryhists[0].GetYaxis()
    yax.SetMaxDigits(3)
    yax.SetNdivisions(8,4,0,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    if yaxtitle is not None:
        yax.SetTitle(yaxtitle)
        yax.SetTitleFont(10*axtitlefont+3)
        yax.SetTitleSize(axtitlesize)
        yax.SetTitleOffset(ytitleoffset)

    # draw histograms
    theoryhists[0].Draw(drawoptions)
    if systhists is not None:
        for hist in systhists:
            if hist is not None: hist.Draw("same e2")
    for hist in theoryhists:
        hist.Draw("same "+drawoptions)
    ROOT.TGaxis.SetExponentOffset(-0.08, 0.00, "y") 

    #nbins = datahist.GetNbinsX()
    #center=[]
    #value=[]
    #totplus=[]
    #totmin=[]
    #statplus=[]
    #statmin=[]
    #for i in range(1,nbins+1):
    #    center.append(datahist.GetBinCenter(i))
    #    value.append(datahist.GetBinContent(i))
    #    totplus.append(datahist.GetBinError(i))
    #    statplus.append(statdatahist.GetBinError(i))

    #gme = ROOT.TGraphMultiErrors(nbins, center, value, 0, 0,0,0)
    #nbins, center, value, 0, 0, statplus, statplusns, center, value, 0, 0,)
    #gme.AddYError(nbins,totplus,totplus)
    #gme.Draw("pe e0 x0 same")

    if horizontal: datahist_horizontal.Draw("same z") 
    datahist.Draw("e0 x0 same")
    statdatahist.Draw("e1 x0 same")
    datahist_marker.Draw("e1 x0 same")
    if onlyoviedo:
     print("=====================================================================================================================================")
     datahist.SetMarkerStyle(24)
    
    if plotoviedo:
     datahist_oviedo.Draw("e0 x0 same")
     statdatahist_oviedo.Draw("e1 x0 same")
     datahist_oviedo_marker.Draw("e1 x0 same")
     datahist_oviedo.SetMarkerStyle(24)    


    if dolegend:
        legend.Draw("same")
    ROOT.gPad.RedrawAxis()

    # draw header
    pt.drawLumi(pad1, extratext=extracmstext, lumitext=lumitext, rfrac=rfrac, cms_in_grid=False)

    # draw extra info
    tinfo = ROOT.TLatex()
    tinfo.SetTextFont(10*infofont+3) 
    tinfo.SetTextSize(1.4*infosize)
    for i,info in enumerate(extrainfos):
        vspace = 0.07*(float(infosize)/20)
        print('drawing in region')
        tinfo.DrawLatexNDC(infoleft,infotop-(i+1)*vspace, info)

    ### make the lower part of the plot
    pad2.cd()
    xax = ratiohistlist[0].GetXaxis()
    xax.SetNdivisions(5,4,0,ROOT.kTRUE)
    xax.SetLabelSize(labelsize)
    xax.SetLabelFont(10*labelfont+3)
    # turn off axis label if we make 2 ratio plots
    title1 = '#splitline{Pred./}{Data}'
    yaxtitlesize = axtitlesize
    ratioytitleoffset = ytitleoffset

    if two_ratiopannels and not onlyoviedo and plotoviedo: 
      xax.SetLabelSize(0)
      title1 = '#splitline{Pred./}{MVA}'
      yaxtitlesize=20
      ratioytitleoffset+=0.5
     
     
    if xaxtitle is not None and not (two_ratiopannels and not onlyoviedo and plotoviedo):
        xax.SetTitle(xaxtitle)
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)
        xax.SetTitleOffset(xtitleoffset)
    # Y-axis layout
    yax = ratiohistlist[0].GetYaxis()
    if ratiorange==None: ratiorange = (0,1.999)
    yax.SetRangeUser(ratiorange[0],ratiorange[1])
    yax.SetMaxDigits(3)
    yax.SetNdivisions(405,ROOT.kTRUE)
    yax.SetLabelFont(10*labelfont+3)
    yax.SetLabelSize(labelsize)
    yax.SetTitle(title1)
    yax.SetTitleFont(10*axtitlefont+3)
    yax.SetTitleSize(yaxtitlesize)
    yax.SetTitleOffset(ratioytitleoffset)
    yax.CenterTitle(True)

    # draw objects
    ratiohistlist[0].Draw(drawoptions)
    if ratiosysthists is not None:
        for hist in ratiosysthists:
            if hist is not None: hist.Draw("same e2")
    for hist in ratiohistlist:
        hist.Draw("same "+drawoptions)
    ratiodatahist.Draw("e0 x0 same")
    ratiostatdatahist.Draw("e1 x0 same")
    ratiodatahist_marker.Draw("e1 x0 same")
    if plotoviedo and not two_ratiopannels:
     ratiodatahist_oviedo.Draw("e0 x0 same")
     ratiostatdatahist_oviedo.Draw("e1 x0 same")
     ratiodatahist_oviedo_marker.Draw("e1 x0 same")
    ROOT.gPad.RedrawAxis()

    # make and draw unit ratio line
    xmax = theoryhists[0].GetXaxis().GetBinUpEdge(theoryhists[0].GetNbinsX())
    xmin = theoryhists[0].GetXaxis().GetBinLowEdge(1)
    line1 = ROOT.TLine(xmin,1,xmax,1)
    line1.SetLineStyle(2)
    line1.Draw("same")

    # write per-bin uncertainty if requested
    # to be tested and continued...
    uncinfo = ROOT.TLatex()
    uncinfo.SetTextFont(10*infofont+3)
    uncinfo.SetTextSize(infosize)
    if writeuncs:
        for i in range(1, ratiodatahist.GetNbinsX()+1):
            error = ratiodatahist.GetBinError(i)
            xpos = ratiodatahist.GetBinCenter(i)
            errorstr = '{:.0f} %'.format(error*100)
            tinfo.DrawLatex(xpos, 1.5, errorstr)


    if two_ratiopannels and not onlyoviedo and plotoviedo:
      pad3.cd()
      xax = ratiohistlist_2[0].GetXaxis()
      xax.SetNdivisions(5,4,0,ROOT.kTRUE)
      xax.SetLabelSize(labelsize)
      xax.SetLabelFont(10*labelfont+3)
      if xaxtitle is not None:
        xax.SetTitle(xaxtitle)
        xax.SetTitleFont(10*axtitlefont+3)
        xax.SetTitleSize(axtitlesize)
        xax.SetTitleOffset(xtitleoffset)
      # Y-axis layout
      yax = ratiohistlist_2[0].GetYaxis()
      if ratiorange==None: ratiorange = (0,1.999)
      yax.SetRangeUser(ratiorange[0],ratiorange[1])
      yax.SetMaxDigits(3)
      yax.SetNdivisions(405,ROOT.kTRUE)
      yax.SetLabelFont(10*labelfont+3)
      yax.SetLabelSize(labelsize)
      yax.SetTitle('#splitline{Pred./}{Counting}')
      yax.SetTitleFont(10*axtitlefont+3)
      yax.SetTitleSize(yaxtitlesize)
      yax.SetTitleOffset(ratioytitleoffset)      
      # draw objects
      ratiohistlist_2[0].Draw(drawoptions)
      if ratiosysthists_2 is not None:
        for hist in ratiosysthists_2:
            if hist is not None: hist.Draw("same e2")
      for hist in ratiohistlist_2:
        hist.Draw("same "+drawoptions)
      ratiodatahist_oviedo.Draw("e0 x0 same")
      ratiostatdatahist_oviedo.Draw("e1 x0 same")
      ratiodatahist_oviedo_marker.Draw("e1 x0 same")
      ROOT.gPad.RedrawAxis()

      # make and draw unit ratio line
      xmax = theoryhists[0].GetXaxis().GetBinUpEdge(theoryhists[0].GetNbinsX())
      xmin = theoryhists[0].GetXaxis().GetBinLowEdge(1)
      line2 = ROOT.TLine(xmin,1,xmax,1)
      line2.SetLineStyle(2)
      line2.Draw("same")

      # write per-bin uncertainty if requested
      # to be tested and continued...
      uncinfo = ROOT.TLatex()
      uncinfo.SetTextFont(10*infofont+3)
      uncinfo.SetTextSize(infosize)
      if writeuncs:
          for i in range(1, ratiodatahist.GetNbinsX()+1):
            error = ratiodatahist.GetBinError(i)
            xpos = ratiodatahist.GetBinCenter(i)
            errorstr = '{:.0f} %'.format(error*100)
            tinfo.DrawLatex(xpos, 1.5, errorstr)

    c1.SaveAs(figname.replace('.png','')+'.png')
    c1.SaveAs(figname.replace('.png','')+'.pdf')
    c1.SaveAs(figname.replace('.png','')+'.eps')


def plotdifferential_cat(
    theoryhists,
    datahist,
    systhists=None,
    statdatahist=None,
    datahist_oviedo=None,
    statdatahist_oviedo=None,
    figname=None, title=None, xaxtitle=None, yaxtitle=None,
    dolegend=True, labellist=None,
    colorlist=None,
    logy=False, ymaxlinfactor=1.8, yminlogfactor=0.2, ymaxlogfactor=100,
    drawoptions='',
    lumitext='', extracmstext = '',
    ratiorange=None, ylims=None, yminzero=False,
    extrainfos=[], infosize=None, infoleft=None, infotop=None,
    chi2info_old=['',''],
    chi2info_improved=['',''],
    writeuncs=False,
    onlyoviedo=False):
    ### plot multiple overlaying histograms (e.g. for shape comparison)
    # note: the ratio plot will show ratios w.r.t. the first histogram in the list!
    # arguments:
    # - theoryhists, colorlist, labellist: lists of TH1, ROOT colors and labels respectively
    # - systhists: list of TH1 with systematic uncertainties on theoryhists
    # - datahist: TH1 with the measurement values
    # - statdatahist: TH1 with same bin contents as datahist but statistical-only errors
    # - figname: name of the figure to save (if None, do not save but return plot dictionary)
    # - title, xaxtitle, yaxtitle, figname: self-explanatory
    # - dolegend: boolean whether to make a legend (histogram title is used if no labellist)
    # - logy: boolean whether to make y-axis logarithmic
    # - ymaxlinfactor: factor by which to multiply maximum y value (for linear y-axis)
    # - yminlogfactor and ymaxlogfactor: same as above but for log scale
    # - drawoptions: string passed to TH1.Draw
    #   see https://root.cern/doc/master/classTHistPainter.html for a full list of options
    # - lumitext and extracmstext: luminosity value and extra text
    # - ratiorange: a tuple of (ylow,yhigh) for the ratio pad, default (0,2)
    # - ylims: a tuple of (ylow,yhigh) for the upper pad
    # - yminzero: whether to clip minimum y to zero.
    # - extrainfos is a list of strings with extra info to display
    # - infosize: font size of extra info
    # - infoleft: left border of extra info text (default leftmargin + 0.05)
    # - infotop: top border of extra info text (default 1 - topmargin - 0.1)

    #y = datahist.GetArray()
    #y.SetSize(datahist.GetNbinsX())
    #y = np.array(y)

    datahist = []
    dataerr = []
    datastaterr = []
    
    oldFxFx = []
    newFxFx = []
    newFxFxerr = []

    for i in range(1,datahist.GetNBinsX()+1):
     print("todo") 

    fig = plt.figure(figsize=(10, 8))
    main_ax_artists, sublot_ax_arists = y.plot_ratio(
      hist.Hist(theoryhists[0]),
      rp_ylabel=r"Pred./Data",
      rp_num_label="hist1",
      rp_denom_label="hist2",
      rp_uncert_draw_type="bar",  # line or bar
    )

    plt.savefig(figname)
