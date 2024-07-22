import math
from maya import cmds

def create_proxy_geo(jnts: list, subdiv_axis: int = 8, subdiv_height: int = 2, axis=[1,0,0]) -> None:
    
    if not jnts:
        cmds.error('Nothing selected.')
    
    geos = []
    radius: float = 1.0
    next_jnts: list = jnts[1:]
    next_jnts.append(None)
    for jnt, next_jnt in zip(jnts, next_jnts):
        radius = math.dist(cmds.xform(jnt, q=1, t=1, ws=1), cmds.xform(next_jnt, q=1, t=1, ws=1)) if next_jnt != None else radius
        geo: str = f'proxyGeo_{jnt}'
        cmds.polyCylinder(name=geo, height=radius, axis=axis, subdivisionsAxis=subdiv_axis, subdivisionsHeight=subdiv_height, constructionHistory=False)
        cmds.matchTransform(geo, jnt, position=True, rotation=True)
        cmds.parent(geo, jnt)
        
        cmds.delete(f'{geo}.f[{subdiv_axis*subdiv_height}:{subdiv_axis*subdiv_height+1}]')
        geos.append(geo)
    
    skin_geo = cmds.polyUnite(geos, constructionHistory=False, mergeUVSets=1, name = 'proxyGeo')
    cmds.polyMergeVertex(skin_geo, distance=0.01, alwaysMergeTwoVertices=True, constructionHistory=False)
    cmds.skinCluster(jnts, skin_geo, maximumInfluences=5)
