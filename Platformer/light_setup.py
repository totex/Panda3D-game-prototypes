from panda3d.core import PointLight, AmbientLight


def setup_point_light(render, pos):
    # adding Point light to the renderer
    plight = PointLight("plight")
    plight.setColor((1, 1, 1, 1))
    plnp = render.attachNewNode(plight)
    plnp.setPos(pos[0], pos[1], pos[2])
    # plight.setAttenuation((0, 0, 1))
    render.setLight(plnp)

    # adding Ambient light to the renderer
    alight = AmbientLight("alight")
    alight.setColor((0.08, 0.08, 0.08, 1))
    alnp = render.attachNewNode(alight)
    render.setLight(alnp)

