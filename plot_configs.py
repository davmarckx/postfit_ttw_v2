import ROOT as r

binwidth = True
logy = False
prefiterror = True
prefitwithdata = True
nlegendcols = 2

class plot( object ):
    """ Description of a plot """
    def __init__(self, name):
        self.name = name

        # >> Things for the x axis
        self.rangex = None
        self.binlabels = []

        # >> Things for the y axis
        self.force_y_max = None
        self.ScaleUpperY = 1.1  
        self.ymin_ratio = 0.7
        self.ymax_ratio = 1.5
        self.logy = False

        # >> Title 
        self.titleX = "My variable"
        self.titleY = "Events"
        
        # >> Legend
        self.leg_x0 = 0.22
        self.leg_x1 = 0.42
        self.leg_y0 = 0.81
        self.leg_ncolumns = 1
        self.corner = "TR"
        self.leg_height = 7 # This is a factor applied to the following formula: leg_ymin = 0.9 - leg_textsize * 1.15 * leg_height

        self.ratioleg_x0 = 0.18
        self.ratioleg_x1 = 0.31
        self.ratioleg_y0 = 0.8


        # >> Keep here your spams
        
        self.spams = {
            "lumi" : {
                "text" : "__LUMI__ fb^{-1} (13 TeV)", 
                "x0"   : .69, 
                "y0"   : .963, 
                "x1"   : .975, 
                "y1"   : .99, 
                "textsize" : 22
            },
            "cmsprel" : {
                "text" : "#splitline{#scale[1.2]{#bf{CMS}}}{}",
                "x0"   : .2, 
                "y0"   : .870, 
                "x1"   : .35, 
                "y1"   : .885, 
                "textsize" : 22      
            },
            "fit" : {
                "text" : '#splitline{#scale[1.]{#font[62]{__REGIONLABEL__}}}{#splitline{#scale[1.]{#font[62]{__LEPTONLABEL__}}}{#scale[1.]{#font[62]{__FITLABEL__}}}}', 
                "x0"   : .75, 
                "y0"   : .825, 
                "x1"   : .90, 
                "y1"   : .865, 
                "textsize" : 22
            }
        }
        return

    def modify_spam(self, label, field, value):
        self.spams[label][field] = value
        return self
    
    def make_prelim(self,var):
        self.spams["cmsprel"]["text"] = "#scale[1.2]{#bf{CMS}}#scale[1.0]{#it{}}"#"#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}"
        self.spams["cmsprel"]["x0"] = .16
        self.spams["cmsprel"]["y0"] = .963
        self.spams["cmsprel"]["y1"] = .988
 
        if self.spams["fit"]["x0"] == 0.2 and self.spams["fit"]["y0"] > 0.7 and var != 'nn':
          print("putting labels higher")
          print(var)
          self.spams["fit"]["y0"] += 0.05
          self.spams["fit"]["y1"] += 0.05


                
    def get_legend(self, entries):
        """ Fixed format for a one column legend """
        leg_textsize = 0.05616#0.04116 #0.05616
        leg_height = len(entries) // self.leg_ncolumns
        width = 0.2*(1 + 1.05*self.leg_ncolumns)
        height = leg_textsize * ( 1.30 - 0.03*self.leg_ncolumns ) * leg_height
        legend = r.TLegend(self.leg_x0, self.leg_y0, self.leg_x0 + width, self.leg_y0 + height) 
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetShadowColor(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)
        legend.SetTextSize( leg_textsize )
        legend.SetNColumns( self.leg_ncolumns )
        return legend

    def get_ratiolegend(self):
        """ Fixed format for a one column legend """
        leg_textsize = 0.1016#0.04116 #0.05616
        leg_height = 1
        width = 0.26*(1 + 1.05)
        height = leg_textsize * ( 1.30 - 0.03 ) * leg_height
        legend = r.TLegend(self.ratioleg_x0, self.ratioleg_y0, self.ratioleg_x0 + width, self.ratioleg_y0 + height)
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetShadowColor(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)
        legend.SetTextSize( leg_textsize )
        legend.SetNColumns( 2 )
        return legend

class lep1_pt_plot(plot):
    def __init__(self):
        plot.__init__(self, "lep1_pt")
        self.titleX = r"Leading lepton #it{p}_{T} (GeV)"
        self.titleY = r"Events / 12.5 GeV"
        self.titleY_binwidth = r"#LT \text{Events / GeV} #GT"
        self.binning = [25, 50, 75, 120, 200]
              
    def modify(self, region):
        self.logy = logy
        self.extralines = False
        self.auxbinning = []        
        if region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 750
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.85)
            self.modify_spam("fit", "y1", 0.72)
            
        elif "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

        elif "np" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 500
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.32)
            self.modify_spam("fit", "y0", 0.46)
            self.modify_spam("fit", "y1", 0.52)
            self.rangex = (25., 200.) 

        elif "signalregion" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 1400
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            self.rangex = (25., 200.)

        elif "ghent" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 500

            self.ymin_ratio = 0.5
            self.ymax_ratio = 1.5

            self.modify_spam("fit", "x0", 0.55)
            self.modify_spam("fit", "x1", 0.65)
            self.modify_spam("fit", "y0", 0.6)
            self.modify_spam("fit", "y1", 0.47)
            self.rangex = (25., 200.) 

      
