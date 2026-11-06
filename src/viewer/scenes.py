import json, sys
G = '/spire/out/glb/'
LL = json.load(open('/home/claude/spire/out/lift_layout.json'))
def lift_parts(lid, cab_y, gates_open=0.0, show_cab=True):
    L = [l for l in LL['lifts'] if l['id'] == lid][0]; x, z = L['x'], L['z']; out = [dict(f=G + 'sp_lift%s_shaft.glb' % lid)]
    if show_cab:
        out.append(dict(f=G + 'sp_lift%s_cab.glb' % lid, p=[x, cab_y, z]))
        ci = L['cab']; s = 1 - 0.85 * gates_open
        out.append(dict(f=G + 'sp_lift_cgate.glb', p=[x + ci['gate_r'][0], cab_y, z + ci['gate_r'][2]], s=[s, 1, 1]))
        out.append(dict(f=G + 'sp_lift_cgate.glb', p=[x + ci['gate_l'][0], cab_y, z + ci['gate_l'][2]], ry=180, s=[s, 1, 1]))
        for g in ('gear_l', 'gear_r'): out.append(dict(f=G + 'sp_lift_cabgear.glb', p=[x + ci[g][0], cab_y + ci[g][1], z]))
        out.append(dict(f=G + 'sp_lift_lever.glb', p=[x + ci['lever'][0], cab_y + ci['lever'][1], z + ci['lever'][2]], ry=ci['lever_ry']))
    for po in L['portals']:
        s = 1 - 0.85 * (gates_open if abs(po['y'] - cab_y) < 0.1 else 0)
        out.append(dict(f=G + 'sp_lift_lgate.glb', p=po['gate_r'], s=[s, 1, 1]))
        out.append(dict(f=G + 'sp_lift_lgate.glb', p=po['gate_l'], ry=180, s=[s, 1, 1]))
        out.append(dict(f=G + 'sp_lift_needle.glb', p=po['needle'], s=po['needle_scale']))
        out.append(dict(f=G + 'sp_lift_call.glb', p=po['call']))
    sy = LL['sheave_y']
    out.append(dict(f=G + 'sp_lift_sheave.glb', p=L['sheave'])); out.append(dict(f=G + 'sp_lift_pinion.glb', p=L['pinion']))
    out.append(dict(f=G + 'sp_lift_gov.glb', p=L['governor']))
    hitch = cab_y + LL['hitch']; out.append(dict(f=G + 'sp_lift_cable.glb', p=L['cab_rope_top'], s=[1, sy - hitch, 1]))
    cw = sy - (LL['rope'] - (sy - hitch))
    out.append(dict(f=G + 'sp_lift_cable.glb', p=L['cw_rope_top'], s=[1, sy - cw, 1]))
    out.append(dict(f=G + 'sp_lift_cw.glb', p=[x, cw, z + LL['cw_z']]))
    return out
