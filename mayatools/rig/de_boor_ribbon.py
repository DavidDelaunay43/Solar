from maya import cmds


class CurveException(BaseException):
    """ Raised to indicate invalid curve parameters. """


def default_knots(count: int, degree: int = 3):
    """
    Gets a default knot vector for a given number of cvs and degrees.

    Args:
        count(int): The number of cvs. 
        degree(int): The curve degree. 

    Returns:
        list: A list of knot values.
    """
    knots = [0 for i in range(degree)] + [i for i in range(count - degree + 1)]
    knots += [count - degree for i in range(degree)]
    return [float(knot) for knot in knots]


def point_on_curve_weights(cvs: list, t: float, degree: int, knots: list = None) -> list:
    """
    Creates a mapping of cvs to curve weight values on a spline curve.
    While all cvs are required, only the cvs with non-zero weights will be returned.
    This function is based on de Boor's algorithm for evaluating splines and has been modified to consolidate weights.

    Args:
        cvs(list): A list of cvs, these are used for the return value.
        t(float): A parameter value. 
        degree(int): The curve dimensions. 
        knots(list): A list of knot values. 

    Returns:
        list: A list of control point, weight pairs.
    """

    order = degree + 1  # Our functions often use order instead of degree
    if len(cvs) <= degree:
        raise CurveException(f'Curves of degree {degree} require at least {degree+1} cvs')

    knots = knots or default_knots(count=len(cvs), degree=degree)  # Defaults to even knot distribution
    if len(knots) != len(cvs) + order:
        raise CurveException(f'Not enough knots provided. Curves with {len(cvs)} cvs must have a knot vector of length {len(cvs)+order}. '
                             f'Received a knot vector of length {len(knots)}: {knots}. '
                             f'Total knot count must equal len(cvs) + degree + 1.' % (len(cvs), len(cvs) + order,
                                                                                     len(knots), knots))

    # Convert cvs into hash-able indices
    _cvs = cvs
    cvs = [i for i in range(len(cvs))]

    # Remap the t value to the range of knot values.
    min = knots[order] - 1
    max = knots[len(knots) - 1 - order] + 1
    t = (t * (max - min)) + min

    # Determine which segment the t lies in
    segment = degree
    for index, knot in enumerate(knots[order:len(knots) - order]):
        if knot <= t:
            segment = index + order

    # Filter out cvs we won't be using
    cvs = [cvs[j + segment - degree] for j in range(0, degree + 1)]

    # Run a modified version of de Boors algorithm
    cvWeights = [{cv: 1.0} for cv in cvs]
    for r in range(1, degree + 1):
        for j in range(degree, r - 1, -1):
            right = j + 1 + segment - r
            left = j + segment - degree
            alpha = (t - knots[left]) / (knots[right] - knots[left])

            weights = {}
            for cv, weight in cvWeights[j].items():
                weights[cv] = weight * alpha

            for cv, weight in cvWeights[j - 1].items():
                if cv in weights:
                    weights[cv] += weight * (1 - alpha)
                else:
                    weights[cv] = weight * (1 - alpha)

            cvWeights[j] = weights

    cvWeights = cvWeights[degree]
    return [[_cvs[index], weight] for index, weight in cvWeights.items()]


def tangent_on_curve_weights(cvs: list, t: float, degree: int, knots: list = None) -> list:
    """
    Creates a mapping of cvs to curve tangent weight values.
    While all cvs are required, only the cvs with non-zero weights will be returned.

    Args:
        cvs(list): A list of cvs, these are used for the return value.
        t(float): A parameter value. 
        degree(int): The curve dimensions. 
        knots(list): A list of knot values. 

    Returns:
        list: A list of control point, weight pairs.
    """

    order = degree + 1  # Our functions often use order instead of degree
    if len(cvs) <= degree:
        raise CurveException(f'Curves of degree {degree} require at least {degree+1} cvs')

    knots = knots or default_knots(count=len(cvs), degree=degree)  # Defaults to even knot distribution
    if len(knots) != len(cvs) + order:
        raise CurveException(f'Not enough knots provided. Curves with {len(cvs)} cvs must have a knot vector of length {len(cvs)+order}. '
                             f'Received a knot vector of length {len(knots)}: {knots}. '
                             f'Total knot count must equal len(cvs) + degree + 1.')

    # Remap the t value to the range of knot values.
    min = knots[order] - 1
    max = knots[len(knots) - 1 - order] + 1
    t = (t * (max - min)) + min

    # Determine which segment the t lies in
    segment = degree
    for index, knot in enumerate(knots[order:len(knots) - order]):
        if knot <= t:
            segment = index + order

    # Convert cvs into hash-able indices
    _cvs = cvs
    cvs = [i for i in range(len(cvs))]

    # In order to find the tangent we need to find points on a lower degree curve
    degree = degree - 1
    qWeights = [{cv: 1.0} for cv in range(0, degree + 1)]

    # Get the DeBoor weights for this lower degree curve
    for r in range(1, degree + 1):
        for j in range(degree, r - 1, -1):
            right = j + 1 + segment - r
            left = j + segment - degree
            alpha = (t - knots[left]) / (knots[right] - knots[left])

            weights = {}
            for cv, weight in qWeights[j].items():
                weights[cv] = weight * alpha

            for cv, weight in qWeights[j - 1].items():
                if cv in weights:
                    weights[cv] += weight * (1 - alpha)
                else:
                    weights[cv] = weight * (1 - alpha)

            qWeights[j] = weights
    weights = qWeights[degree]

    # Take the lower order weights and match them to our actual cvs
    cvWeights = []
    for j in range(0, degree + 1):
        weight = weights[j]
        cv0 = j + segment - degree
        cv1 = j + segment - degree - 1
        alpha = weight * (degree + 1) / (knots[j + segment + 1] - knots[j + segment - degree])
        cvWeights.append([cvs[cv0], alpha])
        cvWeights.append([cvs[cv1], -alpha])

    return [[_cvs[index], weight] for index, weight in cvWeights]


