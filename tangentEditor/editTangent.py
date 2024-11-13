#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math

from maya import cmds

def get_angle(angle_type):
    if angle_type == 1 or angle_type == 2:
        tAngle = cmds.keyTangent(q=True,inAngle=True,)[0]
    elif angle_type == 3:
        tAngle = cmds.keyTangent(q=True,outAngle=True)[0]
    return round(tAngle,2)

def get_weight(angle_type):
    if angle_type == 1 or angle_type == 2:
        tWeight = cmds.keyTangent(q=True,inWeight=True)[0]
    elif angle_type == 3:
        tWeight = cmds.keyTangent(q=True,outWeight=True)[0]
    return round(tWeight,2)

def get_weightTangent():
    wTangent = cmds.keyTangent(query=True, weightedTangents = True )[0]
    return wTangent
    
def set_angle(angle_type,value):
    cmds.keyTangent( lock=False )
    if angle_type == 1:
        cmds.keyTangent(edit=True,absolute=True, inAngle= value, outAngle= value, an = 'keys' )
    elif angle_type == 2:
        cmds.keyTangent(edit=True,absolute=True, inAngle= value, an = 'keys' )
    elif angle_type == 3:
        cmds.keyTangent(edit=True,absolute=True, outAngle= value, an = 'keys' )
    cmds.keyTangent( lock=True )
    
def set_weight(angle_type,value):
    cmds.keyTangent( lock=False )
    if angle_type == 1:
        cmds.keyTangent(edit=True,absolute=True, inWeight = value, outWeight = value, an = 'keys' )
    elif angle_type == 2:
        cmds.keyTangent(edit=True,absolute=True, inWeight = value, an = 'keys' )
    elif angle_type == 3:
        cmds.keyTangent(edit=True,absolute=True, outWeight = value, an = 'keys' )
    cmds.keyTangent( lock=True )

def toggle_wieghtTangent(value):
    start_slider('tglWgt')
    if value:
        cmds.keyTangent(edit=True, weightedTangents = True, an = 'keys' )
        cmds.keyTangent(weightLock = False, an = 'keys' )
    else:
        cmds.keyTangent(edit=True, weightedTangents = False, an = 'keys' )
    close_slider('tglWgt')
        
def start_slider(name):
    cmds.undoInfo(openChunk=True,chunkName = name)
def close_slider(name):
    cmds.undoInfo(closeChunk=True,chunkName = name)

def check_animation():
    curveName = cmds.keyframe(q=True,sl=True,name=True)
    if curveName is not None:
        return cmds.objectType(curveName[0],isa='animCurve')
    return False
    
def set_angle_selected():
    start_slider("autoAngle")
    crvs = cmds.keyframe(q=True, selected=True, name=True)
    if not crvs:
        cmds.warning("Plese selected animation curves.")
        return
    for crv in crvs:
        selKeys = cmds.keyframe(crv, q=True, selected=True, indexValue=True)
        for key in selKeys:
            optimalAngle = optimal_calculate(crv, key)
            cmds.keyTangent(crv, e = True, time = (optimalAngle[3],optimalAngle[3]), outAngle = optimalAngle[0], inAngle = optimalAngle[0])
    close_slider("autoAngle")
        
def set_angle_io():
    start_slider("autoAngle")
    crvs = cmds.keyframe(q=True, selected=True, name=True)
    if not crvs:
        cmds.warning("Plese selected animation curves.")
        return
    for crv in crvs:
        selKeys = cmds.keyframe(crv, q=True, selected=True, indexValue=True)
        if len(selKeys) != 2:
            cmds.warning("Plese selected 2 keys from the {0}.".format(crv))
            continue
        optimalAngle = optimal_calculate(crv, selKeys[0], selKeys[1])
        endTime = cmds.keyframe(crv, q = True, timeChange = True)[selKeys[1]]
        cmds.keyTangent(crv, e = True, time = (optimalAngle[3],optimalAngle[3]), outAngle = optimalAngle[0], inAngle = optimalAngle[0])
        cmds.keyTangent(crv, e = True, time = (endTime,endTime), outAngle = optimalAngle[0], inAngle = optimalAngle[0])
    close_slider("autoAngle")
    
def set_angle_strain(angle_type,value):
    start_slider("autoAngle")
    crvs = cmds.keyframe(q=True, selected=True, name=True)
    cmds.keyTangent( lock=False )
    soften = 0.0005 * value ** 2 + 0.2
    for crv in crvs:
        selKeys = cmds.keyframe(crv, q=True, selected=True, indexValue=True)
        for key in selKeys:
            optimalAngle = optimal_calculate(crv, key, soften = soften)
            if angle_type == 1:
                cmds.keyTangent(crv, e = True, time = (optimalAngle[3],optimalAngle[3]), outAngle = optimalAngle[0], inAngle = optimalAngle[0])
            elif angle_type == 2:
                cmds.keyTangent(crv, e = True, time = (optimalAngle[3],optimalAngle[3]), inAngle = optimalAngle[0])
            elif angle_type == 3:
                cmds.keyTangent(crv, e = True, time = (optimalAngle[3],optimalAngle[3]), outAngle = optimalAngle[0])
    cmds.keyTangent( lock=True )
    
    close_slider("autoAngle")