class jet1_pt_plot(plot):
    def __init__(self):
        plot.__init__(self, "jet1_pt_plot")
        self.titleX = r"Leading jet #it{p}_{T} (GeV)"
        self.titleY = r"Events "
        self.titleY_binwidth = r"#LT Events / GeV #GT"
        self.binning = [25, 100, 180, 300]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = [] 
        if region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1150
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.88)
            self.modify_spam("fit", "y1", 0.75)
            
        elif "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1150
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)  
        
        elif "signalregion" in region: 
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1250
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
            self.rangex = (25., 300.)

class jet2_pt_plot(plot):
    def __init__(self):
        plot.__init__(self, "jet2_pt_plot")
        self.titleX = r"Subleading jet #it{p}_{T} (GeV)"
        self.titleY = r"Events / 9.72 GeV"
        self.titleY_binwidth = r"\langle \text{Events / GeV} \rangle"
        self.binning = [25.0, 90.0, 150.0, 200.0]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if region == "cr_nonprompt_oviedo":
            self.logy = True
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 11000
            self.modify_spam("fit", "x0", 0.75)
            self.modify_spam("fit", "x1", 0.92)
            self.modify_spam("fit", "y0", 0.42)
            self.modify_spam("fit", "y1", 0.62)
            
        elif "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1400
            self.modify_spam("fit", "x0", 0.62)
            self.modify_spam("fit", "x1", 0.67)
            self.modify_spam("fit", "y0", 0.42)
            self.modify_spam("fit", "y1", 0.62) 
 
        elif "signalregion" in region:
            self.leg_x0, self.leg_y0 =0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 1250
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            self.rangex = (25, 200)


class jet1_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "jet1_eta")
        self.titleX = r"Leading jet |#eta|"
        self.titleY = r"Events "
        self.titleY_binwidth = "dN / d#eta"
        self.binning = [0, 0.5, 1.0, 1.5, 2.5]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 600
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.62)
            self.modify_spam("fit", "y1", 0.72)
        elif "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.62)
            self.modify_spam("fit", "y1", 0.72)
                      
class jet2_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "jet2_eta")
        self.titleX = r"Subleading jet |#eta|"
        self.titleY = r"Events "
        self.titleY_binwidth = "dN / d#eta"
        self.binning = [0, 0.5, 1.0, 1.5, 2.5]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 600
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
        elif "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
                
class lep2_pt_plot(plot):
    def __init__(self):
        plot.__init__(self, "lep2_pt")
        self.titleX = r"Subleading lepton #it{p}_{T} (GeV)"
        self.titleY = r"Events / 10 GeV"
        self.titleY_binwidth = r"#LT Events / GeV #GT"
        self.binning = [15, 30, 50, 100]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 1050
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)   
               
        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.ymin_ratio = 0.7
            self.ymax_ratio = 1.3
            self.force_y_max = 750
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)  
 
        elif "np" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 460

            self.ymin_ratio = 0.45
            self.ymax_ratio = 1.3

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)           
            self.rangex = (15., 100.)
 
        elif "signalregion" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 2700
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            self.rangex = (15., 100.)      
 
        elif "ghent" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 600
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)           
            self.rangex = (15., 120.)

class lep2_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "lep2_eta")
        self.titleX = r"Subleading lepton |#eta|"
        self.titleY = r"Events / 0.25 units"
        self.titleY_binwidth = r"#LT Events / unit #GT"
        self.binning = [0, 0.5, 1.0, 1.5, 2.5]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 400
            self.ymin_ratio = 0.8
            self.ymax_ratio = 1.3
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.80)
            self.modify_spam("fit", "y1", 0.67)
        elif "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

        elif "npctr_incl" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 150
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

        elif "npctr_" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 50
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)


        elif "np" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 220

            self.ymin_ratio = 0.5
            self.ymax_ratio = 1.1


            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

        elif "ghent" in region and "cf" not in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 600

            self.ymin_ratio = 0.5
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
            
        elif "ghent" in region and "cf" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 190
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.28)
            self.modify_spam("fit", "y0", 0.46)
            self.modify_spam("fit", "y1", 0.56)
            
class lep1_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "lep1_eta")
        self.titleX = r"Leading lepton |#eta|"
        self.titleY = r"Events / 0.25 units"
        self.titleY_binwidth = r"#LT Events / unit #GT"
        self.binning = [0, 0.5, 1.0, 1.5, 2.5]
              
    def modify(self, region):
        self.logy = logy
        self.extralines = False
        self.auxbinning = []
        if region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.22)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
        elif "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
        elif "npctr_incl" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 150
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

        elif "npctr_" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 50
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

        elif "ghent" in region and "cf" not in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

        elif "ghent" in region and "cf" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 380
              
            if prefiterror: self.ymin_ratio = 0.5
            self.modify_spam("fit", "x0", 0.20)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.6)
            self.modify_spam("fit", "y1", 0.47)
        
