import rhinoscriptsyntax as rs
import math
import Rhino

def DI_IMPORT():
    # Set up layers
    layerNames = rs.LayerNames()
    for layer in layerNames:
        if layer != "Default":
            rs.PurgeLayer(layer)
    rs.AddLayer("Original scan")
    rs.AddLayer("Reference plane", visible = False)
    rs.AddLayer("Side", visible = False)
    rs.AddLayer("Shoe_size", visible = False)
    rs.AddLayer("Position scan", visible = False)
    rs.AddLayer("Shoe outline", visible = False)
    rs.AddLayer("Pressure Image", visible = False)
    rs.AddLayer("Pressure curve", visible = False)
    rs.AddLayer("Heel Medial", color = (0, 255, 225), visible = False)
    rs.AddLayer("Heel Center", color = (0, 255, 225), visible = False)
    rs.AddLayer("Heel Lateral", color = (0, 255, 225), visible = False)
    rs.AddLayer("Heel Cup Height", color = (0, 255, 255), visible = False)
    rs.AddLayer("Base thickness", color = (0, 255, 255), visible = False)
    rs.AddLayer("Arch Medial", color = (0, 255, 225), visible = False)
    rs.AddLayer("Arch Center Medial", color = (0, 255, 225), visible = False)
    rs.AddLayer("Arch Center", color = (0, 255, 255), visible = False)
    rs.AddLayer("Arch Lateral", color = (0, 255, 225), visible = False)
    rs.AddLayer("Arch Center Lateral", color = (0, 255, 225), visible = False)
    rs.AddLayer("MTPJ1", color = (0, 255, 225), visible = False)
    rs.AddLayer("MTPJ2", color = (0, 255, 225), visible = False)
    rs.AddLayer("MTPJ3", color = (0, 255, 225), visible = False)
    rs.AddLayer("MTPJ4", color = (0, 255, 225), visible = False)
    rs.AddLayer("MTPJ5", color = (0, 255, 225), visible = False)
    rs.AddLayer("FO Build", visible = False)
    rs.CurrentLayer("Original scan")
    rs.DeleteLayer("Default")
    
    
    # =========================================================================
    
    # Import Scan
    ## Choose file
    fnm = rs.OpenFileName("Choose scanned file", ".stl|", None, None, None)
    
    ## Import stl
    commandString = ('-_import "' + fnm + '" _Enter')
    rs.Command(commandString)
    
    
    # =========================================================================
    
    # Copy to next layer
    scan = rs.ObjectsByLayer("Original scan")[0]
    scan2 = rs.CopyObject(scan)
    rs.ObjectLayer(scan2, layer = "Position scan")
    rs.CurrentLayer("Position scan")
    rs.LayerVisible("Original scan", False)
    
    
    # =========================================================================
    
    # Set display
    persp_max = rs.IsViewMaximized("Perspective")
    if persp_max:
        rs.ZoomExtents()
    else:
        rs.MaximizeRestoreView(view = "Perspective")
        rs.ZoomExtents()
    
    
    # =========================================================================
    
    # Info
    ## shoe size
    items = ["M9.0", "M9.5", "W8.5", "M10.0", "M10.5", "M11.0", "M11.5", "M12.0", 
             "M13.0", "W8.0", "W9.0", "W9.5"]
    shoe_size = rs.MultiListBox(items, "Select shoe size", "Shoe size")[0]
    shoe_size_index = items.index(shoe_size)
    rs.CurrentLayer("Shoe_size")
    rs.AddPoint(0, 0, shoe_size_index)
    
    ## base thickness
    rs.CurrentLayer("Base thickness")
    rs.AddPoint(0, 0, 7.0)
    
    
    # =========================================================================
    
    # Layer housekeeping
    rs.CurrentLayer("Position scan")
    rs.LayerVisible("Shoe_size", False)
    rs.LayerVisible("Heel Cup Height", False)
    rs.LayerVisible("Base thickness", False)
    
    
    ###########################################################################
    # =========================================================================
    # END OF SCRIPT
    # =========================================================================
    ###########################################################################

DI_IMPORT()