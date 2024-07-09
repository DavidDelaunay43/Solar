from maya import cmds

def create_spine_locators() -> None:
    
    locs = []
    for i in range(5):
        factor: float = i*2.5
        loc = cmds.spaceLocator()[0]
        cmds.setAttr(f'{loc}.ty', factor)
        locs.append(loc)
        
    loc_01, loc_02, loc_03, loc_04, loc_05 = locs
    cmds.parent(loc_02, loc_01)
    cmds.parent(loc_03, loc_02)
    cmds.parent(loc_04, loc_03)
    cmds.parent(loc_05, loc_01)
    
    cmds.setAttr(f'{loc_01}.tx', lock=True)
    cmds.setAttr(f'{loc_01}.rx', lock=True)
    cmds.setAttr(f'{loc_01}.ry', lock=True)
    cmds.setAttr(f'{loc_01}.rz', lock=True)
    cmds.setAttr(f'{loc_01}.sx', lock=True)
    cmds.setAttr(f'{loc_01}.sy', lock=True)
    cmds.setAttr(f'{loc_01}.sz', lock=True)
    
    for loc in (loc_02, loc_03, loc_04, loc_05):
        cmds.setAttr(f'{loc}.tx', lock=True)
        cmds.setAttr(f'{loc}.tz', lock=True)
        cmds.setAttr(f'{loc}.rx', lock=True)
        cmds.setAttr(f'{loc}.ry', lock=True)
        cmds.setAttr(f'{loc}.rz', lock=True)
        cmds.setAttr(f'{loc}.sx', lock=True)
        cmds.setAttr(f'{loc}.sy', lock=True)
        cmds.setAttr(f'{loc}.sz', lock=True)
        
    loc_01_shape: str = cmds.listRelatives(loc_01, shapes=True)[0]
    loc_05_shape: str = cmds.listRelatives(loc_05, shapes=True)[0]
    distance_between_node: str = cmds.createNode('distanceBetween')
    cmds.connectAttr(f'{loc_01_shape}.worldPosition[0]', f'{distance_between_node}.point1')
    cmds.connectAttr(f'{loc_05_shape}.worldPosition[0]', f'{distance_between_node}.point2')
    math_node: str = cmds.createNode('floatMath')
    cmds.setAttr(f'{math_node}.floatB', 4)
    cmds.setAttr(f'{math_node}.operation', 3) # divide
    cmds.connectAttr(f'{distance_between_node}.distance', f'{math_node}.floatA')
    cmds.connectAttr(f'{math_node}.outFloat', f'{loc_02}.ty')
    cmds.connectAttr(f'{math_node}.outFloat', f'{loc_03}.ty')
    cmds.connectAttr(f'{math_node}.outFloat', f'{loc_04}.ty')
    
    cmds.setAttr(f'{loc_01}.overrideEnabled', 1)
    cmds.setAttr(f'{loc_01}.overrideColor', 17)

create_spine_locators()