class bdt_plot(plot):
    def __init__(self):
        plot.__init__(self, "bdt")
        self.titleX = r"BDT output"
        self.titleY = r"Events / 0.05 units"
        self.binning = [2.5,3.5,4.5,5.5,6.5]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        """
        if  "ghent" in region:
            self.leg_x0, self.leg_y0 = 0.42, 0.44
            self.leg_ncolumns = 2
            #self.force_y_max = 10000
            #self.logy = True
            self.binning = [2.5,3.5,4.5,5.5]
            self.modify_spam("fit", "text", '#scale[1.2]{__REGIONLABEL__} #scale[1.0]{__FITLABEL__}')

            self.modify_spam("fit", "x0", 0.58)
            self.modify_spam("fit", "x1", 0.68)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.85)
        """ 
            
        if region == "cfjetscontrolregion_ghent":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 2000
            self.logy = True
            self.binning = [2.5,3.5,4.5,5.5]
            #self.modify_spam("fit", "text", '#splitline{#scale[1.2]{__REGIONLABEL__}}{#scale[1.0]{__FITLABEL__}}')

            self.modify_spam("fit", "x0", 0.58)
            self.modify_spam("fit", "x1", 0.68)
            self.modify_spam("fit", "y0", 0.4)
            self.modify_spam("fit", "y1", 0.45)

        elif region == "cfcontrolregion_ghent":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 200000
            self.logy = True
            self.binning = [2.5,3.5,4.5,5.5]
            #self.modify_spam("fit", "text", '#splitline{#scale[1.2]{__REGIONLABEL__}}{#scale[1.0]{__FITLABEL__}}')

            self.modify_spam("fit", "x0", 0.58)
            self.modify_spam("fit", "x1", 0.68)
            self.modify_spam("fit", "y0", 0.4)
            self.modify_spam("fit", "y1", 0.45)
        elif "np" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 2000
            self.logy = True
            self.binning = [2.5,3.5,4.5,5.5]
            #self.modify_spam("fit", "text", '#splitline{#scale[1.2]{__REGIONLABEL__}}{#scale[1.0]{__FITLABEL__}}')

            self.modify_spam("fit", "x0", 0.58)
            self.modify_spam("fit", "x1", 0.68)
            self.modify_spam("fit", "y0", 0.4)
            self.modify_spam("fit", "y1", 0.45)


class nmuons_plot(plot):
    def __init__(self):
        plot.__init__(self, "nmuons")
        self.titleX = r"Number of muons"
        self.titleY = r"Events / bin"
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "ghent" in region and "np" not in region:
            #self.leg_x0, self.leg_y0 = 0.6, 0.26
            #self.leg_ncolumns = 1
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            
            self.force_y_max = 3500
            self.binning = [0.5,1.5,2.5]
            
            self.modify_spam("fit", "x0", 0.22)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
            
            self.binlabels = ["0", "1", "2"]
            self.rangex = (-0.5, 2.5)



class _eventBDTHT_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTHT")
        self.titleX = "(#it{H}_{T}, BDT) unrolled bins"
        self.titleY = r"Events "


    def modify(self, region):
        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 250.0, 400.0, 600.0, 1000.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTnJets_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTnJets")
        self.titleX = "(#it{N_{jets}}, BDT) unrolled bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [3,4,5,6,'>6']

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1800
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5,20.5,21.5,22.5,23.5,24.5]
            if prefiterror: self.ymax_ratio = 1.5
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 25.)


class _eventBDTdRl1l2_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTdRl1l2")
        self.titleX = "(\\Delta\\text{R}(\\ell_{1},\\ell_{2}),\\text{ BDT})\\text{ unrolled bins}"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 1.6, 2.5, 3.3, 5.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1600
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.20)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTdeltaEtaLeadingLeptonPair_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTdeltaEtaLeadingLeptonPair")
        self.titleX = "#Delta #eta(l1,l2) fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.5, 1.1, 1.8, 3.0] 

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTdRl1bjet_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTdRl1bjet")
        self.titleX = " #Delta R(l1,b-jet)_{min} fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.6, 1.1, 1.8, 3.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)


class _eventBDTdRl1jet_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTdRl1jet")
        self.titleX = " #Delta R(l1,j)_{min} fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 1.0, 1.5, 2.0, 3.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTbjetAbsEtaLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTbjetAbsEtaLeading")
        self.titleX = " |#eta(b-jet 1)| fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.5, 1.0, 1.5, 2.5, 1000] # last one added to plot upper limit

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1400
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)


class _eventBDTjetAbsEtaLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTjetAbsEtaLeading")
        self.titleX = " |#eta(jet 1)| fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.5, 1.0, 1.5, 2.5] # last one added to plot upper limit

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1400
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTjetAbsEtaSubLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTjetAbsEtaSubLeading")
        self.titleX = " |#eta(jet 2)| fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.5, 1.0, 1.5, 2.5,1000] # last one added to plot upper limit

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1400
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTbjetPtLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTbjetPtLeading")
        self.titleX = " p_{T}(b-jet 1) fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [25.0, 85.0, 150.0, 200.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1"]
            self.rangex = (1., 15.)


