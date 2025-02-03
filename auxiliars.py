""" Auxiliar functions for plotting and histo handling """
from copy import deepcopy
import ROOT as r
import re

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)

# https://cms-analysis.docs.cern.ch/guidelines/plotting/colors/
blue = r.TColor.GetColor(63, 144, 218)
orange = r.TColor.GetColor(255, 169, 14)
red = r.TColor.GetColor(189, 31, 1)

red0 = r.TColor.GetColor(128, 19, 10)
red1 = r.TColor.GetColor(158, 23, 13)
red2 = r.TColor.GetColor(188, 23, 13)
red3 = r.TColor.GetColor(218, 23, 13)
red4 = r.TColor.GetColor(247, 23, 13)
red5 = r.TColor.GetColor(247, 87, 74)


gray = r.TColor.GetColor(148, 164, 162)
purple = r.TColor.GetColor(131, 45, 182)
brown = r.TColor.GetColor(169, 107, 89)
dark_orange = r.TColor.GetColor(231, 99, 0)
tan = r.TColor.GetColor(185, 172, 112)
dark_gray = r.TColor.GetColor(113, 117, 129)
light_blue = r.TColor.GetColor(146, 218, 221)



def color_msg(msg, color = "none", indentlevel=0):
    """ Prints a message with ANSI coding so it can be printout with colors """
    codes = {
        "none" : "0m",
        "green" : "1;32m",
        "red" : "1;31m",
        "blue" : "1;34m",
        "yellow" : "1;33m"
    }

    if indentlevel == 0: indentSymbol=">> "
    if indentlevel == 1: indentSymbol="+ "
    if indentlevel >= 2: indentSymbol="* "

    indent = indentlevel*" " + indentSymbol
    print("\033[%s%s%s \033[0m"%(codes[color], indent, msg))
    return

def integrate(histograms):
    """ Reads a dictionary and integrates histograms according to keys """
    summed = {}
    for proc, histos in histograms.items():
        # Grab the first one
        h0 = deepcopy( histos[0].Clone( "{0}_SUM".format( proc )) )

        # Go summing up the rest
        for h in histos[1:]:
            h0.Add( h )

        summed[proc] = h0
    return summed

