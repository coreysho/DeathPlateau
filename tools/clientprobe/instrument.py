#!/usr/bin/env python3
"""Copy the client's sources and add draw counters to Model, because method380 eats exceptions.

Model.method380 wraps the whole draw in `try { ... } catch (Exception) {}`. A probe built on the
stock sources therefore reports a CRASH as geometry: the Infernal cape's crust layer threw on a
negative palette index a third of the way through being painted, and the pixel count that came
back read exactly like back-face culling. A winding "fix" was shipped on the strength of it.

So: never trust a number that came through that catch until this has printed what it caught.

    python3 instrument.py <javaclient dir> <output src dir>
    javac -nowarn -d dbuild $(find <output src dir> -name "*.java") clientprobe/Dbg.java

Model then carries four public static counters:

    CULLED[pri]  faces whose screen-space cross product was <= 0
    QUEUED[pri]  faces put in a depth bucket
    DRAWN[pri]   faces that reached the rasteriser
    BOOM         the first swallowed exception, or the first out-of-range depth bucket

Index 12 holds the faces of a model with no priorities at all. QUEUED well above DRAWN for one
priority is the signature this was written for.
"""
import os, shutil, sys

def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, out = sys.argv[1].rstrip('/\\') + '/src/main/java', sys.argv[2]
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(src, out)
    p = os.path.join(out, 'jagex2/dash3d/Model.java')
    s = open(p, encoding='utf-8', newline='').read()

    def sub(old, new):
        nonlocal s
        if s.count(old) != 1:
            raise SystemExit('Model.java: %d matches for %r - client changed, fix this script'
                             % (s.count(old), old[:60]))
        s = s.replace(old, new, 1)

    sub('public int field1221;',
        'public static int[] DRAWN = new int[13];\n\tpublic static int[] QUEUED = new int[13];\n'
        '\tpublic static int[] CULLED = new int[13];\n\tpublic static String BOOM = null;\n'
        '\tpublic int field1221;')
    sub('\tpublic void method383(int arg0) {',
        '\tpublic void method383(int arg0) {\n'
        '\t\tDRAWN[this.field1207 == null ? 12 : this.field1207[arg0]]++;')
    sub('\t\t\t\t\tif ((field1234[var32] - field1234[var31]) * (var33 - var34) '
        '- (field1234[var30] - field1234[var31]) * (var35 - var34) > 0) {',
        '\t\t\t\t\tint cullsign = (field1234[var32] - field1234[var31]) * (var33 - var34) '
        '- (field1234[var30] - field1234[var31]) * (var35 - var34);\n'
        '\t\t\t\t\tif (cullsign <= 0) { CULLED[this.field1207 == null ? 12 : this.field1207[var5]]++; }\n'
        '\t\t\t\t\tif (cullsign > 0) {')
    sub('''						int var37 = (field1235[var30] + field1235[var31] + field1235[var32]) / 3 + this.field1221;
						field1240[var37][field1239[var37]++] = var5;''',
        '''						int var37 = (field1235[var30] + field1235[var31] + field1235[var32]) / 3 + this.field1221;
						QUEUED[this.field1207 == null ? 12 : this.field1207[var5]]++;
						if (var37 < 0 || var37 >= field1240.length || field1239[var37] >= field1240[var37].length) { if (BOOM == null) BOOM = "depth bucket " + var37 + " of " + this.field1220; }
						field1240[var37][field1239[var37]++] = var5;''')
    sub('''		} catch (Exception var32) {
		}''',
        '''		} catch (Exception var32) {
			BOOM = "exception: " + var32;
		}''')
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('instrumented %s' % p)

main()
