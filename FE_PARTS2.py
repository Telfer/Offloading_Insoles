import rhinoscriptsyntax as rs

cyl = rs.AddCylinder(rs.WorldXYPlane(), 30, 30)

pt = rs.GetPoint()
cyl = rs.MoveObject(cyl, pt)

x = rs.MessageBox("Scan position correct?", 3)

while x == 7:
    cyl = rs.MoveObject(cyl, pt * -1)
    pt = rs.GetPoint()
    cyl = rs.MoveObject(cyl, pt)
    x = rs.MessageBox("Scan position correct?", 3)

rs.MessageBox("Finished")