def get_histograms( inputFile, channels, shapedir, year = "all", divideByBinWidth=False ):
    """ Grab all histograms from fitDiagnostics and split them by channels """
    rfile = r.TFile.Open( inputFile )

    # Get all the interesting keys from the file. This essentially fetches years and channels
    #channels = filter( lambda key: shapedir in key.GetName() and key.GetName() != shapedir, rfile.GetListOfKeys() ) # Exclude the prefit/postfit directories for the individua          = l processes

    # Start building histograms. Format will be:
    # { 
    #  "proc" : [channel0, channel1, channel2, ...]
    # }

    shapes = {}
    # Get all the histograms

    for key in channels:
        channel = rfile.Get( "{0}_{1}".format( key, shapedir ) )
        channel.cd()
        for proc_key in channel.GetListOfKeys():
            # These are handled differently because we have to make sure we use the ones produced by combine,
            # since those are the ones that have been propagated using the covariance matrix.


            #if proc_key.GetName() in ["TotalProcs"]:
            #    h = channel.Get( "TotalProcs" )

                #print( channel.GetName(), "Bin content: {0} +/- {1}".format(h.GetBinContent(1), h.GetBinError(1)))

            if proc_key.GetName() in ["TotalBkg", "TotalSig"]: continue 
            if proc_key.GetName() not in shapes:
                h = channel.Get( proc_key.GetName() ).Clone()
                h.SetDirectory(0)
                # now divide all process bins by their width
                if divideByBinWidth:
                    for i in range(1, 1+h.GetNbinsX()):
                        binwidth = h.GetBinWidth(i)
                        binheight = h.GetBinContent(i)

                        h.SetBinContent(i, h.GetBinContent(i)/binwidth)
                        h.SetBinError(i, h.GetBinError(i)/binwidth)

                shapes[ proc_key.GetName() ] = [ h ]
            else:
                h = channel.Get( proc_key.GetName() ).Clone()
                h.SetDirectory(0)
                # now divide all process bins by their width
                if divideByBinWidth:
                    for i in range(1, 1+h.GetNbinsX()):
                        binwidth = h.GetBinWidth(i)
                        binheight = h.GetBinContent(i)


                        h.SetBinContent(i, h.GetBinContent(i)/binwidth)
                        h.SetBinError(i, h.GetBinError(i)/binwidth)
                shapes[ proc_key.GetName() ].append( h )
            
            #if proc_key.GetName() == "data_obs":
            #    print(  " + ", channel.Get( proc_key.GetName() ).Integral() )


    # Now integrate all histograms into one
    summed = integrate( shapes )

    # Now use the prefit/postfit directories to fetch the total and data histograms
    shapes_summedByCombine = rfile.Get( shapedir )
    shapes_summedByCombine.cd()

    # Data comes in histogram, we want to convert it into a TGraph
    data_h = summed["data_obs"] #deepcopy( shapes_summedByCombine.Get( "data_obs" ).Clone("data_obs_COMBINE") )
    data_gr = r.TGraphErrors( data_h.GetNbinsX() )
    data_gr.SetName(" data_obs_COMBINE_gr" )
    for ibin in range(1, 1+data_h.GetNbinsX() ):
        data_gr.SetPoint(ibin-1, data_h.GetBinCenter(ibin), data_h.GetBinContent(ibin) )
        data_gr.SetPointError(ibin-1, 0, data_h.GetBinError(ibin) )
    
    
    summed["data_obs"]  = data_gr

    # extra lines to always get the prefit shapes
    #print("looking for prefit: {}".format(len(channels)))
    if len(channels) ==1: 
        prefit_channel = rfile.Get( "{}_prefit".format( key) )
    else: 
        summed["TotalProcs"] = deepcopy( shapes_summedByCombine.Get( "TotalProcs" ).Clone("totalProcs_COMBINE") )
        if divideByBinWidth:
            for i in range(1, 1+h.GetNbinsX()):
                binwidth = summed["TotalProcs"].GetBinWidth(i)
                binheight = summed["TotalProcs"].GetBinContent(i)


                summed["TotalProcs"].SetBinContent(i, summed["TotalProcs"].GetBinContent(i)/binwidth)
                summed["TotalProcs"].SetBinError(i, summed["TotalProcs"].GetBinError(i)/binwidth)
        
        prefit_channel = rfile.Get( "prefit" ) #clearly to be tuned

    prefit_channel.cd()
    for proc_key in prefit_channel.GetListOfKeys():
       if proc_key.GetName() in ["TotalProcs"]:
           h_prefit = prefit_channel.Get( "TotalProcs" )
           h_prefit.SetDirectory(0)
           if divideByBinWidth:
             for i in range(1, 1+h_prefit.GetNbinsX()):
               binwidth = h_prefit.GetBinWidth(i)
               binheight = h_prefit.GetBinContent(i)

               h_prefit.SetBinContent(i, h_prefit.GetBinContent(i)/binwidth)
               h_prefit.SetBinError(i, h_prefit.GetBinError(i)/binwidth)


    return shapes, summed, h_prefit

def doSpam(text,x1,y1,x2,y2,align=12,fill=False,textSize=0.033,_noDelete={}):
  cmsprel = r.TPaveText(x1,y1,x2,y2,"NDC")
  cmsprel.SetTextSize(textSize)
  cmsprel.SetFillColor(0)
  cmsprel.SetFillStyle(1001 if fill else 0)
  cmsprel.SetLineStyle(2)
  cmsprel.SetLineColor(0)
  cmsprel.SetLineWidth(0)
  cmsprel.SetTextAlign(align)
  cmsprel.SetTextFont(43)
  cmsprel.AddText(text)
  cmsprel.Draw("same")
  _noDelete[text] = cmsprel; 
  return cmsprel


def new_canvas( name ):
    """ Creates a template canvas """
    # --------------- Prepare the basic canvas
    c = r.TCanvas(name, "",  612, 600)
    topSpamSize     = 1.1
    c.SetTopMargin(c.GetTopMargin() * topSpamSize)
    c.Divide(1,2)

    # --- First pad
    p1 = c.GetPad(1)
    p1.SetPad(0, 0.25, 1, 1)
    p1.SetTopMargin(0.055)
    p1.SetBottomMargin(0.025)
    p1.SetLeftMargin(0.16)
    p1.SetRightMargin(0.05)#0.03

    # --- Second pad
    p2 = c.GetPad(2)
    p2.SetPad(0, 0, 1, 0.25)
    p2.SetTopMargin(0.06)
    p2.SetBottomMargin(0.42)
    p2.SetLeftMargin(0.16)
    p2.SetRightMargin(0.05)
    return c, p1, p2

def new_postfitcanvas( name ):
    """ Creates a template canvas """
    # --------------- Prepare the basic canvas
    c = r.TCanvas(name, "",  612, 700)
    topSpamSize     = 1.1
    c.SetTopMargin(c.GetTopMargin() * topSpamSize)
    c.Divide(1,2)

    # --- First pad
    p1 = c.GetPad(1)
    p1.SetPad(0, 0.35, 1, 1)
    p1.SetTopMargin(0.055)
    p1.SetBottomMargin(0.025)
    p1.SetLeftMargin(0.16)
    p1.SetRightMargin(0.05)#0.03

    # --- Second pad
    p2 = c.GetPad(2)
    p2.SetPad(0, 0, 1, 0.35)
    p2.SetTopMargin(0.06)
    p2.SetBottomMargin(0.42)
    p2.SetLeftMargin(0.16)
    p2.SetRightMargin(0.05)
    return c, p1, p2


