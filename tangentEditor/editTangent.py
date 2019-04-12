#!/usr/bin/env python
# -*- coding: utf-8 -*-

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