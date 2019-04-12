import maya.cmds as cmds

def scaleKeys(type,scaleValue,pivTime,pivValue):
	keyTime = cmds.keyframe(q=True,sl=True,tc=True)
	if not keyTime:
		return
	if len(keyTime) == 1:
		key = cmds.keyframe(q=True,lsl=True,n=True)
		cmds.selectKey(clear=True)
		cmds.selectKey(key,add=True,k=True)
		keyTime = cmds.keyframe(q=True,sl=True,tc=True)
	keyValue = cmds.keyframe(q=True,sl=True,vc=True)
	lstTime = cmds.keyframe(q=True,lsl=True,tc=True)[0]
	lstValue = cmds.keyframe(q=True,lsl=True,vc=True)[0]
	if type == "up":
		if pivValue > (sum(keyValue)/len(keyValue)):
			scaleValue = scaleValue * -1
		cmds.scaleKey(ssk=True,ts=1,tp=pivTime,fs=1,fp=pivTime,vs=scaleValue,vp=pivValue)
	elif type == "down":
		if pivValue <= (sum(keyValue)/len(keyValue)):
			scaleValue = scaleValue * -1
		cmds.scaleKey(ssk=True,ts=1,tp=pivTime,fs=1,fp=pivTime,vs=scaleValue,vp=pivValue)
	elif type == "left":
		if pivTime <= (sum(keyTime)/len(keyTime)):
			scaleValue = scaleValue * -1
		cmds.scaleKey(ssk=True,ts=scaleValue,tp=pivTime,fs=scaleValue,fp=pivTime,vs=1,vp=pivValue)
	elif type == "right":
		if pivTime > (sum(keyTime)/len(keyTime)):
			scaleValue = scaleValue * -1
		cmds.scaleKey(ssk=True,ts=scaleValue,tp=pivTime,fs=scaleValue,fp=pivTime,vs=1,vp=pivValue)
	elif type == "avr":
		pivValue = (max(keyValue)+min(keyValue))/2
		scaleValue = -1
		cmds.scaleKey(ssk=True,ts=1,tp=pivTime,fs=1,fp=pivTime,vs=scaleValue,vp=pivValue)
	else:
		pass
		
def getKeyValue():
	return cmds.keyframe(q=True,lsl=True,vc=True,tc=True)