def optimal_calculate(crv, idx, subIdx = None, preInf = -1, posInf = -1, soften = 1.4):
    keySize = cmds.keyframe(crv, q = True, keyframeCount = True)
    if preInf == -1:
        preInf = cmds.getAttr(crv+".preInfinity")
    if posInf == -1:
        posInf = cmds.getAttr(crv+".postInfinity")
        
    if subIdx is None:
        valCur = cmds.keyframe(crv, q = True, valueChange = True)[idx]
        timeCur = cmds.keyframe(crv, q = True, timeChange = True)[idx]
        
        valPre = valCur
        valNext = valCur
        timePre = timeCur
        timeNext = timeCur
        
        ang = 0
        inWgt = 10
        outWgt = 10
    
        if idx > 0:
            valPre = cmds.keyframe(crv, q=True, valueChange = True)[idx-1]
            timePre = cmds.keyframe(crv, q=True, timeChange = True)[idx-1]
        if idx < (keySize-1):
            valNext = cmds.keyframe(crv, q=True, valueChange = True)[idx+1]
            timeNext = cmds.keyframe(crv, q=True, timeChange = True)[idx+1]
        if idx == 0:
            if preInf <= 1:# constant or linear
                r = cmds.keyTangent(crv, q = True, time = (timeCur,timeCur), inAngle = True, inWeight = True, outWeight= True)
                r.append(timeCur)
                return r
            if preInf >= 3 :# cycle
                valPre = cmds.keyframe(crv, q=True, valueChange = True)[keySize-2]
                timePre = timeCur - (cmds.keyframe(crv, q=True, timeChange = True)[keySize-1] - cmds.keyframe(crv, q=True, timeChange = True)[keySize-2])
            if preInf == 4:# cycle offset 
                valPre = valCur - (cmds.keyframe(crv, q=True, valueChange = True)[keySize-1] - cmds.keyframe(crv, q=True, valueChange = True)[keySize-2])
            if preInf == 5:# oscillate
                valPre = valNext
                timePre = timeCur - (timeNext - timeCur)
                
        if idx == (keySize-1):
            if posInf <= 1:# constant or linear
                r = cmds.keyTangent(crv, q = True, time = (timeCur,timeCur), inAngle = True, inWeight = True, outWeight= True)
                r.append(timeCur)
                return r
            if posInf >= 3 :# cycle
                valNext = cmds.keyframe(crv, q=True, valueChange = True)[1]
                timeNext = timeCur + (cmds.keyframe(crv, q=True, timeChange = True)[1] - cmds.keyframe(crv, q=True, timeChange = True)[0])
            if posInf == 4:# cycle offset 
                valNext = valCur - (cmds.keyframe(crv, q=True, valueChange = True)[0] - cmds.keyframe(crv, q=True, valueChange = True)[1])
            if posInf == 5:# oscillate
                valNext = valPre
                timeNext = timeCur + (timeCur - timePre)
        
        valIn = valCur - valPre
        valOut = valNext - valCur
        timeIn = timeCur - timePre
        timeOut = timeNext - timeCur
    else:
        valFst = cmds.keyframe(crv, q = True, valueChange = True)[idx]
        valSnd = cmds.keyframe(crv, q = True, valueChange = True)[subIdx]
        timeFst = cmds.keyframe(crv, q = True, timeChange = True)[idx]
        timeSnd = cmds.keyframe(crv, q = True, timeChange = True)[subIdx]
    
        valPre = cmds.keyframe(crv, q=True, valueChange = True)[subIdx-1]
        timePre = cmds.keyframe(crv, q=True, timeChange = True)[subIdx-1]
        valNext = cmds.keyframe(crv, q=True, valueChange = True)[idx+1]
        timeNext = cmds.keyframe(crv, q=True, timeChange = True)[idx+1]
        
        valIn = valSnd - valPre
        valOut = valNext - valFst
        timeIn = timeSnd - timePre
        timeOut = timeNext - timeFst
        
        timeCur = timeFst
    
    tanIn = 0
    tanOut = 0
    
    if timeIn != 0:
        tanIn = valIn / timeIn
    if timeOut != 0:
        tanOut = valOut / timeOut
            
    powIn = 0.5
    powOut = 0.5
    
    if (tanIn + tanOut) != 0:
        powOut = ( abs( tanIn ) / ( abs( tanIn ) + abs(tanOut) ) )
        powIn = 1.0 - powOut
    
    powIn = soften * powIn
    powOut = soften * powOut
    
    newTan = (powIn * tanIn) + (powOut * tanOut)
    ang = math.atan(newTan) * 180 / math.pi
    
    isWeight = cmds.keyTangent(crv, q=True, weightedTangents = True)
    
    
    if isWeight:
        inWgt = abs(timeIn) / 2.0
        outWgt = abs(timeOut) / 2.0
    
    return [ang,inWgt,outWgt,timeCur]