def draw_stack( hstack, data, cfgplot, binwidthbool ):
    """ Modify parameters of the hstack """
    hstack.Draw("hist")
    if cfgplot.logy:
        mini = 5
    else:
        mini = 0
        
    if cfgplot.force_y_max == None:
        hstack.GetYaxis().SetRangeUser( 0, max( hstack.GetMaximum(), data.GetMaximum() )*cfgplot.ScaleUpperY )
        hstack.SetMaximum( max( hstack.GetMaximum(), data.GetMaximum() )*cfgplot.ScaleUpperY )
        hstack.SetMinimum( mini )

    else:
        hstack.GetYaxis().SetRangeUser( 0, cfgplot.force_y_max )
        hstack.SetMaximum( cfgplot.force_y_max )
        hstack.SetMinimum( mini )


    if cfgplot.rangex != None:
        hstack.GetXaxis().SetRangeUser( cfgplot.rangex[0], cfgplot.rangex[1] )
    
        
    hstack.GetXaxis().SetTitleFont(43)
    hstack.GetYaxis().SetTitleFont(43)
    hstack.GetXaxis().SetLabelFont(43)
    hstack.GetYaxis().SetLabelFont(43)
    
    
    hstack.GetXaxis().SetLabelSize(0)
    hstack.GetYaxis().SetLabelSize(24)   
    hstack.GetXaxis().SetTitleSize(26)
    hstack.GetYaxis().SetTitleSize(26)

    hstack.GetYaxis().SetTitleOffset(1.8)

    if binwidthbool: hstack.GetYaxis().SetTitle( cfgplot.titleY_binwidth ) 
    else: hstack.GetYaxis().SetTitle( cfgplot.titleY )
 

    hstack.GetYaxis().SetMaxDigits(4)

def draw_data( data ):
    """ Draws the data TGraph """
    data.Draw("pe same")
    data.SetLineColor(1)
    data.SetFillColor(0)
    data.SetMarkerColor(1)
    data.SetMarkerStyle(20)
    
def draw_unc( total ):
    """ Draws the uncertainty band """
    total.Draw("e2 same")
    total.SetFillStyle(3344)
    total.SetFillColor(r.kBlack)#kGray+2)
    total.SetMarkerStyle(0)
    total.SetMarkerColor(920)
    total.SetLineWidth(0)