class _eventBDTjetPtLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTjetPtLeading")
        self.titleX = "(#it{p_{T}}(j_{1}), BDT) unrolled bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [25.0, 100.0, 180.0, 300.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1"]
            self.rangex = (1., 15.)

class _eventBDTjetPtSubLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTjetPtSubLeading")
        self.titleX = " p_{T}(jet 2) fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [25.0, 90.0, 150.0, 200.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1"]
            self.rangex = (1., 15.)

class _eventBDTleptonAbsEtaLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTleptonAbsEtaLeading")
        self.titleX = " |#eta(l1)| fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.5, 1.0, 1.5, 2.5, 1000] # last one added to plot upper limit

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1400
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDT_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDT")
        self.titleX = " BDT output score"
        self.titleY = r"Events / 0.05 units "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.logy = logy
            self.extralines = False
            self.auxbinning = []

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1450
            #self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5,20.5]
            
            self.ymin_ratio = 0.5
            self.ymax_ratio = 1.25            

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            #self.binlabels = ["0.", "0.1", "","0.2", "", "0.3", "", "0.4", "", "0.5","", "0.6", "", "0.7","", "0.8", "", "0.9", "","1"]
            self.rangex = (0., 1.)


class _eventBDTleptonAbsEtaSubLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTleptonAbsEtaSubLeading")
        self.titleX = " |#eta(l2)| fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.5, 1.0, 1.5, 2.5, 1000] # last one added to plot upper limit

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1400
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTleptonMaxEta_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTleptonMaxEta")
        self.titleX = " Max(|#eta(l1)|,|#eta(l2)|) fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 0.5, 1.0, 1.5, 2.5, 1000] # last one added to plot upper limit

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 1400
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTleptonPtLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTleptonPtLeading")
        self.titleX = " p_{T}(l1) fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [25.0, 50.0, 75.0, 120.0, 200.0] 

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2000
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0", "","0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTleptonPtSubLeading_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTleptonPtSubLeading")
        self.titleX = " p_{T}(l2) fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [15.0, 30.0, 50.0, 100.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1"]
            self.rangex = (1., 15.)


class _eventBDTleptonPtSum_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTleptonPtSum")
        self.titleX = "#sum  p_{T}(l) fitting bins"
        self.titleY = r"Events "

    
    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [40.0, 110.0, 185.0, 280.0, 400.0]

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15,5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0", "","0.5", "", "1"]
            self.rangex = (1., 20.)

class _eventBDTM3l_plot(plot):
    def __init__(self):
        plot.__init__(self, "eventBDTM3l")
        self.titleX = " m(leptons) fitting bins"
        self.titleY = r"Events "


    def modify(self, region):

        if "ghent" in region and "np" not in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = nlegendcols
            self.logy = logy
            self.extralines = True
            self.auxbinning = [0.0, 95.0, 185.0, 280.0, 400.0] # last one added to plot upper limit

            if logy: self.force_y_max = 20000
            else: self.force_y_max = 2500
            self.binning = [1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5]

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

            self.binlabels = ["0", "", "0.5", "","1", "0", "", "0.5","", "1", "0", "","0.5", "", "1", "0","", "0.5", "", "1"]
            self.rangex = (1., 20.)


class njets_plot(plot):
    def __init__(self):
        plot.__init__(self, "njets")
        self.titleX = r"Number of jets"
        self.titleY = r"Events / bin"
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 1500
            self.binning = [2.5,3.5,4.5,5.5]
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            
            self.binlabels = ["3", "4", "5","6",">6"]
            self.rangex = (3, 7)
            
        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1400
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.25)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
            
            self.binlabels = ["3", "4", "5"]
            self.rangex = (3, 5)
            
        elif "ghent" in region and "np" not in region:
            #self.leg_x0, self.leg_y0 = 0.6, 0.26
            #self.leg_ncolumns = 1
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            
            self.force_y_max = 3500
            self.binning = [2.5,3.5,4.5,5.5]

            self.ymin_ratio = 0.7
            self.ymax_ratio = 1.05
            
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            
            self.binlabels = ["3", "4", "5", "6", ">6", ""]
            self.rangex = (3, 7)
        
        elif "ghent" in region and "np" in region:
            #self.leg_x0, self.leg_y0 = 0.6, 0.26
            #self.leg_ncolumns = 1
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.ymin_ratio = 0.45
            self.ymax_ratio = 1.2
            
            self.force_y_max = 500
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.62)
            self.modify_spam("fit", "x1", 0.7)
            self.modify_spam("fit", "y0", 0.38)
            self.modify_spam("fit", "y1", 0.45)
            
            self.binlabels = ["3", "4", "5", "6", ">6", ""]
            self.rangex = (3, 7)

class nloosebjets_plot(plot):
    def __init__(self):
        plot.__init__(self, "nbjets")
        self.titleX = r"Number of b-tagged jets"
        self.titleY = r"Events "
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []        
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1600
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.25)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
               
            self.binning = [1.5,2.5,3.5]
            self.binlabels = ["2", "3"]

        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1400
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.25)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
               
            self.binning = [1.5,2.5,3.5]
            self.binlabels = ["2", "3"]
        
        if "ghent" in  region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            
            self.force_y_max = 600
            
            self.modify_spam("fit", "x0", 0.22)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
            self.binning = [0.5, 1.5, 2.5, 3.5]
            self.binlabels = ["1", "2", "3", ">3"]

