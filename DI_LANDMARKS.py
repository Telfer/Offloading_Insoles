import rhinoscriptsyntax as rs
import math

def DI_LANDMARKS():
    # helper function
    def landmark_point(layer, instruct):
        rs.CurrentLayer(layer)
        objs = rs.ObjectsByLayer(layer)
        rs.DeleteObjects(objs)
        x = rs.GetPointOnMesh(scan, instruct)
        rs.AddPoint(x)
    
    
    # =========================================================================
    
    # Set up layers
    rs.LayerVisible("Reference plane", False)
    
    
    # =========================================================================
    
    # Identify foot scan
    scan = rs.ObjectsByLayer("Position scan")[0]
    rs.UnselectAllObjects()
    
    
    # =========================================================================
    
    ## Maximize perspective view
    persp_max = rs.IsViewMaximized("Perspective")
    if persp_max:
        rs.ZoomExtents("Perspective")
        print "Perspective view maximised"
    else:
        rs.MaximizeRestoreView(view = "Perspective")
        rs.ZoomExtents("Perspective")
    
    
    # =========================================================================
    
    # layer management
    rs.CurrentLayer("Heel Medial")
    rs.LayerVisible("Pressure Image", False)
    
    
    # =========================================================================
    
    # Identify points to generate trim curves
    ## Select point on lateral side of heel
    landmark_point("Heel Lateral", "Identify point on lateral side of heel")
    
    ## Select point on center posterior of heel
    landmark_point("Heel Center", "Identify point on posterior of heel")
    
    ## Select point on medial side of heel
    landmark_point("Heel Medial", "Identify point on medial side of heel")
    
    ## Select point on lateral arch
    landmark_point("Arch Lateral", "Identify highest point on lateral arch")
    
    ## Select point on center lateral point of arch
    landmark_point("Arch Center Lateral", "Identify center lateral point of arch")
    
    ## Select point on center of arch
    landmark_point("Arch Center", "Identify center of arch")
    
    ## Select point on center medial point of arch
    landmark_point("Arch Center Medial", "Identify center medial point of arch")
    
    ## Select point on medial arch
    landmark_point("Arch Medial", "Identify highest point on medial arch")
    
    ## Select point on lateral side of distal metatarsal head 1
    landmark_point("MTPJ1", "Identify MTH1")
    
    ## Select point on lateral side of distal metatarsal head 2
    landmark_point("MTPJ2", "Identify MTH2")
    
    ## Select point on lateral side of distal metatarsal head 3
    landmark_point("MTPJ3", "Identify MTP3")
    
    ## Select point on lateral side of distal metatarsal head 4
    landmark_point("MTPJ4", "Identify MTP4")
    
    ## Select point on lateral side of distal metatarsal head 5
    landmark_point("MTPJ5", "Identify MTH5")
    
    
    # =========================================================================
    
    # Add additional variables
    rs.CurrentLayer("Heel Cup Height")
    objs = rs.ObjectsByLayer("Heel Cup Height")
    rs.DeleteObjects(objs)
    rs.AddPoint([0, 0, 15])
    
    
    # =========================================================================
    
    # prep for next step
    ## Make perspective view
    rs.MaximizeRestoreView("Perspective")
    rs.ZoomExtents()
    rs.ViewDisplayMode("Perspective", "Shaded")
    
    ## layer management
    rs.CurrentLayer("FO Build")
    rs.LayerVisible("Heel Cup Height", False)
    

DI_LANDMARKS()