def draw_ratio( ratio, total, data, cfgplot, prefit,shapedir ):
    """ Draws the ratio distributions """
    htotalNoErr = deepcopy(total.Clone("ratiounc"))
    htotalErr = deepcopy(total.Clone("ratiouncErr"))
    h_prefit = deepcopy(prefit.Clone("prefit"))
    h_prefitNoErr = deepcopy(prefit.Clone("prefitNoErr"))

    for ibin in range(1, htotalNoErr.GetNbinsX()+1):
        htotalNoErr.SetBinError(ibin, 0)
        h_prefitNoErr.SetBinError(ibin, 0)
        ratio.SetPoint(ibin-1, ratio.GetX()[ibin-1], data.GetY()[ibin-1] / htotalNoErr.GetBinContent(ibin) ) 
        ratio.SetPointError(ibin-1, 0, data.GetErrorY(ibin-1) / htotalNoErr.GetBinContent(ibin) ) 
        #h_prefit.SetBinError(ibin, 0)
        h_prefit.SetBinContent(ibin, prefit.GetBinContent(ibin)/htotalNoErr.GetBinContent(ibin) )
        h_prefit.SetBinError(ibin, prefit.GetBinError(ibin)/htotalNoErr.GetBinContent(ibin) )
    h_prefit.SetBinContent(0, 1 )
    htotalErr.Divide(htotalNoErr)

    mini = cfgplot.ymin_ratio
    maxi = cfgplot.ymax_ratio

    if shapedir == 'postfit': maxi += 0.25

    htotalErr.GetYaxis().SetRangeUser( mini, maxi )
    h_prefit.GetYaxis().SetRangeUser( mini, maxi )


    if cfgplot.rangex != None:
        htotalErr.GetXaxis().SetRangeUser( cfgplot.rangex[0], cfgplot.rangex[1] )
        h_prefit.GetXaxis().SetRangeUser( cfgplot.rangex[0], cfgplot.rangex[1] )


    if cfgplot.binlabels != []:
        print(cfgplot.binlabels, htotalErr.GetNbinsX())
        for ibin in range(1, 1+htotalErr.GetNbinsX() ):
            htotalErr.GetXaxis().SetBinLabel( ibin, cfgplot.binlabels[ibin-1] )
            h_prefit.GetXaxis().SetBinLabel( ibin, cfgplot.binlabels[ibin-1] )

    
    htotalErr.GetYaxis().SetTitleFont(43)
    htotalErr.GetXaxis().SetTitleFont(43)
    htotalErr.GetXaxis().SetLabelFont(43)
    htotalErr.GetYaxis().SetLabelFont(43)
    
    htotalErr.SetLineWidth(1)
    htotalErr.SetLineColor(1)
    
    htotalErr.GetXaxis().SetLabelSize(24)
    htotalErr.GetYaxis().SetLabelSize(24)   
    htotalErr.GetXaxis().SetTitleSize(24)
    htotalErr.GetYaxis().SetTitleSize(26)

    htotalErr.GetYaxis().SetTitleOffset(1.8)
    htotalErr.GetXaxis().SetTitleOffset(4.3)
    htotalErr.GetXaxis().SetLabelOffset(0.01)

    

    htotalErr.SetTitle("")
    htotalErr.GetYaxis().SetTitle("Data / Pred.     ")
    htotalErr.GetXaxis().SetTitle(cfgplot.titleX)
    #htotalErr.GetXaxis().LabelsOption("v")
    
    htotalErr.GetYaxis().SetNdivisions(503)
    htotalErr.GetXaxis().SetNdivisions(410)
    htotalErr.GetYaxis().CenterTitle(True)

    h_prefit.GetYaxis().SetTitleFont(43)
    h_prefit.GetXaxis().SetTitleFont(43)
    h_prefit.GetXaxis().SetLabelFont(43)
    h_prefit.GetYaxis().SetLabelFont(43)

    h_prefit.SetLineWidth(1)
    h_prefit.SetLineColor(1)

    h_prefit.GetXaxis().SetLabelSize(24)
    h_prefit.GetYaxis().SetLabelSize(24)
    h_prefit.GetXaxis().SetTitleSize(24)
    h_prefit.GetYaxis().SetTitleSize(26)

    h_prefit.GetYaxis().SetTitleOffset(1.8)
    h_prefit.GetXaxis().SetTitleOffset(4.3)
    h_prefit.GetXaxis().SetLabelOffset(0.01)



    h_prefit.SetTitle("")
    h_prefit.GetYaxis().SetTitle("Data / Pred.     ")
    h_prefit.GetXaxis().SetTitle(cfgplot.titleX)
    #htotalErr.GetXaxis().LabelsOption("v")

    h_prefit.GetYaxis().SetNdivisions(503)
    h_prefit.GetXaxis().SetNdivisions(410)
    h_prefit.GetYaxis().CenterTitle(True)

    h_prefit.SetLineColor(r.kRed)
    h_prefit.SetLineWidth(2)

    return htotalErr, ratio, h_prefit 

def get_channels( combinedCard, region, match_ch ):
    """ Tries to get the SR channels """
    
    # Open the combined card
    f = open( combinedCard )

    channels = []
    lines = f.readlines()
    pattern = re.compile(match_ch)

    for line in lines:
        
        #if region == "3l" and "cr" in line: continue # This is an exception for oviedo's cards
        if "shapes" in line:
            fields = list(filter( lambda x: x != "", line.split(" ")) )
            
            channel = fields[2]
            card = fields[3]
      
            #print(card)
            #print(region)      
            if region in card:
                print("match!")
                channels.append( channel )
            
        #match_response = pattern.match( line )
        #if match_response:
        #    print( match_response.groups())
        #    channel, card = match_response.groups()
        #    if region in card: 
        #        channels.append( channel )
    return channels

def get_signals( combinedCard, analysis, region = "signalregion" ):
    """ Tries to get the SR channels """
    
    # Open the combined card
    f = open( combinedCard )

    signals = []
    for l in f.readlines():
        
        if analysis == "oviedo":
            if "process" in l:
                p = l.split(" ")
                
                if ("cr" not in region) or (region == "cr_nonprompt"):
                    for item in p:
                        if "TTW_" in item and "inc" not in item: # and "ooa" not in item:
                            signals.append(item)
                else:
                    signals.append( "TTW_inclusive" )
        else:
            if "process" in l:
                p = l.split( " " )
                for item in p:
                    if "TTW" in item: 
                        signals.append(item)
        #match_response = pattern.match( line )
        #if match_response:
        #    print( match_response.groups())
        #    channel, card = match_response.groups()
        #    if region in card: 
        #        channels.append( channel )
    
    return list( set(signals) )
