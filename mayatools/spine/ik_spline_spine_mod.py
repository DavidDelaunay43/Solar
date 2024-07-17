from maya import cmds
import math
from .. import attribute, curve, display, offset
from .. import matrix
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
        cmds.joint(position=pos, orientation=[90,0,90], name=jnt)
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
    fk_controls = []
    for i in range(1, 4):
        y_pos = start_pos[1] + (length/4)*i
        pos = start_pos[0], y_pos, start_pos[2]
        ctrl = f'fk_spine_{i:02}'
        cmds.circle(name=ctrl, normal=[0,1,0], constructionHistory=False)
        cmds.setAttr(f'{ctrl}.t', *pos)
        display.color_node(ctrl, 'blue')
        fk_controls.append(ctrl)
    cmds.select(clear=True)
    cmds.parent(fk_controls[1], fk_controls[0])
    cmds.parent(fk_controls[2], fk_controls[1])
    offset.offset_parent_matrix(fk_controls)
    
    # create ik spline
    spline_curve: str = cmds.curve(degree=3, point=points, name = 'crv_spline_spine')
    start_jnt, end_jnt = bind_joints[0], bind_joints[-1]
    ik_spline, _ = cmds.ikHandle(solver = 'ikSplineSolver', startJoint = start_jnt, endEffector = end_jnt, curve = spline_curve, createCurve = False, name = 'ik_spline_spine')

    # create curve joints
    pelvis_jnt: str = 'jnt_crv_pelvis'
    chest_jnt: str = 'jnt_crv_chest'
    cmds.select(clear=True)
    cmds.joint(name=pelvis_jnt, position=start_pos)
    cmds.matchTransform(pelvis_jnt, bind_joints[0], position=True)
    cmds.select(clear=True)
    cmds.joint(name=chest_jnt, position=end_pos)
    cmds.matchTransform(chest_jnt, bind_joints[-1], position=True)
    offset.offset_parent_matrix([pelvis_jnt, chest_jnt])
    display.color_node([pelvis_jnt, chest_jnt], 'yellow')
    cmds.setAttr(f'{pelvis_jnt}.v', 0)
    cmds.setAttr(f'{chest_jnt}.v', 0)
    
    # skin curve
    cmds.skinCluster(pelvis_jnt, chest_jnt, spline_curve, maximumInfluences=3, name='skinCluster_curve_spine')
        
    # set twist
    cmds.setAttr(f'{ik_spline}.dTwistControlEnable', 1)
    cmds.setAttr(f'{ik_spline}.dWorldUpType', 4) # Object Rotation Up
    cmds.setAttr(f'{ik_spline}.dForwardAxis', 0) # Positive X
    cmds.setAttr(f'{ik_spline}.dWorldUpAxis', 3) # Positive Z
    cmds.setAttr(f'{ik_spline}.dWorldUpVector', 0.0, 0.0, -1.0)
    cmds.setAttr(f'{ik_spline}.dWorldUpVectorEnd', 0.0, 0.0, -1.0)
    cmds.connectAttr(f'{pelvis_jnt}.worldMatrix[0]', f'{ik_spline}.dWorldUpMatrix')
    cmds.connectAttr(f'{chest_jnt}.worldMatrix[0]', f'{ik_spline}.dWorldUpMatrixEnd')
    
    # create controls
    root_ctrl: str = curve.control('root', 'ctrl_root', 'orange')
    chest_ctrl: str = curve.control('root', 'ctrl_chest', 'orange')
    cmds.matchTransform(root_ctrl, pelvis_jnt, position=True)
    cmds.matchTransform(chest_ctrl, chest_jnt, position=True)
    cmds.parent(chest_ctrl, fk_controls[-1])
    cmds.parent(fk_controls[0], root_ctrl)
    cmds.parent(pelvis_jnt, root_ctrl)
    cmds.parent(chest_jnt, chest_ctrl)
    offset.offset_parent_matrix([pelvis_jnt, chest_jnt, chest_ctrl, root_ctrl, fk_controls[0]])
    
    # global scale
    loc_world: str = 'loc_world_spine'
    cmds.spaceLocator(name=loc_world)
    cmds.setAttr(f'{loc_world}.v', 0)
    decompose_matrix_scale: str = matrix.create_offset_matrix(root_ctrl, loc_world)
    
    # stretch
    attribute.sep_cb(chest_ctrl)
    cmds.addAttr(chest_ctrl, longName = 'stretch', niceName = 'Stretch', attributeType='float', min=0.0, max=1.0, dv=1.0, k=1)
    cmds.addAttr(chest_ctrl, longName = 'preserveVolume', niceName = 'Preserve Volume', attributeType='float', min=0.0, max=1.0, dv=1.0, k=1)
    
    curve_shape: str = cmds.listRelatives(spline_curve, shapes=True)[0]
    curve_info_node: str = cmds.createNode('curveInfo', name='curve_info_spine')
    cmds.connectAttr(f'{curve_shape}.worldSpace[0]', f'{curve_info_node}.inputCurve')
    default_length: float = round(cmds.getAttr(f'{curve_info_node}.arcLength'), 3)
    
    for i, jnt in enumerate(bind_joints, start=1):
        
        # x_value
        remap_node_x: str = cmds.createNode('remapValue', name=f'rm_{jnt}_scaleX')
        cmds.setAttr(f'{remap_node_x}.outputMin', 1.0)
        cmds.connectAttr(f'{chest_ctrl}.stretch', f'{remap_node_x}.inputValue')
        cmds.connectAttr(f'{remap_node_x}.outValue', f'{jnt}.sx')
        
        # power value
        '''
        1: 0.0
        2: 0.5
        3: 1.0
        4: 1.5
        5: 1.0
        6: 0.5
        7: 0.0
        '''
        power_value: float = (-1/6) * ((i-4)*(i-4)) + 1.5
        remap_node: str = cmds.createNode('remapValue', name=f'rm_{jnt}')
        cmds.setAttr(f'{remap_node}.outputMin', 0.5)
        cmds.setAttr(f'{remap_node}.outputMax', power_value)
        cmds.connectAttr(f'{chest_ctrl}.preserveVolume', f'{remap_node}.inputValue')
        
        # expression
        stretch_expression: str = f'''
        // Expression scale : {jnt}
        float $power_value = {remap_node}.outValue;
        float $global_scale = {decompose_matrix_scale}.outputScaleY;
        float $default_length = $global_scale * {default_length};
        float $arc_length = {curve_info_node}.arcLength;
        float $normalized_length = $arc_length/$default_length;
        float $sqrt_length = pow($normalized_length, $power_value);
        float $div_length = 1/($sqrt_length);
        float $scale_x = $normalized_length * $global_scale;
        float $scale = $div_length * $global_scale;
        {remap_node_x}.outputMax = $scale_x;
        {jnt}.sy = $scale;
        {jnt}.sz = $scale;
        '''.replace('  ', '')
        cmds.expression(string = stretch_expression, name=f'Exp_spine_stretch_{jnt}')
        
    # clean outliner
    xtra_spine_grp: str = 'Xtra_spine'
    cmds.group(bind_joints[0], spline_curve, loc_world, name = xtra_spine_grp)
    global_move_grp: str = 'GlobalMove_spine'
    cmds.group(ik_spline, root_ctrl, name = global_move_grp)
    spine_grp: str = 'Spine_grp'
    cmds.group(global_move_grp, xtra_spine_grp, name = spine_grp)
    cmds.select(clear=True)
