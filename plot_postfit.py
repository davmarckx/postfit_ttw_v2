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
        "2018":"2018",
        "2017":"2017",
        "2016post":"2016post",
        "2016pre":"2016pre" 
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
            #"3l" : { "binname" : "3l_0tau", "label" : ["SR 3L", "(Tight)"] },
            #"2lss_plus" : { "binname" : "positive", "label" : ["SR 2L+", "(Tight)"] },
            #"2lss_minus" : { "binname" : "negative", "label" : ["SR 2L-", "(Tight)"] },
            "cr_nonprompt" : { "binname" : "2lss", "label" : ["NP VR", "(Tight)"] },
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
            #"sigreg" : { "binname" : "signalregion", "label" : ["#scale[1.]{SR 2L}", "#scale[0.8]{(Loose)}"] },
            #"cfjetscontrolregion" : { "binname" : "cfjets", "label" : ["#scale[1.]{CR CF+jets}", "#scale[0.8]{(Loose)}"] },
            #"cfcontrolregion" : { "binname" : "cf", "label" : ["#scale[1.]{CR CF}", "#scale[0.8]{(Loose)}"] },
            #"npcontrolregion" : { "binname" : "npcontrolregion", "label" : ["#scale[1.]{CR NP}", "#scale[0.8]{(Loose)}"] },
            #"trileptoncontrolregion" : { "binname" : "trileptoncontrolregion", "label" : ["#scale[1.]{CR 3L}", "#scale[0.8]{(Loose)}"] },
            #"fourleptoncontrolregion" : { "binname" : "fourleptoncontrolregion", "label" : ["#scale[1.]{CR 4L}", "#scale[0.8]{(Loose)}"] },
        }
        match_ch = r'shapes \*\s+ch(\d+)\s+([^\s]+)'
        
    else:
        aux.color_msg("Analysis {0} not valid.".format( analysis ) )
        sys.exit(0)
        
        
        
    aux.color_msg("Producing postfit plots from {0}".format( inputFolder ), color = "green", indentlevel = 0)

    keyword = "bdt" if analysis == "ghent" else "counting"
    for reg in region_labels.keys():
        print(reg)
        # Get the list of variables to be plot 
        variables = cfgs.plots[analysis][ reg ]
        print(variables)
        for variableName, variable in variables.items():
            print(variableName)
            #if "eventBDT" in variableName: continue

            # flag to see if we need to divide this var by width
            dividethisvar = cfgs.plots['binwidth'] and variableName in cfgs.plots[analysis]['needwidth']
            if dividethisvar:
              print("dividing by binwidth")

            # Get the plot configs
            cfgplot = deepcopy( variable )
            cfgplot.modify( "{0}_{1}".format( reg, analysis ) )
            if "plus" in reg: 
                cfgplot.force_y_max *= 0.7
            elif "minus" in reg:
                cfgplot.force_y_max *= 0.7
                
            if analysis == "oviedo":
                
                if reg in ["cr_3l", "cr_4l"]:    
                    inputFile = os.path.join( inputFolder, "2lss", "njets", "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, "2lss", "njets", "combined_njets_2lss.dat" ) 
                elif reg in  ["2lss_plus", "2lss_minus"]:
                    inputFile = os.path.join( inputFolder, "2lss", variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, "2lss", variableName, "combined_{0}_2lss.dat".format( variableName )) 
                elif reg in ["3l"]:
                    inputFile = os.path.join( inputFolder, "3l", variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, "3l", variableName, "combined_{0}_3l.dat".format( variableName )) 
                elif reg in ["cr_nonprompt"]:
                    inputFile = os.path.join( inputFolder, "cr_nonprompt", variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, "cr_nonprompt", variableName, "combined_{0}_2lss.dat".format( variableName )) 
                else:
                    inputFile = os.path.join( inputFolder, region_labels[reg]["binname"], variableName, "ttW_OUT.root" )
                    combinedCard = os.path.join( inputFolder, region_labels[reg]["binname"], variableName, "combined_{0}_{1}.dat".format( variableName, region_labels[reg]["binname"] ) )
                
                
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
            print(channels)
            #print(combinedCard, region_labels[reg]["binname"], match_ch)
            if analysis == "ghent":
                channels = [ channels[0] ]
                if reg == "sigreg":
                  channels = ['ch1']
                elif reg == "signalregion" and "njets" in variableName:
                  channels = ['ch1']
                elif reg == "signalregion" and "eventBDT" in variableName:
                  channels = ['ch1']
                elif reg == "signalregion" and ("HT" == variableName):
                  channels = ['ch2']
                elif reg == "signalregion" and ( "lt" == variableName):
                  channels = ['ch2']


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

                if shapedir == "postfit": c, p1, p2 = aux.new_postfitcanvas( "canvas_{0}".format( shapedir ) )
                else: c, p1, p2 = aux.new_canvas( "canvas_{0}".format( shapedir ) )
                
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

                    # Now update the histogram dictionary
                    for proc in group_info["processes"]: 
                        if proc in summed:
                            #print("Popping {0}".format( proc ) )
                            summed.pop( proc ) 
                    
                    summed[group] = deepcopy( summed_group[group].Clone("{0}_forStack".format( group ) ) )

                    # Finally, stack them
                    hstack.Add( summed[group],'PLC' )


                    entries_legend.append( (summed[group], group if "special_name" not in group_info else group_info["special_name"], "f") )


                # Get the data, uncertainty and ratio distributions
                data  = summed["data_obs"]
                total = summed["TotalProcs"]
                if shapedir == "postfit":
                  h_prefit.SetLineColor(r.kRed)
                  h_prefit.SetLineWidth(2)
                  entries_ratiolegend.append( (h_prefit, "prefit", "l") )
                entries_legend.append( (summed["TotalProcs"], "Uncertainty", "ef") )
                entries_legend.append( (summed["data_obs"], "Data", "pe") )

                #for pname, h in summed.items():
                #    aux.color_msg(" Process {0} has {1} integral".format( pname, h.Integral()), "green", 2)
                #    if pname in ["data_obs"]: continue
                #    for ibin in range(1, h.GetNbinsX()+1):
                #        aux.color_msg(" Process {0} has {1} yields in bin {2}".format( pname, h.GetBinContent(ibin), ibin), "none", 3)

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
                
                if cfgplot.logy: 
                    p1.SetLogy()
                aux.draw_stack( hstack, data, cfgplot, dividethisvar)
                aux.draw_data( data )
                aux.draw_unc( total )
                legend.Draw("same")

                # check if we need to draw extra lines and labels in the plot
                if cfgplot.extralines:
                   aux.color_msg(" Plot needs extra lines, we assume there are 5 bdt bins", "blue", 2)
                   
                   first = 0.5
                   p1vlines = []
                   bdtbins = 5
                   if analysis == "oviedo": 
                     bdtbins = 4 # we can assume it is asymmetry plot if we need extra lines in oviedo, they have 4 eta bins.
                     first = -0.5
 
                   for i in range(total.GetNbinsX()/bdtbins):
                     first+= bdtbins
                     if cfgplot.logy: vline = r.TLine(first,0 , first, 0.05*cfgplot.force_y_max)
                     else: vline = r.TLine(first,0 , first, 0.6*cfgplot.force_y_max)
                     vline.SetLineColor(r.kBlack)
                     vline.SetLineStyle(r.kDashed)
                     vline.Draw()
                     p1vlines.append(vline)

                   if len(cfgplot.auxbinning) > 0:
                    aux.color_msg(" Plot needs extra text as well to show secondary binning", "blue", 2)
                    tsecondarybinlabels = r.TLatex()
                    #tsecondarybinlabels.SetTextFont(10*labelfont+3)
                    tsecondarybinlabels.SetTextSize(0.025)
                    if analysis == "oviedo": tsecondarybinlabels.SetTextSize(0.035)
                    tsecondarybinlabels.SetTextAlign(21)

                    if isinstance(cfgplot.auxbinning[0], int):
                     for i,label in enumerate(cfgplot.auxbinning):
                      labelxpos = 0.5 + i*5 + 5/2.
                      labelxposndc = (labelxpos-r.gPad.GetX1())/(r.gPad.GetX2()-r.gPad.GetX1())
                      labelyposndc = 0.55
                      tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(" fitting bins","") + " = "+str(label))
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
                      labelyposndc = 0.55
                      print(labelxposndc)
                      print(labelxpos)
                      if i == 0:
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(" fitting bins","") + " < "+str(cfgplot.auxbinning[1]))
                      elif i == len(cfgplot.auxbinning)-2:
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, cfgplot.titleX.replace(" fitting bins","") + " > "+str(cfgplot.auxbinning[-2]))
                      elif i == len(cfgplot.auxbinning)-1:
                        break
                      else:
                        tsecondarybinlabels.DrawLatexNDC(labelxposndc, labelyposndc, str(label)+" < " + cfgplot.titleX.replace(" fitting bins","") + " < "+str(cfgplot.auxbinning[i+1]))

               

 
     
                # Draw labels
                if prel: 
                    cfgplot.make_prelim()
                for spam, metaspam in cfgplot.spams.items():

                    text = metaspam["text"]
                    text = text.replace( "__FITLABEL__", "Prefit" if shapedir == "prefit" else "Postfit" )
                    text = text.replace( "__REGIONLABEL__", region_labels[reg]["label"][0])
                    text = text.replace( "__LEPTONLABEL__", region_labels[reg]["label"][1])
                    text = text.replace( "__LUMI__", "{0}".format(lumis[year]))
                    aux.doSpam( text, metaspam["x0"], metaspam["y0"], metaspam["x1"], metaspam["y1"], textSize = metaspam["textsize"])


                p2.cd()
                ratio = deepcopy( data.Clone( "axis_{0}".format(variableName) ) )

                htotalErr, ratio, prefit = aux.draw_ratio( ratio, total, data, cfgplot, h_prefit )
                htotalErr.GetXaxis().SetTickLength(0.24 * (p2.GetWh() * p2.GetAbsHNDC()) / (p1.GetWh() * p1.GetAbsHNDC()))
                if shapedir == "postfit": htotalErr.GetYaxis().SetRangeUser( cfgplot.ymin_ratio, cfgplot.ymax_ratio+0.5 )


                # For some reason root deletes these 
                if shapedir == "postfit":
                    print("drawing prefit")
                    prefit.Draw("")
                htotalErr.Draw("e2 same")
                htotalErr.Draw("l same")
                ratio.Draw("pe0 same")  
                #if shapedir == "postfit":
                #    print("drawing prefit")
                #    prefit.Draw("same")           

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
                   if analysis == "oviedo":
                     bdtbins = 4 # we can assume it is asymmetry plot if we need extra lines in oviedo, they have 4 eta bins.
                     first = -0.5

                   for i in range(total.GetNbinsX()/bdtbins):
                     first+= bdtbins
                     vline = r.TLine(first,0.5 , first, 1.5)
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
        