class nbjets_plot(plot):
    def __init__(self):
        plot.__init__(self, "nbjets")
        self.titleX = r"Number of b-tagged jets"
        self.titleY = r"Events / bin "
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 3500
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
               
            self.binning = [1.5,2.5,3.5]
            self.binlabels = ["2", "3"]

        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 2000
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.25)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
               
            self.binning = [1.5,2.5,3.5]
            self.binlabels = ["2", "3"]
        
        if "ghent" in  region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            
            self.force_y_max = 700

            self.ymin_ratio = 0.7
            self.ymax_ratio = 1.25
            
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            self.binning = [0.5, 1.5, 2.5, 3.5]
            self.binlabels = ["1", "2", "3", ">3"]
class nloosebjets_plot(plot):
    def __init__(self):
        plot.__init__(self, "nbjets")
        self.titleX = r"nloosebjets"
        self.titleY = r"Events "
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []        
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1800
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.25)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
               
            self.binning = [1.5,2.5,3.5]
            self.binlabels = ["2", "3"]

        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1400
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.25)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
               
            self.binning = [1.5,2.5,3.5]
            self.binlabels = ["2", "3"]
        
        if "ghent" in  region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            
            self.force_y_max = 600
            
            self.modify_spam("fit", "x0", 0.22)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.68)
            self.modify_spam("fit", "y1", 0.75)
            self.binning = [0.5, 1.5, 2.5, 3.5]
            self.binlabels = ["1", "2", "3", ">3"]


class cr3l_plot(plot):
    def __init__(self):
        plot.__init__(self, "cr3l")
        self.titleX = r"Number of (b-tagged) jets category"
        self.titleY = r"Events "
        self.binning = [2.5,3.5,4.5,5.5,6.5]
              
    def modify(self, region):
        self.extralines = True
        self.auxbinning = ["0 bj","1 bj",">1 bj"]
        self.leg_ncolumns = 2     
        self.logy = True
        self.leg_ncolumns = 2
        self.force_y_max = 300000
        self.binning = [2.5,3.5,4.5,5.5]
        
        if region == "cr_3l_oviedo":
            self.binlabels = ["1j", "2j", "3j", ">3j", "2j", "3j", "4j", ">4j", "2j", "3j", "4j", ">4j"]
            self.rangex = (0.5, 12.5)
            self.ymax_ratio = 1.55
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67) 
        elif region == "trileptoncontrolregion_ghent":
            self.binlabels = [ "", "", "1j", "2j", "3j", ">3j", "1j", "2j", "3j", "4j", ">4j", "2j", "3j", "4j", ">4j"]
            self.rangex = (0.5, 13.5)
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            if prefiterror: self.ymin_ratio = 0.6
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
        elif region == "cfcontrolregion_ghent":
            self.binlabels = ["", "0b0j", "1j", "2j", "3j", ">3j", "1b1j", "2j", "3j", "4j", ">4j", ">1b2j", "3j", "4j", ">4j"]
            self.rangex = (0.5, 13.5)
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.modify_spam("fit", "x0", 0.72)
            self.modify_spam("fit", "x1", 0.8)
            self.modify_spam("fit", "y0", 0.46)
            self.modify_spam("fit", "y1", 0.54) 
        
class cr4l_plot(plot):
    def __init__(self):
        plot.__init__(self, "cr4l")
        self.titleX = r"Number of jets / Z candidates category"
        self.titleY = r"Events "
        self.binning = [2.5,3.5,4.5,5.5,6.5]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        self.leg_ncolumns = 1     
        self.logy = True
        self.force_y_max = 20000
        if region == "cr_4l_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.64
            self.leg_ncolumns = 2
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.58)
            self.modify_spam("fit", "x1", 0.62)
            self.modify_spam("fit", "y0", 0.52)
            self.modify_spam("fit", "y1", 0.56)
            
            self.binlabels = [ "2Z", "1Z,0j", "1Z,1b", "1Z,>1b"]
            self.rangex = (0.5, 4.5)

        elif region == "fourleptoncontrolregion_ghent":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.binning = [2.5,3.5,4.5,5.5]
            
            self.modify_spam("fit", "x0", 0.20)
            self.modify_spam("fit", "x1", 0.32)
            self.modify_spam("fit", "y0", 0.72)
            self.modify_spam("fit", "y1", 0.76)
            
            self.binlabels = ["Other", "2Z", "1Z,0j", "1Z,1b", "1Z,>1b"]
            self.rangex = (-0.5, 3.5)

