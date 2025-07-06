""" 
Script to make postfit plots. Thanks to @mobeso for preparing the basic skeleton :-).
"""
import os, sys, re
from array import array
import argparse
from copy import deepcopy
import ROOT as r
from collections import OrderedDict
#import cmsstyle as CMS
import auxiliars as aux
import plot_configs as cfgs

def add_parsing_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outname', '-o', dest = "outname", default = "/user/dmarckx/public_html/postfitplots_test/", help = "plots")
    parser.add_argument('--year', '-y', dest = "year", default = "all", help = "To select the luminosity value.")
    parser.add_argument('--preliminary', dest = "preliminary", default = False, action = "store_true", help = "To select the label.")
    parser.add_argument('--analysis', dest = "analysis", default = "oviedo", help = "To select analysis to  take configs.")
    parser.add_argument('--split_signal', dest = "split_signal", default = False, action = "store_true", help = "To select the signal categories.")

    return parser.parse_args()



if __name__ == "__main__":
    
    lumis = {
        "all" : 138,
        '2017':41.5, 
        '2018':59.7,
        '2016pre':19.5, 
        '2016post':16.8
    }
    
    # 1. First step, grab all histograms from input cards
    opts = add_parsing_options()
    
    outname = opts.outname
    year = opts.year 
    prel = opts.preliminary
    analysis = opts.analysis



    groups_per_region = OrderedDict()
    
    # import configs from each analysis
    if analysis == "oviedo":
        inputFolder = "counting/"

        # Groupings 
        groups_per_region["Other"]        = { "processes" : ["tHq", "TTWW",  "ttVV", "tHW", "Rares", "VVV", "tZq"], "color" : aux.purple  }
        groups_per_region["ttX"]          = { "processes" : ["ttH", "TTZ"], "color" : aux.blue, "special_name" : "t#bar{t}X" }
        groups_per_region["Conversions"]        = { "processes" : ["Convs"], "color" : aux.orange }
        groups_per_region["Diboson"]      = { "processes" : ["WZ", "ZZ"], "color" : aux.dark_orange}
        groups_per_region["Charge MisID"]        = { "processes" : ["data_flips"], "color": aux.dark_gray }
        groups_per_region["Nonprompt"]    = { "processes" : ["data_fakes"], "color": aux.gray}  
     
        # Plot labeling   
        region_labels = {
            #"cr_3l" : { "binname" : "cr_3l", "label" : ["CR 3L", "(Tight)"] },
            #"cr_4l" : { "binname" : "cr_4l", "label" : ["CR 4L", "(Tight)"] },
            #"2lss" : { "binname" : "2lss", "label" : ["SR 2L", "(Tight)"] },
            "3l" : { "binname" : "3l", "label" : ["SR 3L", "(Tight)"] },
            #"2lss_plus" : { "binname" : "positive", "label" : ["SR 2L+", "(Tight)"] },
            #"2lss_minus" : { "binname" : "negative", "label" : ["SR 2L-", "(Tight)"] },
            #"cr_nonprompt" : { "binname" : "2lss", "label" : ["VR NP", "(Tight)"] },
            #"asymmetry" : { "binname" : "asymmetry", "label" : ["(Tight)",""] }
        }
        
        match_ch = r'shapes \*\s+ch(\d+)\s+([^\s]+)'
        
    elif analysis == "ghent":
        
        inputFolder = "bdt/"

        # Groupings 
        groups_per_region["Other"]        = { "processes" : ["TTX", "Multiboson", "TX"], "color" : aux.purple  }
        groups_per_region["ttX"]          = { "processes" : ["TTH", "TTZ"], "color" : aux.blue, "special_name" : "t#bar{t}X" }
        groups_per_region["Conversions"]        = { "processes" : ["TTG","ZG"], "color" : aux.orange } #ZG
        groups_per_region["Diboson"]      = { "processes" : ["WZ","ZZ"], "color" : aux.dark_orange} #ZZ
        groups_per_region["Charge MisID"]        = { "processes" : ["Chargeflips"], "color": aux.dark_gray }
        groups_per_region["Nonprompt"]    = { "processes" : ["NonpromptE", "NonpromptMu"], "color": aux.gray}  
        #groups_per_region["Zbs"]        = { "processes" : ["ZZ","ZG"], "color": aux.dark_gray }
     
        # Plot labeling   
        region_labels = {
            #"sigreg_withcut_onHT"  : { "binname" : "sigreg", "label" : "SR 2L (Loose)" },
            #"sigreg_withcut" : { "binname" : "sigreg", "label" : "SR 2L (Loose)" },
            "signalregion" : { "binname" : "signalregion", "label" : ["#scale[1.]{SR 2L}", "#scale[0.8]{(Loose)}"] },
            "sigreg" : { "binname" : "signalregion", "label" : ["#scale[1.]{SR 2L}", "#scale[0.8]{(Loose)}"] },
            "cfjetscontrolregion" : { "binname" : "cfjets", "label" : ["#scale[1.]{CR ChargeMisID}", "#scale[0.8]{(Loose)}"] },
            #"cfcontrolregion" : { "binname" : "cf", "label" : ["#scale[1.]{CR CF}", "#scale[0.8]{(Loose)}"] },
            #"npctr_incl": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP}", "#scale[0.8]{(Loose)}"] },
            #"npctr_me": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP me}", "#scale[0.8]{(Loose)}"] },
            #"npctr_em": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP em}", "#scale[0.8]{(Loose)}"] },
            #"npctr_ee": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP ee}", "#scale[0.8]{(Loose)}"] },
            #"npctr_mm": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP mm}", "#scale[0.8]{(Loose)}"] },
            #"npctr_2018": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP 18}", "#scale[0.8]{(Loose)}"] },
            #"npctr_2017": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP 17}", "#scale[0.8]{(Loose)}"] },
            #"npctr_2016pre": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP pre}", "#scale[0.8]{(Loose)}"] },
            #"npctr_2016post": { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP post}", "#scale[0.8]{(Loose)}"] },            
            "npcontrolregion" : { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP}", "#scale[0.8]{(Loose)}"] },
            "trileptoncontrolregion" : { "binname" : "trileptoncontrolregion", "label" : ["#scale[1.]{CR 3L}", "#scale[0.8]{(Loose)}"] },
            #"fourleptoncontrolregion" : { "binname" : "fourleptoncontrolregion", "label" : ["#scale[1.]{CR 4L}", "#scale[0.8]{(Loose)}"] },
        }
        match_ch = r'shapes \*\s+ch(\d+)\s+([^\s]+)'
        
    else:
        aux.color_msg("Analysis {0} not valid.".format( analysis ) )
        sys.exit(0)
        
        
        
    aux.color_msg("Producing postfit plots from {0}".format( inputFolder ), color = "green", indentlevel = 0)

    keyword = "bdt" if analysis == "ghent" else "counting"
    for reg in region_labels.keys():
        if "201" in reg: year = reg.split("_")[-1]
        #print(reg)
        # Get the list of variables to be plot 
        variables = cfgs.plots[analysis][ reg ]
        #print(variables)
        for variableName, variable in variables.items():
            #print(variableName)
            #if not "_eventBDT" in variableName: continue

            # flag to see if we need to divide this var by width
            dividethisvar = cfgs.plots['binwidth'] and variableName in cfgs.plots[analysis]['needwidth']
            print(cfgs.plots['binwidth'])
            print(cfgs.plots[analysis]['needwidth'])
            if dividethisvar:
              print("dividing by binwidth")

            # Get the plot configs
            cfgplot = deepcopy( variable )
            cfgplot.modify( "{0}_{1}".format( reg, analysis ) )
            if "plus" in reg: 
                cfgplot.force_y_max *= 0.7
            elif "minus" in reg:
                cfgplot.force_y_max *= 0.7
            elif any(x in reg for x in ["ee","em","me","mm"]):
                cfgplot.force_y_max *= 0.8
            elif any(x in reg for x in ["pre","post"]):
                cfgplot.force_y_max *= 0.65
            elif any(x in reg for x in ["17","18"]):
                cfgplot.force_y_max *= 0.95

                
            if analysis == "oviedo":
                
                """ 
                # OLD
                if reg in ["cr_3l", "cr_4l"]:    
                    inputFile = os.path.join( inputFolder, "2lss", "njets", "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, "2lss", "njets", "combined_njets_2lss.dat" ) 
                elif reg in  ["2lss_plus", "2lss_minus"]:
                    inputFile = os.path.join( inputFolder, reg, variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, reg, variableName, "combined_counting_{0}_{1}.dat".format( reg, variableName )) 
                elif reg in ["3l"]:
                    inputFile = os.path.join( inputFolder, "3l", variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, "3l", variableName, "combined_{0}_3l.dat".format( variableName )) 
                """

                reg_input = region_labels[reg]["binname"]
                var_input = variableName
                if "cr_3l" in variableName:
                    var_input = variableName.replace("_","")
                    reg_input = region_labels[reg]["binname"].replace("_","")

                if reg in ["2lss_plus", "2lss_minus"]:
                    reg_input = reg
                 
                inputFile = os.path.join( inputFolder, reg_input, var_input, "ttW_OUT.root" )
                combinedCard = os.path.join( inputFolder, reg_input, var_input, "combined_counting_{0}_{1}.dat".format( reg_input, var_input ) )
                if "cr_nonprompt" in reg:
                    #inputFile = os.path.join( inputFolder, "cr_nonprompt", variableName, "ttW_OUT.root" )
                    #combinedCard = os.path.join( inputFolder, "cr_nonprompt", variableName, "combined_{0}_2lss.dat".format( variableName )) 
                    inputFile = os.path.join( inputFolder, "cr_nonprompt", variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, "cr_nonprompt", variableName, "combined_counting_cr_nonprompt_{0}.dat".format( variableName ) )
                #    var_input = variableName.replace("_","")
                #    reg_input = region_labels[reg]["binname"].replace("_","")
                print(inputFile, combinedCard)
                
                if opts.split_signal and reg == "asymmetry":
                    groups_per_region["ttW_ooa"] = { 
                        "processes" : ["TTW_ooa"],
                        "color" : aux.red0, "special_name" : "t#bar{t}W o.o.a." 
                    }
                    groups_per_region["ttW_asymmetry_negative"] = {
                        "processes" : ["TTW_asymmetry_negative"],
                        "color" : aux.red2, "special_name" : "t#bar{t}W #Deltay^{l}<0"
                    }
                    groups_per_region["ttW_asymmetry_positive"] = {
                        "processes" : ["TTW_asymmetry_positive"],
                        "color" : aux.red4, "special_name" : "t#bar{t}W #Deltay^{l}>0"
                    }
                else:
                    groups_per_region["ttW"] = {
                        "processes" : aux.get_signals( combinedCard, analysis, reg),
                        "color" : aux.red, "special_name" : "t#bar{t}W"
                    }




                #print(groups_per_region["ttW"])            
            
            elif analysis == "ghent":
               
                if not (opts.split_signal and reg in ["signalregion","sigreg"] ):
                    inputFile = os.path.join( inputFolder, reg, variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, reg, variableName, "combined_{0}_{1}_{2}.dat".format( keyword, reg, variableName )) 
                    groups_per_region["ttW"] = { 
                        "processes" : aux.get_signals( combinedCard, analysis, reg ), 
                        "color" : aux.red, "special_name" : "t#bar{t}W" 
                    }
                    print(aux.get_signals( combinedCard, analysis, reg ))
                else:
                    colors = [aux.red0, aux.red1, aux.red2, aux.red3, aux.red4, aux.red5]
                    name = ""
                    processes = [x for x in aux.get_signals( combinedCard, analysis, reg ) if "eventBDT" in x]
                    name = processes[0][:3]+'{}'+processes[0][4:]
                    print(name)
                    for i in range(len(processes), -1, -1):
                        print(i)
                        groups_per_region["ttWbin{}".format(i)] = {
                            "processes" : [name.format(i)],
                            "color" : colors[i], "special_name" : ("t#bar{t}W bin "+str(i)).replace("bin 0","o.o.a.")
                        }



            if not os.path.isfile( inputFile ):
                aux.color_msg("Skipping {0} in {1} because {2} does not exist.".format( variableName, reg, inputFile ), color = "yellow", indentlevel = 1)
                continue

            channels = aux.get_channels( combinedCard, region_labels[reg]["binname"], match_ch ) 
            #print(combinedCard, region_labels[reg]["binname"], match_ch)
            if analysis == "ghent":
                channels = [ channels[0] ]
                if reg == "sigreg":
                  channels = ['ch1']
                elif reg == "signalregion" and "njets" in variableName:
                  channels = ['ch1']
                elif reg == "signalregion" and "eventBDT" in variableName:
                  channels = ['ch1']
                elif reg == "signalregion" and (variableName in ["HT","lt","jet2_pt"]):
                  channels = ['ch2']
                elif reg == "signalregion" and (variableName in ["jet1_pt","lep1_pt","lep2_pt"]):
                  channels = ['ch1']



                print("channels:")
                print(channels) 

            for shapedir in [ "prefit", "postfit" ]:
                entries_legend = []
                entries_ratiolegend = []

                aux.color_msg( "Making plots for {0}: {1}".format( shapedir, inputFile ), color = "green" )

                # Get histograms from the cards
                shapes, summed, h_prefit = aux.get_histograms( 
                    inputFile = inputFile, 
                    shapedir = shapedir, 
                    year = year,
                    channels = channels,
                    divideByBinWidth=dividethisvar
                )

                _, summed_prefit, _ = aux.get_histograms(
                    inputFile = inputFile,
                    shapedir = "prefit",
                    year = year,
                    channels = channels,
                    divideByBinWidth=dividethisvar
                )

                h_prefit = summed_prefit["TotalProcs"]



                # if divide by width: check how you have to rescale the plot based on the highest value
                if dividethisvar and shapedir == "prefit":
                  print("rescaling parameter force_y_max")
                  _, summed_width,_ = aux.get_histograms(          
                    inputFile = inputFile,
                    shapedir = shapedir,
                    year = year,
                    channels = channels,
                    divideByBinWidth=False
                  )
                  data_nw  = summed["data_obs"]
                  data_w  = summed_width["data_obs"]
                  maxi = [0,0]
                  for i in range(1, 1+h_prefit.GetNbinsX()):
                      binwidth = h_prefit.GetBinWidth(i)
                      binheight = h_prefit.GetBinContent(i)

                      if binheight/binwidth > maxi[0]: maxi = [binheight/binwidth, cfgplot.force_y_max/binwidth]
                  cfgplot.force_y_max = maxi[1]

                if shapedir == "postfit" and reg in ["asymmetry","3l"]: c, p1, p2 = aux.new_postfitcanvas( "canvas_{0}".format( shapedir ) )
                elif shapedir == "postfit": c, p1, p2 = aux.new_postfitcanvas( "canvas_{0}".format( shapedir ) )
                else: c, p1, p2 = aux.new_canvas( "canvas_{0}".format( shapedir ) )
                
                pad1W = p1.GetWw()*p1.GetAbsWNDC()
                pad2W = p2.GetWw()*p2.GetAbsWNDC()
                pad1H = p1.GetWh()*p1.GetAbsHNDC()
                pad2H = p2.GetWh()*p2.GetAbsHNDC()

                # Now we have to group them further for the plot
                hstack = r.THStack()
                groups = deepcopy( groups_per_region )
                p1.cd()


                for group, group_info in groups.items():
                    # Get a subset dictionary with th          = e processes and sum them
                    aux.color_msg( "Process {0}".format( group ), color = "none", indentlevel = 1 )

                    sub_dict = { group : [ summed[proc] for proc in group_info["processes"] if proc in summed ] }

                    if sub_dict[group] == []: 
                        aux.color_msg( "Skipping process {0} because it has 0 entries".format( group ), color = "yellow", indentlevel = 2 )
                        continue
                    
                    summed_group = aux.integrate( sub_dict )

                    # apply some very basic cosmetics
                    #summed_group[group].SetDirectory( 0 )
                    summed_group[group].SetFillStyle( 1001 )
                    
                    summed_group[group].SetFillColor( group_info["color"] )
                    summed_group[group].SetMarkerSize(0)
                    summed_group[group].SetLineColor(1)
                    summed_group[group].GetXaxis().SetLabelSize(0)
                    summed_group[group].SetLineWidth(0)

                    if "eventBDT" == variableName: ndivs = -504
                    if "BDT" in variableName: ndivs = -1*(500 + int(h_prefit.GetNbinsX()/5))
                    elif reg == "asymmetry": ndivs = -1*(400 + int(h_prefit.GetNbinsX()/4))
                    elif reg == 'cfjetscontrolregion' and variableName=="lep1_pt":
                      ndivs = -6
                    elif reg == 'signalregion' and variableName=="lep1_pt":
                      ndivs = -407
                    elif reg == 'signalregion' and variableName=="jet2_pt":
                      ndivs = -408
                    else: ndivs = -1*(300 + int(h_prefit.GetNbinsX()/2))

                    summed_group[group].GetXaxis().SetNdivisions(ndivs)


                    # Now update the histogram dictionary
                    for proc in group_info["processes"]: 
                        if proc in summed:
                            #print("Popping {0}".format( proc ) )
                            summed.pop( proc ) 
                    
                    summed[group] = deepcopy( summed_group[group].Clone("{0}_forStack".format( group ) ) )
                    summed[group].GetXaxis().SetNdivisions(ndivs)

                    # Finally, stack them
                    hstack.Add( summed[group],'PLC' )


                    entries_legend.append( (summed[group], group if "special_name" not in group_info else group_info["special_name"], "f") )

                # Get the data, uncertainty and ratio distributions
                data  = summed["data_obs"]
                total = summed["TotalProcs"]
                data.GetXaxis().SetNdivisions(ndivs)
                total.GetXaxis().SetNdivisions(ndivs)
                if shapedir == "postfit":
                  h_prefit.SetLineColor(r.kRed)
                  h_prefit.SetLineWidth(2)
                  #entries_ratiolegend.append( (h_prefit, "prefit", "l") )
                  #entries_ratiolegend.append( (h_prefit, "Uncertainty", "e3") )
                entries_legend.append( (summed["TotalProcs"], "Uncertainty", "ef") )
                entries_legend.append( (summed["data_obs"], "Data", "pe") )

                """ 
                # For debug
                for pname, h in summed.items():
                    aux.color_msg(" Process {0} has {1} integral".format( pname, h.Integral()), "green", 2)
                    if pname in ["data_obs"]: continue
                    if "TTW" not in pname: continue
                    aux.color_msg(" Process {0} has {1} integral".format( pname, sum( data.GetY())), "green", 2)
                    #for ibin in range(1, h.GetNbinsX()+1):
                    #    aux.color_msg(" Process {0} has {1} yields in bin {2}".format( pname, h.GetBinContent(ibin), ibin), "none", 3)
                """
                aux.color_msg(" Process data has {0} integral".format( sum( data.GetY())), "green", 2)
                aux.color_msg(" Process total has {0} integral".format( total.Integral() ), "green", 2)

                legend = cfgplot.get_legend( entries_legend )
                entries_legend.reverse()
                for entry in entries_legend:
                    #if entry[0].Integral() < 10: continue
                    legend.AddEntry( entry[0], entry[1], entry[2] )


                
                # Now start drawing stuff
                # ------------- Upper pad
                p1.cd()

                p1.SetTicks(1,1)
                tickScaleX = (pad1W -0.21)/pad1W*pad1H
                tickScaleY = (pad1H - 0.08)/pad1H*pad1W

                
                if cfgplot.logy: 
                    p1.SetLogy()

                aux.draw_stack( hstack, data, cfgplot, dividethisvar)

                hstack.GetXaxis().SetTickLength(10/tickScaleX)
                hstack.GetYaxis().SetTickLength(10/tickScaleY)
                hstack.GetXaxis().SetNdivisions(ndivs)

                aux.draw_data( data )
                aux.draw_unc( total )
                legend.Draw("same")


                # check if we need to draw extra lines and labels in the plot
                if cfgplot.extralines:
                   aux.color_msg(" Plot needs extra lines, we assume there are 5 bdt bins", "blue", 2)
                   
                   first = 0.5
                   p1vlines = []
                   bdtbins = 5
                   if analysis == "oviedo" and reg=='asymmetry': 
                     bdtbins = 4 # we can assume it is asymmetry plot if we need extra lines in oviedo, they have 4 eta bins.
                     first = -0.5
                   elif analysis == "oviedo":
                     bdtbins = 4 # we can assume it is asymmetry plot if we need extra lines in oviedo, they have 4 eta bins.
                     first = 0.5
                   elif analysis == 'ghent' and reg == 'trileptoncontrolregion':
                       first = -0.5
                   if "dRl1l2" in variableName:
                       first += 0.05 
                   for i in range( int(total.GetNbinsX()/bdtbins)):
                     first+= bdtbins
                     if cfgplot.logy and reg in ['trileptoncontrolregion', 'cr_3l']: vline = r.TLine(first,0 , first, 0.01*cfgplot.force_y_max)
                     elif cfgplot.logy: vline = r.TLine(first,0 , first, 0.05*cfgplot.force_y_max)
                     else: vline = r.TLine(first,0 , first, 0.6*cfgplot.force_y_max)
                     vline.SetLineColor(r.kBlack)
                     vline.SetLineStyle(r.kDashed)
                     vline.Draw()
                     p1vlines.append(vline)

                   if len(cfgplot.auxbinning) > 0:
                    aux.color_msg(" Plot needs extra text as well to show secondary binning", "blue", 2)
                    tsecondarybinlabels = r.TLatex()
                    #tsecondarybinlabels.SetTextFont(1)
                    tsecondarybinlabels.SetTextSize(0.05)
                    labelyposndc = 0
                    if analysis == "oviedo": tsecondarybinlabels.SetTextSize(0.05)
                    tsecondarybinlabels.SetTextAlign(21)

                    if isinstance(cfgplot.auxbinning[0], int):
                     for i,label in enumerate(cfgplot.auxbinning):
                      labelxpos = 0.5 + i*5 + 5/2.
                      labelxposndc = (labelxpos-r.gPad.GetX1())/(r.gPad.GetX2()-r.gPad.GetX1())
                      labelyposndc = 0.55
                      if isinstance(cfgplot.auxbinning[i], int):
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(", BDT) unrolled bins","")[1:] + " = "+str(label))
                      else:
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(", BDT) unrolled bins","")[1:] + label)
                    elif isinstance(cfgplot.auxbinning[0], str) and reg == 'cr_3l':
                     for i,label in enumerate(cfgplot.auxbinning):
                      labelxpos = 0.5 + i*bdtbins + bdtbins/2. + (1-i)*0.5
                      labelxposndc = (labelxpos-r.gPad.GetX1())/(r.gPad.GetX2()-r.gPad.GetX1())
                      labelyposndc = 0.55
                      tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, str(label))
                    elif isinstance(cfgplot.auxbinning[0], str) and reg == 'trileptoncontrolregion':
                     for i,label in enumerate(cfgplot.auxbinning):
                      labelxpos = -1.5 + i*bdtbins + bdtbins/2. + (1-i)*0.5
                      labelxposndc = (labelxpos-r.gPad.GetX1())/(r.gPad.GetX2()-r.gPad.GetX1())
                      labelyposndc = 0.55
                      tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, str(label))
                    elif isinstance(cfgplot.auxbinning[0], str):
                     for i,label in enumerate(cfgplot.auxbinning):
                      labelxpos = -0.5 + i*bdtbins + bdtbins/2.
                      labelxposndc = (labelxpos-r.gPad.GetX1())/(r.gPad.GetX2()-r.gPad.GetX1())
                      labelyposndc = 0.55
                      tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, str(label))
                    else:
                     for i,label in enumerate(cfgplot.auxbinning):
                      labelxpos = 0.5 + i*5 + 5/2.
                      labelxposndc = (labelxpos-r.gPad.GetX1())/(r.gPad.GetX2()-r.gPad.GetX1())
                      labelxposndc2 = (labelxpos+ 5/2. -r.gPad.GetX1())/(r.gPad.GetX2()-r.gPad.GetX1())
                      labelyposndc = 0.55+0.02
                      """
                      if i == 0:
                        x=cfgplot.auxbinning[1]
                        if x-int(x)==0: x = int(x)
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(", BDT) unrolled bins","")[1:] + "<")
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc2, labelyposndc,str(x))
                      elif i == len(cfgplot.auxbinning)-2:
                        x = cfgplot.auxbinning[-2]
                        if x-int(x)==0: x = int(x)
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, "<"+cfgplot.titleX.replace(", BDT) unrolled bins","")[1:])
                      elif i == len(cfgplot.auxbinning)-1:
                        break
                      else:
                        x = cfgplot.auxbinning[i+1]
                        if label-int(label)==0: label = int(label)
                        if x-int(x)==0: x = int(x)
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, "<" + cfgplot.titleX.replace(", BDT) unrolled bins","")[1:]+ "<")
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc2, labelyposndc,str(x))
                      """
                      if "dRl1l2" in variableName:
                        tsecondarybinlabels.SetTextAngle(90)
                        tsecondarybinlabels.SetTextSize(0.045)
                        labelyposndc = 0.42
                        
                      if i == 0:
                        x=cfgplot.auxbinning[1]
                        if x-int(x)==0: x = int(x)
                        if not ("H}_{T" in cfgplot.titleX or 'p_{T}}(j_{1}' in cfgplot.titleX):
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc+0.01, labelyposndc, cfgplot.titleX.replace(", BDT) unrolled bins","").replace(",\\text{ BDT})\\text{ unrolled bins}","")[1:] + "<"+str(x))
                        else:
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(", BDT) unrolled bins","").replace(",\\text{ BDT})\\text{ unrolled bins}","")[1:] + "<"+str(x))

                      elif i == len(cfgplot.auxbinning)-2:
                        x = cfgplot.auxbinning[-2]
                        if x-int(x)==0: x = int(x)
                        if not ("H}_{T" in cfgplot.titleX or 'p_{T}}(j_{1}' in cfgplot.titleX):
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc+0.01, labelyposndc, cfgplot.titleX.replace(", BDT) unrolled bins","").replace(",\\text{ BDT})\\text{ unrolled bins}","")[1:] + "\\geq"+str(x))
                        else:
                          print("special")
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(", BDT) unrolled bins","").replace(",\\text{ BDT})\\text{ unrolled bins}","")[1:] + "#geq"+str(x))

                      elif i == len(cfgplot.auxbinning)-1:
                        break
                      else:
                        x = cfgplot.auxbinning[i+1]
                        if label-int(label)==0: label = int(label)
                        if x-int(x)==0: x = int(x)
                        if not ("H}_{T" in cfgplot.titleX or 'p_{T}}(j_{1}' in cfgplot.titleX):
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc+0.01, labelyposndc, "\\text{"+str(label)+"}\\leq" + cfgplot.titleX.replace(", BDT) unrolled bins","").replace(",\\text{ BDT})\\text{ unrolled bins}","")[1:] + "<\\text{"+str(x)+"}")
                        else:
                          print("special")
                          tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, str(label)+"#leq" + cfgplot.titleX.replace(", BDT) unrolled bins","").replace(",#text{ BDT})#text{ unrolled bins}","")[1:] + "<"+str(x))               

 
     
                # Draw labels
                if prel: 
                    cfgplot.make_prelim(variableName)
                for spam, metaspam in cfgplot.spams.items():

                    text = metaspam["text"]
                    text = text.replace( "__FITLABEL__", "Prefit" if shapedir == "prefit" else "Postfit" )
                    text = text.replace( "__REGIONLABEL__", region_labels[reg]["label"][0])
                    text = text.replace( "__LEPTONLABEL__", region_labels[reg]["label"][1])
                    text = text.replace( "__LUMI__", "{0}".format(lumis[year]))
                    aux.doSpam( text, metaspam["x0"], metaspam["y0"], metaspam["x1"], metaspam["y1"], textSize = metaspam["textsize"])


                p2.cd()
                ratio = deepcopy( data.Clone( "axis_{0}".format(variableName) ) )

                htotalErr, ratio, prefit = aux.draw_ratio( ratio, total, data, cfgplot, h_prefit,shapedir,cfgs )
                #htotalErr.GetXaxis().SetTickLength(0.24 * (p2.GetWh() * p2.GetAbsHNDC()) / (p1.GetWh() * p1.GetAbsHNDC()))
                p2.SetTicks(1,1)
                tickScaleX = (pad2W -0.21)/pad2W*pad2H
                tickScaleY = (pad2H - 0.08)/pad2H*pad2W
                if "eventBDT" == variableName: ndivs = -504
                if "BDT" in variableName: ndivs = -1*(500 + int(h_prefit.GetNbinsX()/5))
                elif reg == "asymmetry": ndivs = -1*(400 + int(h_prefit.GetNbinsX()/4))
                elif reg == 'cfjetscontrolregion' and variableName=="lep1_pt":
                      ndivs = -407
                elif reg == 'signalregion' and variableName=="jet2_pt":
                      ndivs = -408
                elif reg == 'signalregion' and variableName=="lep1_pt":
                      ndivs = -407
                else: ndivs = -1*(300 + int(h_prefit.GetNbinsX()/2))
                htotalErr.GetXaxis().SetTickLength(10/tickScaleX)
                htotalErr.GetYaxis().SetTickLength(10/tickScaleY)
                htotalErr.GetXaxis().SetNdivisions(ndivs)
                #htotalErr.GetYaxis().SetNdivisions(202)

                if shapedir == "postfit" and reg in ["asymmetry","3l"]: htotalErr.GetYaxis().SetRangeUser( cfgplot.ymin_ratio, cfgplot.ymax_ratio+0.5 )
                elif shapedir == "postfit": htotalErr.GetYaxis().SetRangeUser( cfgplot.ymin_ratio, cfgplot.ymax_ratio+0.25 )

                # For some reason root deletes these 
                if shapedir == "postfit":
                    print("drawing prefit")

                    prefit_extra = prefit.Clone()
                    prefit.SetFillColorAlpha(r.kRed-9,1.)
                    prefit.SetFillStyle(1001)
                    prefit.SetMarkerSize(0)
                    prefit_extra.SetMarkerSize(0)
                    #prefit_extra.Draw("hist")
                    if cfgs.plots['prefiterror']: 
                      print("and prefit errors")
                      prefit.Draw("e2 ")
                      prefit_extra.Draw("hist same")
                    if cfgs.plots['prefitwithdata']:
                      entries_ratiolegend.append( (prefit, "Data/prefit", "lpf") )
                      entries_ratiolegend.append( (ratio, "Data/postfit", "pe" ) )
                    else:
                      entries_ratiolegend.append( (prefit, "prefit MC", "lpf") )
                    #entries_ratiolegend.append( (prefit, "Uncertainty", "lpf") )

                htotalErrExtra = htotalErr.Clone()
                htotalErrExtra.SetLineWidth(0)
                htotalErrExtra.Draw("e2 same")
                for ibin in range(1, htotalErr.GetNbinsX()+1):
                  htotalErr.SetBinError(ibin, 0)
                #  htotalErr.SetBinContent(ibin, 1)
                htotalErr.SetFillStyle(0)
                htotalErr.Draw("hist same")
                ratio.Draw("pe0 same") 


                if len(entries_ratiolegend)>0:
                    ratiolegend = cfgplot.get_ratiolegend( )
                    print("making prefit legend")
                    print(ratiolegend)
                    for entry in entries_ratiolegend:
                        ratiolegend.AddEntry( entry[0], entry[1], entry[2] )
                    ratiolegend.Draw("same")

                # check if we need to draw extra lines
                if cfgplot.extralines:
                   aux.color_msg(" Plot needs extra lines, we assume there are 5 bdt bins", "blue", 2)
                   auxbinning = cfgplot.auxbinning 
               
                   first = 0.5
                   p2vlines = []
                   bdtbins = 5
                   if analysis == "oviedo" and reg == 'cr_3l':
                       first = 0.5
                       bdtbins = 4

                   elif analysis == "oviedo":
                     bdtbins = 4 # we can assume it is asymmetry plot if we need extra lines in oviedo, they have 4 eta bins.
                     first = -0.5
                   elif analysis == 'ghent' and reg == 'trileptoncontrolregion':
                       first = -0.5


                   height = 1.5
                   if shapedir == "postfit" and reg in ["asymmetry"]: height=cfgplot.ymax_ratio-0.25
                   elif shapedir == "postfit" and variableName in ["_eventBDTHT","_eventBDTdRl1l2"]:height=cfgplot.ymax_ratio
                   elif shapedir == "postfit" and variableName in ["_eventBDTnJets"]:height=cfgplot.ymax_ratio-0.1
                   elif shapedir == "postfit": height=cfgplot.ymax_ratio
                   first+= bdtbins
                   vline = r.TLine(first,cfgplot.ymin_ratio , first, height)
                   vline.SetLineColor(r.kBlack)
                   vline.SetLineStyle(r.kDashed)
                   vline.Draw()
                   p2vlines.append(vline)
                   #if shapedir == "postfit" and reg in ["asymmetry"]: height=cfgplot.ymax_ratio+0.25
                   #elif shapedir == "postfit" and variableName in ["_eventBDTHT","_eventBDTdRl1l2"]:height += 0.25
                   #elif shapedir == "postfit" and variableName in ["_eventBDTnJets"]:height += 0.35

                   for i in range(1, int(total.GetNbinsX()/bdtbins)):
                     first+= bdtbins
                     vline = r.TLine(first,cfgplot.ymin_ratio , first, height)
                     if reg in ["asymmetry"]: vline = r.TLine(first,cfgplot.ymin_ratio , first, height)
                     vline.SetLineColor(r.kBlack)
                     vline.SetLineStyle(r.kDashed)
                     vline.Draw()
                     p2vlines.append(vline)

 
                label = "counting" if analysis == "oviedo" else "bdt"
                if not os.path.exists( outname  ):
                    os.system("mkdir -p {0}".format( outname  ))
                    os.system("cp index.php {0}".format( outname ))

                
                c.SaveAs( os.path.join( outname + "/{0}_{1}_{2}_{3}.png".format(label, reg, variableName, shapedir)) )
                c.SaveAs( os.path.join( outname + "/{0}_{1}_{2}_{3}.pdf".format(label, reg, variableName, shapedir)) )
                c.SaveAs( os.path.join( outname + "/{0}_{1}_{2}_{3}.eps".format(label, reg, variableName, shapedir)) ) 


                #os.system("epstopdf {}".format(outname + "/{0}_{1}_{2}_{3}.eps".format(label, reg, variableName, shapedir)))
