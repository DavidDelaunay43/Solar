from typing import Union
from maya import cmds
from ...mayatools import tools


def create_offset_matrix(nodes: Union[str, list], reference_node: str) -> str:
    
    for node in tools.ensure_list(nodes):
        
        mult_matrix_node: str = f'offsetMatrix_{node}'
        cmds.createNode('multMatrix', name = mult_matrix_node)
        cmds.connectAttr(f'{node}.worldMatrix[0]', f'{mult_matrix_node}.matrixIn[0]')
        cmds.connectAttr(f'{reference_node}.worldInverseMatrix[0]', f'{mult_matrix_node}.matrixIn[1]')
        
        decompose_matrix_node: str = f'offsetDecompose_{node}'
        cmds.createNode('decomposeMatrix', name = decompose_matrix_node)
        cmds.connectAttr(f'{mult_matrix_node}.matrixSum', f'{decompose_matrix_node}.inputMatrix')
        
        return decompose_matrix_node