class lt_plot(plot):
    def __init__(self):
        plot.__init__(self, "HT")
        self.titleX = r"L_T (GeV)"
        self.titleY = r"Events / "
        self.titleY_binwidth = r"#L_T Events / GeV #GT"
        self.binning = [0, 250, 400, 600, 1000]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38,0.57
            self.leg_ncolumns = 1
            self.force_y_max = 1000
            
            self.modify_spam("fit", "x0", 0.48)
            self.modify_spam("fit", "x1", 0.58)
            self.modify_spam("fit", "y0", 0.65)
            self.modify_spam("fit", "y1", 0.72)
            
        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 1
            self.force_y_max = 1000
            
            self.modify_spam("fit", "x0", 0.48)
            self.modify_spam("fit", "x1", 0.58)
            self.modify_spam("fit", "y0", 0.65)
            self.modify_spam("fit", "y1", 0.72)
            
        elif region == "3l_oviedo":
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 300
            self.modify_spam("fit", "x0", 0.62)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.78)
            self.modify_spam("fit", "y1", 0.85)
            
        elif region == "signalregion_ghent":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2            
            self.force_y_max = 1200
            self.rangex = (60, 600)
            
            self.modify_spam("fit", "x0", 0.53)
            self.modify_spam("fit", "x1", 0.62)
            self.modify_spam("fit", "y0", 0.35)
            self.modify_spam("fit", "y1", 0.48)
           
class HT_plot(plot):
    def __init__(self):
        plot.__init__(self, "HT")
        self.titleX = r"#it{H}_{T} (GeV)"
        self.titleY = r"Events / 50 GeV"
        self.titleY_binwidth = r"#LT Events / GeV #GT"
        self.binning = [0, 250, 400, 600, 1000]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2            
            self.force_y_max = 700
            
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            
        elif region == "cr_nonprompt_oviedo":
            self.logy = True
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 20000
            
            self.modify_spam("fit", "x0", 0.48)
            self.modify_spam("fit", "x1", 0.58)
            self.modify_spam("fit", "y0", 0.35)
            self.modify_spam("fit", "y1", 0.48)
            
        elif region == "3l_oviedo":
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 60
            self.ymin_ratio = 0.6
            self.ymax_ratio = 1.75
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.70)
            self.modify_spam("fit", "y1", 0.78)
            
        elif region == "signalregion_ghent":
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2            
            self.force_y_max = 1200

            self.ymin_ratio = 0.6
            self.ymax_ratio = 1.3 

            self.modify_spam("fit", "x0", 0.53)
            self.modify_spam("fit", "x1", 0.62)
            self.modify_spam("fit", "y0", 0.35)
            self.modify_spam("fit", "y1", 0.48)
            self.rangex = (50., 999.)


class deepflavor_plot(plot):
    def __init__(self):
        plot.__init__(self, "HT")
        self.titleX = r"Highest b tagging discriminant"
        self.titleY = r"Events "
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "cfjetscontrolregion" in region:
            self.leg_x0, self.leg_y0 = 0.3, 0.36
            self.leg_ncolumns = 2
            self.force_y_max = 400
            
            self.modify_spam("fit", "x0", 0.48)
            self.modify_spam("fit", "x1", 0.58)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.82)



class dR_ll_plot(plot):
    def __init__(self):
        plot.__init__(self, "dR_ll")
        self.titleX = r"#DeltaR leptons"
        self.titleY = r"Events "
        self.titleY_binwidth = r"#LT Events / unit #GT"
        self.binning = [0, 1.6, 2.5, 3.3, 5]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 600
            
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)
            

            self.modify_spam("cmsprel", "x0", 0.2)
            self.modify_spam("cmsprel", "x1", 0.37)
        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1250

            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.72)
            self.modify_spam("fit", "y1", 0.78)


            self.modify_spam("cmsprel", "x0", 0.2)
            self.modify_spam("cmsprel", "x1", 0.37)

class deta_llss_plot(plot):
    def __init__(self):
        plot.__init__(self, "dR_ll")
        self.titleX = r"#Delta#eta leptons"
        self.titleY = r"Events "
        self.titleY_binwidth = "dN/d#eta"
        self.binning = [0.0, 0.5, 1.1, 1.8, 3.0]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 800
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
            
        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 600
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

class max_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "max_eta")
        self.titleX = r"max #eta leptons"
        self.titleY = r"Events "
        self.titleY_binwidth = r"#LT Events / unit \GT"
        self.binning = [0, 1.0, 1.5, 2, 2.5]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1400
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
            
        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 600
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.30)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)

class mindr_lep1_jet25_plot(plot):
    def __init__(self):
        plot.__init__(self, "mindr_lep1_jet25")
        self.titleX = r" #Delta R(leading lepton, jet)_{min}"
        self.titleY = r"Events "
        self.titleY_binwidth = "dN/dR"
        self.binning = [0, 1, 1.5, 2, 3]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1400
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
            
        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1000
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.75)
            self.modify_spam("fit", "y1", 0.62)
       
class sum_2lss_pt(plot):
    def __init__(self):
        plot.__init__(self, "sum_2lss_pt")
        self.titleX = r"#Sigma lepton #it{p}_{T} (GeV) "
        self.titleY = r"Events"
        self.titleY_binwidth = r"#LT Events / GeV #GT"
        self.binning = [0.0, 110.0, 185.0, 280.0, 400.0]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.32, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 1000
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.8)
            self.modify_spam("fit", "y1", 0.67)

        elif region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1300
            
            self.modify_spam("fit", "x0", 0.68)
            self.modify_spam("fit", "x1", 0.78)
            self.modify_spam("fit", "y0", 0.35)
            self.modify_spam("fit", "y1", 0.42)  

