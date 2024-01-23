# Pressure image

import rhinoscriptsyntax as rs

def PRESSURE_IMAGE ():
    # layer
    rs.CurrentLayer("Pressure Image")
    
    # clean layer if needed
    objs = rs.ObjectsByLayer("Pressure Image")
    rs.DeleteObjects(objs)
    
    
    # =========================================================================
    
    # make sure top view is maximized
    persp_max = rs.IsViewMaximized("Top")
    if persp_max:
        rs.ZoomExtents()
    else:
        rs.MaximizeRestoreView(view = "Top")
        rs.ZoomExtents()
    
    # set display mode
    views = rs.ViewNames()
    modes = rs.ViewDisplayModes()
    viewtype = "Wireframe"
    #rs.EnableRedraw(False)
    if viewtype in modes:
        for view in views:
            rs.ViewDisplayMode(view, viewtype)
    
    
    # =========================================================================
    
    # user chooses file
    filename = rs.OpenFileName()
    
    # picture loaded
    picture = rs.AddPictureFrame(rs.WorldXYPlane(), filename, embed=False, 
                                 use_alpha=False, make_mesh=False)
    
    # zoom extents
    rs.ZoomExtents("Top")
    
    # align picture
    ## user select points
    hal_scan = rs.GetPoint("On the foot scan, pick the center of the hallux")
    heel_scan = rs.GetPoint("On the foot scan, pick the center of the heel")
    hal_press = rs.GetPoint("On the pressure image, pick the center of the hallux")
    heel_press = rs.GetPoint("On the pressure image, pick the center of the heel")
    
    ## move picture and points to hallux
    picture = rs.MoveObject(picture, [hal_scan[0] - hal_press[0],
                                      hal_scan[1] - hal_press[1],
                                      hal_scan[2] - hal_press[2]])
    heel_press = rs.MoveObject(heel_press, [hal_scan[0] - hal_press[0],
                                            hal_scan[1] - hal_press[1],
                                            hal_scan[2] - hal_press[2]])
    heel_press = rs.coerce3dpoint(heel_press)
    
    ## align pressure
    scan_axis = rs.VectorCreate(hal_scan, heel_scan)
    press_axis = rs.VectorCreate(hal_scan, heel_press)
    xform = rs.XformRotation3(press_axis, scan_axis, hal_scan)
    picture = rs.TransformObject(picture, xform)
    
    # set next layer
    rs.CurrentLayer("Pressure curve")
    rs.ZoomExtents()
    rs.MessageBox("Draw pressure contour behind forefoot")
    
    

PRESSURE_IMAGE()