def deboor_ribbon(controls_count: int, points_count: int, degree: int, length: float = 10.0, scale: bool = False) -> None:
    
    master_control: str = cmds.spaceLocator(name=f'ctrl_master_ribbon')[0]
    master_pick_matrix_node: str = cmds.createNode('pickMatrix', name=f'pickMtx_master_ribbon')
    cmds.connectAttr(f'{master_control}.worldMatrix[0]', f'{master_pick_matrix_node}.inputMatrix')
    cmds.setAttr(f'{master_pick_matrix_node}.useTranslate', False)
    cmds.setAttr(f'{master_pick_matrix_node}.useRotate', False)
    cmds.setAttr(f'{master_pick_matrix_node}.useShear', False)
    
    controls_world_matrices: list[str] = []
    
    for i in range(controls_count):
        control = cmds.circle(normal = [1, 0, 0], name = f'ctrl_ribbon_{i+1:02}', ch=False)[0]
        cmds.setAttr(f'{control}.offsetParentMatrix', (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, i*length*0.5, 0, 0, 1), type='matrix')
        cmds.parent(control, master_control)
        controls_world_matrices.append(f'{control}.worldMatrix[0]')
        
    for i in range(points_count):
        
        t: float = i/(float(points_count)-1)
        cmds.select(clear=True)
        joint: str = cmds.joint(name = f'bind_ribbon_{i+1:02}')
        cmds.select(clear=True)
        
        # Create the position matrix
        point_matrix_weights: list[list[str, float]] = point_on_curve_weights(cvs=controls_world_matrices, t=t, degree=degree)
        point_matrix_node: str = cmds.createNode('wtAddMatrix', name=f'pointMtx_{i+1:02}')
        for index, (matrix, weight) in enumerate(point_matrix_weights):
            cmds.connectAttr(matrix, f'{point_matrix_node}.wtMatrix[{index}].matrixIn')
            cmds.setAttr(f'{point_matrix_node}.wtMatrix[{index}].weightIn', weight)
            
        # Create the tangent matrix
        tangent_matrix_weights: list[list[str, float]] = tangent_on_curve_weights(cvs=controls_world_matrices, t=t, degree=degree)
        tangent_matrix_node: str = cmds.createNode('wtAddMatrix', name=f'tangentMtx_{i+1:02}')
        for index, (matrix, weight) in enumerate(tangent_matrix_weights):
            cmds.connectAttr(matrix, f'{tangent_matrix_node}.wtMatrix[{index}].matrixIn')
            cmds.setAttr(f'{tangent_matrix_node}.wtMatrix[{index}].weightIn', weight)
        
        # configure aim matrix node
        aim_matrix_node: str = cmds.createNode('aimMatrix', name=f'aimMtx_{i+1:02}')
        cmds.connectAttr(f'{point_matrix_node}.matrixSum', f'{aim_matrix_node}.inputMatrix')
        cmds.connectAttr(f'{tangent_matrix_node}.matrixSum', f'{aim_matrix_node}.primaryTargetMatrix')
        cmds.setAttr(f'{aim_matrix_node}.primaryMode', 1)
        cmds.setAttr(f'{aim_matrix_node}.primaryInputAxis', 1, 0, 0)
        cmds.setAttr(f'{aim_matrix_node}.secondaryInputAxis', 0, 1, 0)
        cmds.setAttr(f'{aim_matrix_node}.secondaryMode', 0)
        cmds.connectAttr(f'{aim_matrix_node}.outputMatrix', f'{joint}.offsetParentMatrix')
        
        # global scale
        mult_matrix_node: str = cmds.createNode('multMatrix', name=f'multMtx_{i+1:02}')
        cmds.connectAttr(f'{aim_matrix_node}.outputMatrix', f'{mult_matrix_node}.matrixIn[0]')
        cmds.connectAttr(f'{master_pick_matrix_node}.outputMatrix', f'{mult_matrix_node}.matrixIn[1]')
        
        if not scale:
            pick_matrix_node: str = cmds.createNode('pickMatrix', name=f'pickMtx_{i+1:02}')
            cmds.connectAttr(f'{mult_matrix_node}.matrixSum', f'{pick_matrix_node}.inputMatrix')
            cmds.setAttr(f'{pick_matrix_node}.useScale', False)
            cmds.setAttr(f'{pick_matrix_node}.useShear', False)
            cmds.connectAttr(f'{pick_matrix_node}.outputMatrix', f'{joint}.offsetParentMatrix', force=True)
        
    cmds.select(clear=True)
        

deboor_ribbon(controls_count=3, points_count=5, degree=2, length=5.0, scale = True)