class pt3l_plot(plot):
    def __init__(self):
        plot.__init__(self, "pt3l")
        self.titleX = r"#Sigma lepton #it{p}_{T} (GeV) "
        self.titleY = r"Events "
        self.titleY_binwidth = r"#LT Events / GeV #GT"
        self.binning = [0.0, 110.0, 185.0, 280.0, 400.0]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "3l" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.ymin_ratio = 0.6
            self.ymax_ratio = 1.5
            self.force_y_max = 180
            self.modify_spam("fit", "x0", 0.53)
            self.modify_spam("fit", "x1", 0.62)
            self.modify_spam("fit", "y0", 0.35)
            self.modify_spam("fit", "y1", 0.48)
            
class mll_plot(plot):

    def __init__(self):
        plot.__init__(self, "mll")
        self.titleX = r"m(l, l) (GeV) "
        self.titleY = r"Events "
        self.titleY_binwidth = r"#LT Events / GeV #GT"
        self.binning = [0.0, 110.0, 185.0, 280.0, 400.0]
              
    def modify(self, region):
        self.extralines = False
        self.auxbinning = []
        if "2lss" in region:
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1100
            
            self.modify_spam("fit", "x0", 0.58)
            self.modify_spam("fit", "x1", 0.68)
            self.modify_spam("fit", "y0", 0.35)
            self.modify_spam("fit", "y1", 0.42) 
        if region == "cr_nonprompt_oviedo":
            self.leg_x0, self.leg_y0 = 0.38, 0.57
            self.leg_ncolumns = 2
            self.force_y_max = 1100
            
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.85)
            self.modify_spam("fit", "y1", 0.72) 

class asymmetry_plot(plot):
    def __init__(self):
        plot.__init__(self, "asymmetry")
        self.titleX = "\\Delta y^{$\ell$}_{reco}\\text{ per category}"
        self.titleY = r"Events / bin"
              
    def modify(self, region):
        self.ratioleg_x0 = 0.16
        self.extralines = True
        self.auxbinning = ["A","B","C","D","E","F","G","H"]
        if "asymm" in region:
            #self.binlabels = ["-#infty", "", "", "+#infty","-#infty", "", "", "+#infty","-#infty", "", "", "+#infty","-#infty", "", "", "+#infty","-#infty", "", "", "+#infty","-#infty", "", "", "+#infty","-#infty", "", "", "+#infty","-#infty", "", "", "+#infty"]
            self.binlabels = ["0", "", "", "","4", "", "", "","8", "", "", "","12", "", "", "","16", "", "", "","20", "", "", "","24", "", "", "","28", "", "", "32"]
            self.ymin_ratio = 0.3
            self.ymax_ratio = 2.25
            #self.binlabels = ["0","4","8","12","16","20","24","28", "32"]
            self.leg_x0, self.leg_y0 = 0.38, 0.64
            self.leg_ncolumns = 2
            self.force_y_max = 80
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.3)
            self.modify_spam("fit", "y0", 0.85)
            self.modify_spam("fit", "y1", 0.72)
                         
