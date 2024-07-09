from maya import cmds
import math
from .. import curve, display, offset

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
    bind_01, bind_02, bind_03, bind_04, bind_05, bind_06, bind_07 = bind_joints 

    # create fk joints
    fk_joints = []
    for i in range(5):
        y_pos = start_pos[1] + (length/4)*i
        pos = start_pos[0], y_pos, start_pos[2]
        jnt = f'fk_spine_{i+1:02}'
        cmds.joint(position=pos, orientation=[0,0,0], name=jnt)
        cmds.setAttr(f'{jnt}.drawStyle', 2) # None
        display.color_node(jnt, 'blue')
        fk_joints.append(jnt)
    cmds.select(clear=True)
    for jnt in fk_joints:
        try:
            cmds.joint(jnt, edit=True, oj='yxz', sao='xup')
        except RuntimeError:
            cmds.joint(jnt, edit=True, oj='none')
    offset.offset_parent_matrix(fk_joints)
    curve.add_shape(['fk_spine_02', 'fk_spine_03', 'fk_spine_04'], normal=[0,1,0])
    
    # create ik spline
    spline_curve: str = cmds.curve(degree=3, point=points, name = 'crv_spline_spine')
    start_jnt, end_jnt = bind_joints[0], bind_joints[-1]
    ik_spline, _ = cmds.ikHandle(solver = 'ikSplineSolver', startJoint = start_jnt, endEffector = end_jnt, curve = spline_curve, createCurve = False, name = 'ik_spline_spine')

    # create curve joints
    pelvis_jnt: str = 'jnt_crv_pelvis'
    chest_jnt: str = 'jnt_crv_chest'
    cmds.select(clear=True)
    cmds.joint(name=pelvis_jnt, position=start_pos)
    cmds.matchTransform(pelvis_jnt, fk_joints[0])
    cmds.select(clear=True)
    cmds.joint(name=chest_jnt, position=end_pos)
    cmds.matchTransform(chest_jnt, fk_joints[-1])
    offset.offset_parent_matrix([pelvis_jnt, chest_jnt])
    display.color_node([pelvis_jnt, chest_jnt], 'yellow')
    cmds.setAttr(f'{pelvis_jnt}.v', 0)
    cmds.setAttr(f'{chest_jnt}.v', 0)
    cmds.skinCluster(pelvis_jnt, chest_jnt, spline_curve, maximumInfluences=3, name='skinCluster_curve_spine')

    # set twist
    cmds.setAttr(f'{ik_spline}.dTwistControlEnable', 1)
    cmds.setAttr(f'{ik_spline}.dWorldUpType', 4) # Object Rotation Up
    cmds.setAttr(f'{ik_spline}.dForwardAxis', 2) # Positive Y
    cmds.setAttr(f'{ik_spline}.dWorldUpAxis', 6) # Positive X
    cmds.connectAttr(f'{pelvis_jnt}.worldMatrix[0]', f'{ik_spline}.dWorldUpMatrix')
    cmds.connectAttr(f'{chest_jnt}.worldMatrix[0]', f'{ik_spline}.dWorldUpMatrixEnd')
    
    # create controls
    root_ctrl: str = curve.control('root', 'ctrl_root', 'orange')
    chest_ctrl: str = curve.control('root', 'ctrl_chest', 'orange')
    cmds.matchTransform(root_ctrl, fk_joints[0], position=True)
    cmds.matchTransform(chest_ctrl, fk_joints[-1], position=True)
    cmds.parent(chest_ctrl, fk_joints[-1])
    cmds.parent(fk_joints[0], root_ctrl)
    cmds.parent(pelvis_jnt, root_ctrl)
    cmds.parent(chest_jnt, chest_ctrl)
    offset.offset_parent_matrix([pelvis_jnt, chest_jnt, chest_ctrl, root_ctrl, fk_joints[0]])
    
    # stretch
    curve_shape: str = cmds.listRelatives(spline_curve, shapes=True)[0]
    curve_info_node: str = cmds.createNode('curveInfo', name='curve_info_spine')
    cmds.connectAttr(f'{curve_shape}.worldSpace[0]', f'{curve_info_node}.inputCurve')
    default_length: float = round(cmds.getAttr(f'{curve_info_node}.arcLength'), 3)
    
    remap_node_list = []
    for jnt in bind_joints:
        remap_node = cmds.createNode('remapValue', name=f'rm_{jnt}')
        cmds.setAttr(f'{remap_node}.inputMax', 10)
        cmds.setAttr(f'{remap_node}.outputMax', 10)
        cmds.connectAttr(f'{remap_node}.outValue', f'{jnt}.sy')
        cmds.connectAttr(f'{remap_node}.outValue', f'{jnt}.sz')
        remap_node_list.append(remap_node)
    rm_01, rm_02, rm_03, rm_04, rm_05, rm_06, rm_07 = remap_node_list 
    
    stretch_expression: str = f'''
    float $arc_length = {curve_info_node}.arcLength;
    float $normalized_length = $arc_length/{default_length};
    float $sqrt_length = pow($normalized_length, 0.5);
    float $div_length = 1/($sqrt_length);
    float $scale_x = $normalized_length;
    float $scale = $div_length;
    {bind_01}.sx = $scale_x;
    {bind_02}.sx = $scale_x;
    {bind_03}.sx = $scale_x;
    {bind_04}.sx = $scale_x;
    {bind_05}.sx = $scale_x;
    {bind_06}.sx = $scale_x;
    {bind_07}.sx = $scale_x;
    {rm_01}.inputValue = $scale;
    {rm_02}.inputValue = $scale;
    {rm_03}.inputValue = $scale;
    {rm_04}.inputValue = $scale;
    {rm_05}.inputValue = $scale;
    {rm_06}.inputValue = $scale;
    {rm_07}.inputValue = $scale;
    '''
    cmds.expression(string = stretch_expression, name='Exp_spine_stretch')
