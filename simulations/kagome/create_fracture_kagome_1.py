# -*- coding: utf-8 -*-
"""
Create fracture speciment kagome input deck for ABAQUS.
Khanh Trinh 
Intelligent Systems Division
NASA Ames Research Center
"""

import sys
sys.path.append("../../src/python");
from  abqiface import *
from  createLatticeMesh import *

print('create kagome fracture specimen')

if __name__ == "__main__":
    
    # print the python version
    print("\n\nUsing python version:")
    print(sys.version)
    print(" \n")

    # set up file
    ############## file name INPUT ######
    geomFile = open('fracture_specimen_kagome_1.inp','w')
    geomFile.write('*HEADING\n')
    geomFile.write('kagome fracture specimen\n')

    # mesh inputs
    pitch = 2.
    panel1X = 10
    panel1Y = 4
    panel1Z = 2
    panel2X = 3
    panel2Y = 1
    panel2Z = panel1Z
    d2X = (panel1X-panel2X)*pitch
    d2Y = panel1Y*pitch
    d3Y = (panel1Y+panel2Y)*pitch
    
    numBeamsPerStrut = 1
    mesh = ABAQUS_mesh()
    length = 2.
    theta_d = 60.
    numX = 300
    numY = 600
    cX = 0
    cY = 0
    cZ = 0
    inclusionBox = [[60, 40,-1], [80, 80, 1]]    # define geometry inside this box
    noMergeBox = [[60, 61.3,-1], [71.5, 61.6, 1]]      # define crack inside this box
    
    mesh.addKagome1LatticeMesh(numX, numY, numBeamsPerStrut, cX, cY, cZ, length, theta_d, inclusionBox, noMergeBox)

    # write lattice nodes and elements
    geomFile.write('*NODE, NSET=lattice_nodes\n')
    nsetList = []
    for i in range (len(mesh.nodeList)):
        nodeId = i+1    # nodeId is ABAQUS id
        geomFile.write('%d, %f, %f, %f\n'%(nodeId, mesh.nodeList[i][0],mesh.nodeList[i][1],mesh.nodeList[i][2]))
        nsetList.append(nodeId)  # nodeId is ABAQUS id
        mesh.addNset('lattice_nodes', nsetList)

    geomFile.write('*ELEMENT, TYPE=B31, ELSET=BEAM\n')
    beamList = []
    for i in range (len(mesh.elemList)):
        geomFile.write('%d, %d, %d\n'%(i+1, mesh.elemList[i][0]+1,mesh.elemList[i][1]+1))
        beamList.append(i+1)
    mesh.addElset('BEAM',beamList)

    # write voxel beam section set
    ptop = [0,0,1]
    mid1 = [.5,.5,0]
    n1_s1 = [ptop[0]-mid1[0], ptop[1]-mid1[1],ptop[2]-mid1[2]]
    mid2 = [-.5,.5,0]
    n1_s2 = [ptop[0]-mid2[0], ptop[1]-mid2[1],ptop[2]-mid2[2]]
    n1_s3 = n1_s1
    n1_s4 = n1_s2
    py = [0,1,0]
    mid5 = [.5,0,.5]
    n1_s5 = [py[0]-mid5[0], py[1]-mid5[1],py[2]-mid5[2]]
    px = [1,0,0]
    mid6 = [0,.5,.5]
    n1_s6 = [px[0]-mid6[0], px[1]-mid6[1],px[2]-mid6[2]]
    mid7 = [-.5,0,.5]
    n1_s7 = [py[0]-mid7[0], py[1]-mid7[1],py[2]-mid7[2]]
    mid8 = [0,-.5,.5]
    n1_s8 = [px[0]-mid8[0], px[1]-mid8[1],px[2]-mid8[2]]
    n1_s9 = n1_s7
    n1_s10 = n1_s8
    n1_s11 = n1_s5
    n1_s12 = n1_s6
    n1 = [n1_s1,n1_s2,n1_s3,n1_s4,n1_s5,n1_s6,n1_s7,n1_s8,n1_s9,n1_s10,n1_s11,n1_s12]

    t1 = 0.072
    scale = 2.
    t2 = 0.072*scale

    for i in range(len(mesh.elsetList['superElementSectionList'])):
        name = 'voxel_strut'+str(i+1)
        n1X = n1[i][0]
        n1Y = n1[i][1]
        n1Z = n1[i][2]
        mesh.addElset(name,mesh.elsetList['superElementSectionList'][i])  # storing ABAAQUS id
        add_one_to_ID = 1
        mesh.writeElset(geomFile,name,add_one_to_ID) 
        geomFile.write('*BEAM SECTION, SECTION=RECTANGULAR, ELSET=%s, MATERIAL=ultem_2200_polyetherimide_E\n'%(name))
        geomFile.write(' %f, %f\n'%(t1,t2))
        geomFile.write(' %f, %f, %f\n'%(n1X, n1Y, n1Z))
       
    # materials definitions
    matlLib = Material_Library()
    matlLib.writeAbaqusMatlLines('ultem_2200_polyetherimide_E', geomFile)
    matlLib.writeAbaqusMatlLines('Aluminum_E', geomFile)

##    # BC definitions
    baseNodes = mesh.findNodes_coord_locations(1,40.7032)
    baseNodesName = 'baseNodes'
    mesh.addNset(baseNodesName,baseNodes)
    mesh.writeNset(geomFile, baseNodesName)
    geomFile.write('*BOUNDARY\n')
    geomFile.write(baseNodesName +',1,6,0.\n')
    movedNodes = mesh.findNodes_coord_locations(1,80.5404)
    movedNodesName = 'movedNodes'
    mesh.addNset(movedNodesName,movedNodes)
    mesh.writeNset(geomFile, movedNodesName)    

    geomFile.write('*STEP\n')
    geomFile.write('*FREQUENCY\n')
    geomFile.write('12\n')    # full run
    geomFile.write('*END STEP\n')
    geomFile.write('*STEP,INC=40000,NLGEOM\n')
    geomFile.write('*STATIC\n')
    geomFile.write('.1,1.,.001\n')    # full run
    geomFile.write('*BOUNDARY\n')
    geomFile.write(movedNodesName +',2,2,0.8\n')    
    geomFile.write('*END STEP\n')    
    geomFile.close()

    print('number of nodes: %d, number of elements: %d'%(len(mesh.nodeList), len(mesh.elemList)))

    print('end create kagome fracture specimen')    