plots = {
    "oviedo" : {
        # NP Validation region
        "cr_nonprompt" : {
            "lep1_pt" : lep1_pt_plot(),
            "lep1_eta" : lep1_eta_plot(),
            "lep2_pt" : lep2_pt_plot(),
            "lep2_eta" : lep2_eta_plot(),
            "jet1_pt" : jet1_pt_plot(),
            "jet1_eta" : jet1_eta_plot(),
            "jet2_pt" : jet2_pt_plot(),
            "jet2_eta" : jet2_eta_plot(),
            #"njets" : njets_plot(),
            "dR_ll" : dR_ll_plot(),
            "HT" : HT_plot(),
            "sum_2lss_pt" : sum_2lss_pt(),
            "mindr_lep1_jet25" : mindr_lep1_jet25_plot(),
            "mll" : mll_plot(),
            "nbjets" : nbjets_plot(),
            "max_eta" : max_eta_plot(),
        },
        "cr_3l" : {
            "cr_3l" : cr3l_plot(),
        },
        "cr_4l" : {
            "cr_4l" : cr4l_plot(),
        },
        "2lss" : {
            "lep1_pt" : lep1_pt_plot(),
            "lep1_eta" : lep1_eta_plot(),
            "lep2_pt" : lep2_pt_plot(),
            "lep2_eta" : lep2_eta_plot(),
            "jet1_pt" : jet1_pt_plot(),
            "jet1_eta" : jet1_eta_plot(),
            "jet2_pt" : jet2_pt_plot(),
            "jet2_eta" : jet2_eta_plot(),
            "deta_llss" : deta_llss_plot(),
            "njets_7bins" : njets_plot(), 
            "dR_ll" : dR_ll_plot(),
            "HT" : HT_plot(),
            "sum_2lss_pt" : sum_2lss_pt(),
            "mindr_lep1_jet25" : mindr_lep1_jet25_plot(),
            "mll" : mll_plot(),
            #"nbjets" : nbjets_plot(),
            "max_eta" : max_eta_plot(),
        },
        "3l" : {
            "pt3l" : pt3l_plot(),
            "HT" : HT_plot(),
        },
        "asymmetry" : {
            "nn" : asymmetry_plot()
        }
    },
    "ghent" : {
        "signalregion" : { 
            "lt" : lt_plot(),
            "HT" : HT_plot(),
            "lep1_pt" : lep1_pt_plot(),
            "lep2_pt" : lep2_pt_plot(),
            "jet1_pt" : jet1_pt_plot(),
            "jet2_pt" : jet2_pt_plot(),
            "njets_correctbins" : njets_plot(),
            "_eventBDT" : _eventBDT_plot(),
            "_eventBDTHT" : _eventBDTHT_plot(),
            "_eventBDTnJets" : _eventBDTnJets_plot(),
            "_eventBDTdRl1l2" : _eventBDTdRl1l2_plot(),
            #"_eventBDTdeltaEtaLeadingLeptonPair" : _eventBDTdeltaEtaLeadingLeptonPair_plot(),
            #"_eventBDTdRl1jet" : _eventBDTdRl1jet_plot(),
            #"_eventBDTdRl1bjet" : _eventBDTdRl1bjet_plot(),
            #"_eventBDTbjetAbsEtaLeading" : _eventBDTbjetAbsEtaLeading_plot(),
            #"_eventBDTbjetPtLeading" : _eventBDTbjetPtLeading_plot(),
            #"_eventBDTjetAbsEtaLeading" : _eventBDTjetAbsEtaLeading_plot(),
            #"_eventBDTjetAbsEtaSubLeading" : _eventBDTjetAbsEtaSubLeading_plot(),
            "_eventBDTjetPtLeading" : _eventBDTjetPtLeading_plot(),
            #"_eventBDTjetPtSubLeading" : _eventBDTjetPtSubLeading_plot(),
            #"_eventBDTleptonAbsEtaLeading" : _eventBDTleptonAbsEtaLeading_plot(),
            #"_eventBDTleptonAbsEtaSubLeading" : _eventBDTleptonAbsEtaSubLeading_plot(),
            #"_eventBDTleptonMaxEta" : _eventBDTleptonMaxEta_plot(),
            #"_eventBDTleptonPtLeading" : _eventBDTleptonPtLeading_plot(),
            #"_eventBDTleptonPtSubLeading" : _eventBDTleptonPtSubLeading_plot(),
            #"_eventBDTleptonPtSum" : _eventBDTleptonPtSum_plot(),
            #"_eventBDTM3l" : _eventBDTM3l_plot(),

            #"nmuons" : nmuons_plot(),
        },
        "sigreg" : {
            "_eventBDT" : _eventBDT_plot(),
        },
        "sigreg_withcut" : { 
            #"fineHT" : HT_plot(),
            #"HT" : HT_plot(),
            "njets" : njets_plot(),
            #"nbjets" : nbjets_plot(),
            #"nloosebjets" : nloosebjets_plot(),
        },
        "sigreg_withcut_onHT" : { 
            "fineHT" : HT_plot(),
            "HT" : HT_plot(),
        },
        "cfjetscontrolregion" : {
            "bdt" : bdt_plot(),
            "lep2_pt" : lep2_pt_plot(), 
            "lep2_eta" : lep2_eta_plot(),
            "lep1_pt" : lep1_pt_plot(),
            "lep1_eta" : lep1_eta_plot(), 
            "deepflavor" : deepflavor_plot(), 
        },
        "cfcontrolregion" : { 
            "njetsnbjets" : cr3l_plot(), 
            "bdt" : bdt_plot(), 
        },
        "trileptoncontrolregion" : { 
            "cr_3l" : cr3l_plot(), 
        },
        "fourleptoncontrolregion" : { 
            "cr_4l" : cr4l_plot(), 
        },
        "npcontrolregion" : {
            "bdt" : bdt_plot(),
            "lep2_pt" : lep2_pt_plot(),
            "lep2_eta" : lep2_eta_plot(), 
            "nbjets" : nbjets_plot(),
            "njets_correctbins" : njets_plot(),
        },
        "npctr_mm" : {
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_me" : { 
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_em" : { 
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_ee" : { 
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_2016pre" : { 
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_2016post" : { 
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_2017" : { 
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_2018" : { 
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        },
        "npctr_incl" : {
             "lep1_eta" : lep1_eta_plot(),
             "lep2_eta" : lep2_eta_plot(),
        }
    }
}
plots["binwidth"] = binwidth
plots["prefiterror"] = prefiterror
plots["prefitwithdata"] = prefitwithdata

plots["oviedo"]["needwidth"] = [
"jet2_eta",
"dR_ll",
"lep1_eta",
"mindr_lep1_jet25",
"deta_llss",
"jet2_pt",
"lep2_pt",
"jet1_pt",
"mll",
"lep2_eta",
"max_eta",
"HT","lt",
"jet1_eta",
"sum_2lss_pt",
"lep1_pt",
"pt3l"
]

plots["ghent"]["needwidth"] = [
]


plots["oviedo"]["2lss_plus"] = plots["oviedo"]["2lss"]
plots["oviedo"]["2lss_minus"] = plots["oviedo"]["2lss"]
