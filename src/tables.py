"""(v42, owner: "these chairs are so short compared to the table") the Meshy card table came out 1.7 m tall at 2.3 m wide (its
own proportions), so the armchairs round it looked tiny. Card tables are squashed to CT_SY of their height (top ~1.15 m) and the
armchairs round them made CH_K bigger (and pulled back a little so they don't sink into the table). Works on sdeco-style
entries [file, x, y(model origin), z, ry, scale(, sy ratio)] in place; table entries get the sy ratio as their 7th value."""
import math
CT_SY, CH_K, CH_BACK = 0.68, 1.25, 0.12
T_MN, T_TOP, A_MN = 0.7066, 0.684, 0.9517          # card table: origin above floor / felt above origin (per unit scale); armchair origin

def resize(entries):
    tabs = [e for e in entries if e[0] == 'sp_m_cardtable' and len(e) < 7]
    for t in tabs:
        floor = t[2] - T_MN * t[5]; t[2] = round(floor + T_MN * t[5] * CT_SY, 3); t.append(CT_SY)
    for e in entries:
        if e[0] != 'sp_m_armchair' or len(e) > 6: continue
        near = [t for t in tabs if math.hypot(e[1] - t[1], e[3] - t[3]) < 2.0]
        if not near: continue
        t = near[0]; d = math.hypot(e[1] - t[1], e[3] - t[3]) or 1
        e[1] = round(e[1] + (e[1] - t[1]) / d * CH_BACK, 3); e[3] = round(e[3] + (e[3] - t[3]) / d * CH_BACK, 3)
        floor = e[2] - A_MN * e[5]; e[5] = round(e[5] * CH_K, 4); e[2] = round(floor + A_MN * e[5], 3); e.append(1.0)
    return tabs

def top(t):
    """felt height of a (resized) card table entry"""
    return t[2] + T_TOP * t[5] * (t[6] if len(t) > 6 else 1.0)
