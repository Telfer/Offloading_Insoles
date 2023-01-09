import rhinoscriptsyntax as rs


def moveLive():
    if rs.LastCommandResult() != 0:
        return
    while rs.LastCommandResult()== False:
        arrObject = rs.GetObjectEx("Select object to drag (Enter when done)",0,False,True)
        #idObject = arrObject[0]
        arrP = arrObject[3]
        rs.Command("_Move " + str(arrP) + " _Pause _EnterEnd", False)
    #return


def moveLive():
    while True:
        arrObject = rs.GetObjectEx("Select object to drag (Enter when done)",0,False,True)
        if arrObject is None: break
        idObject = arrObject[0]
        arrP = arrObject[3]
        rs.Command("_Move " + str(arrP) + " _Pause _EnterEnd", False)
        if rs.LastCommandResult() != 0:
            break
    return

ScanFE = rs.GetObject()
Insole_FE = rs.GetObject()

rs.Command("_Move SelID " + str(ScanFE) + " _Enter SelID " + str(Insole_FE) + " _Enter _Pause _EnterEnd", False)

#cyl = rs.AddCylinder(rs.WorldXYPlane(), 30, 30)
#arrObject = rs.GetObjectEx("Select object to drag (Enter when done)",0,False,True)
#print arrObject[3]
#idObject = arrObject[0]

#main()

#pt = rs.GetPoint()
 = rs.MoveObject(cyl, pt)

#x = rs.MessageBox("Scan position correct?", 3)
#
#while x == 7:
#    cyl = rs.MoveObject(cyl, pt * -1)
#    pt = rs.GetPoint()
#    cyl = rs.MoveObject(cyl, pt)
#    x = rs.MessageBox("Scan position correct?", 3)
#
#rs.MessageBox("Finished")
