import json; from scenes import *
D = json.loads(open('/home/claude/spire/out/spire.html').read().split('const D = ', 1)[1].split(';\n', 1)[0])
W = D['where']
npcs = [dict(f=G + 'npc_%s.glb' % k, p=v[:3], ry=v[3], anim=0, t=1.0) for k, v in W.items()]
base = [dict(f=G + n) for n in ('sp_shell.glb', 'sp_boardwalk.glb', 'sp_f1_lounge.glb', 'sp_f2_hall.glb', 'sp_f2_vault.glb', 'sp_f3_room.glb')]
lifts = lift_parts('A', 3.0, 1.0) + lift_parts('B', 53.0, 1.0)
LA = [l for l in LL['lifts'] if l['id'] == 'A'][0]; op = LA['cab']['operator']
npcs.append(dict(f=G + 'npc_operator.glb', p=[LA['x'] + op[0], 3.0 + op[1], op[2]], ry=LA['cab']['operator_ry'], anim=0, t=1.0))
ll = [[x, 9, z, 160, 22] for x in (-12, 0, 12) for z in (-12, 0, 12)]
sc = [dict(out='/home/claude/shots/npc_bar.png', models=base + lifts + npcs, cam=[-4, 5.2, -12.5], at=[-3, 4.3, -20], fov=60, night=True, lights=ll, exposure=1.2),
      dict(out='/home/claude/shots/npc_fire.png', models=base + lifts + npcs, cam=[-12, 5.0, 10], at=[-21, 4.2, 5], fov=60, night=True, lights=ll, exposure=1.2),
      dict(out='/home/claude/shots/npc_lift.png', models=base + lifts + npcs, cam=[9.0, 4.8, 8.5], at=[11.6, 4.3, 0.5], fov=55, night=True, lights=ll, exposure=1.2),
      dict(out='/home/claude/shots/npc_walk.png', models=base + npcs, cam=[-1, 2.2, 108], at=[2, 1.6, 100], fov=55),
      dict(out='/home/claude/shots/npc_cards.png', models=base + lifts + npcs, cam=[-6, 56, 10], at=[-1, 54.5, -6], fov=62, night=True, lights=[[x, 59, z, 120, 22] for x in (-12, 0, 12) for z in (-12, 0, 12)], exposure=1.2)]
json.dump(sc, open('s10.json', 'w'))
