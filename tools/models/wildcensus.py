"""Every npc spawned inside the build's own Wilderness rectangles, by name and count."""
import os, re, collections

W = r'C:\Users\short\AppData\Local\Temp\claude\C--LostCityServer\90f23383-3341-4f69-860b-813e181d2ba3\scratchpad'
MAPS = os.path.join(W, 'content', 'maps')

names = {}
for l in open(os.path.join(W, 'content', 'pack', 'npc.pack'), encoding='utf-8'):
    l = l.strip()
    if '=' in l:
        i, n = l.split('=', 1)
        names[int(i)] = n

# wilderness_zones.dbrow, in world coords. The surface rectangle runs to z 6399 but everything from
# z 3968 up is underground space the client's rectangle happens to cover, so the surface Wilderness
# proper is z 3520-3967.
SURFACE = (2944, 3391, 3520, 3967)
DUNGEON = (2944, 3391, 9920, 12799)

counts = collections.Counter()
where = collections.defaultdict(list)
for f in sorted(os.listdir(MAPS)):
    if not f.endswith('.jm2'):
        continue
    mx, mz = [int(v) for v in f[1:-4].split('_')]
    innpc = False
    for line in open(os.path.join(MAPS, f), encoding='utf-8'):
        line = line.strip()
        if line.startswith('===='):
            innpc = 'NPC' in line
            continue
        if not innpc or ':' not in line:
            continue
        coord, rest = line.split(':', 1)
        c = coord.split()
        if len(c) != 3:
            continue
        lvl, lx, lz = int(c[0]), int(c[1]), int(c[2])
        x, z = mx * 64 + lx, mz * 64 + lz
        nid = int(rest.split()[0])
        for x0, x1, z0, z1 in (SURFACE, DUNGEON):
            if x0 <= x <= x1 and z0 <= z <= z1:
                n = names.get(nid, f'#{nid}')
                counts[n] += 1
                if len(where[n]) < 3:
                    where[n].append(f'{x},{z}' + ('' if lvl == 0 else f' p{lvl}'))
                break

print(f'{len(counts)} distinct npcs, {sum(counts.values())} spawns\n')
for n, c in counts.most_common():
    print('%-34s %4d   %s' % (n, c, ', '.join(where[n])))
