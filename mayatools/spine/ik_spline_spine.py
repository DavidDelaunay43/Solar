from maya import cmds
import math
from .. import curve, display

def ik_spline_spine(start: str, end: str) -> None:
    
    cmds.select(clear=True)

    start_pos = cmds.xform(start, query=True, translation=True, worldSpace=True)
    end_pos = cmds.xform(end, query=True, translation=True, worldSpace=True)
    length = math.dist(start_pos, end_pos)

    # create bind joints
    bind_joints = []
    points = []
    for i in range(7):
        y_pos = start_pos[1] + (length/6)*i
        pos = start_pos[0], y_pos, start_pos[2]
        jnt = f'bind_spine_{i+1:02}'
        cmds.joint(position=pos, orientation=[-180,0,90], name=jnt)
        cmds.setAttr(f'{jnt}.displayLocalAxis', 1)
        display.color_node(jnt, 'white')
        bind_joints.append(jnt)
        points.append(pos)
    cmds.select(clear=True)
    for jnt in bind_joints:
        try:
            cmds.joint(jnt, edit=True, oj='xyz', sao='xup')
        except RuntimeError:
            cmds.joint(jnt, edit=True, oj='none')

    # create fk joints
    fk_joints = []
    for i in range(5):
        y_pos = start_pos[1] + (length/4)*i
        pos = start_pos[0], y_pos, start_pos[2]
        jnt = f'fk_spine_{i+1:02}'
        cmds.joint(position=pos, orientation=[-180,0,90], name=jnt)
        cmds.setAttr(f'{jnt}.displayLocalAxis', 1)
        display.color_node(jnt, 'blue')
        fk_joints.append(jnt)
    cmds.select(clear=True)
    for jnt in fk_joints:
        try:
            cmds.joint(jnt, edit=True, oj='xyz', sao='xup')
        except RuntimeError:
            cmds.joint(jnt, edit=True, oj='none')

    # create ik spline
    curve: str = cmds.curve(degree=3, point=points, name = 'crv_spline_spine')
    start_jnt, end_jnt = bind_joints[0], bind_joints[-1]
    ik_spline, _ = cmds.ikHandle(solver = 'ikSplineSolver', startJoint = start_jnt, endEffector = end_jnt, curve = curve, createCurve = False, name = 'ik_spline_spine')

    # create curve joints
    pelvis_jnt: str = 'jnt_crv_pelvis'
    chest_jnt: str = 'jnt_crv_chest'
    cmds.select(clear=True)
    cmds.joint(name=pelvis_jnt, position=start_pos)
    cmds.select(clear=True)
    cmds.joint(name=chest_jnt, position=end_pos)
    display.color_node([pelvis_jnt, chest_jnt], 'yellow')
    cmds.skinCluster(pelvis_jnt, chest_jnt, curve, maximumInfluences=3, name='skinCluster_curve_spine')

    # set twist
    cmds.setAttr(f'{ik_spline}.dTwistControlEnable', 1)
    cmds.setAttr(f'{ik_spline}.dWorldUpType', 4) # Object Rotation Up
    cmds.connectAttr(f'{pelvis_jnt}.worldMatrix[0]', f'{ik_spline}.dWorldUpMatrix')
    cmds.connectAttr(f'{chest_jnt}.worldMatrix[0]', f'{ik_spline}.dWorldUpMatrixEnd')
