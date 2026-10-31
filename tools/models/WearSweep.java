package jagex2.client;
import jagex2.config.*;
import jagex2.dash3d.*;
import jagex2.graphics.*;
import jagex2.io.*;
import java.nio.file.*; import java.util.*; import java.io.*;

// EVERY WORN MODEL, CHECKED FOR PAINTING ITSELF ONTO THE PLAYER UNDER IT.
//
// tools/models/wearpoke.py does this for one pair and costs a JVM start and 1,500 animation files
// per render, which is fine for one cape and hopeless for two thousand models. This is the same
// measurement with the loading done once: the client is set up, the reference kit is loaded, and
// then each model is merged with it, drawn twice - with and without itself - and the pixels that
// differ INSIDE the reference kit's own silhouette are counted. A model beside the player is not
// counted; a model on top of it is.
//
// WHAT A NON-ZERO NUMBER MEANS. Model.method382 paints the merged player a priority group at a
// time, 0 through 9, and a face's group is fixed in the model, so a face in a later group is
// painted over the body however far behind it is. Groups 10 and 11 are the exception - those are
// interleaved by real depth. So a count here is the model asking to be drawn in front of a body
// it is behind, which is what the max capes were doing on 29 October.
//
// A NUMBER HERE IS A CANDIDATE, NOT A VERDICT, and the hat slot is why. 475 of 501 hats score
// something, and moving them to the depth-sorted group breaks every one of them: a helmet's shell
// and the head inside it interleave, so depth at bucket granularity lets the HAIR THROUGH THE BACK
// OF THE HELMET. The fixed priority is what was holding the helmet shut.
//
// So the rule a change has to pass is two sweeps, not one: against the thing the model must still
// COVER, where the count has to stay 0, and against the thing it must not paint over, where the
// count is what is being fixed. On hats that leaves 489 of 501 disqualified and one worth 91
// pixels, which is why hats were measured and then left alone. It appeared to leave all 164
// capes, and that is the finding --selfdiff overturned.
//
// THE SECOND SWEEP IS THE BACK VIEW, and it is the one that has disqualified every slot tried
// since. Every slot was measured on 30 October and only the cape slot was changed:
//
//     slot    models  front px  back px  verdict
//     back       164    63,742  529,170  CHANGED AND THEN REVERTED - see below
//     hat        501         -        -  489 of 501 let the hair through the helmet
//     front      145     4,521   10,941  a stole's collar at the nape disappears
//     feet       119     2,648    3,315  tens of pixels either way, invisible
//     legs       299    60,522  113,844  all 299 disturbed; the boot clips the trouser
//     torso      308    12,864   59,599  the skirt comes through the coat
//
// A back figure larger than the front one is the slot saying no. The cape row first read
// "57,123 front, 0 back - all 164 now read zero", AND THAT ZERO WAS THE SWEEP MEASURING NOTHING.
// It compares a model as it ships against the same model forced to priority 10, and by then the
// models on disk were already at 10, so both renders were the same drawing. A sweep run after a
// change, over the changed files, cannot see the change. The real figures above are from the
// authored bytes, recovered out of git, and 152 of the 164 came out worse: from behind the armour
// under the cape is painted through the middle of it, which is a hole in the back of the cape.
// All 164 were put back; content/tools/capepriority_battery.py now holds every back-slot model's
// priorities so the next one has to be argued for by name.
//
// --selfdiff IS THE MEASUREMENT THAT CAN SEE THAT. Everything above looks INSIDE THE BODY'S
// SILHOUETTE at what the model does to the body. --selfdiff looks at the model itself over the
// whole frame: what it covers as authored against what it covers depth-sorted, reported as lost
// and gained. From the front a cape losing ground is the fix working; from the back it is the
// body coming through the cape. Give it <objdir> pointing at the AUTHORED bytes, never at the
// shipped ones, or it measures a drawing against itself exactly as the zero above did.
//
// lost AND gained ARE STILL ONLY A SILHOUETTE TEST, and the twelve capes that survived the figures
// above are what that costs. Is this pixel the model or is it not - so a face of the model beating
// ANOTHER FACE OF THE SAME MODEL is neither lost nor gained, and twelve capes came through reading
// clean while the infernal Max cape had 10,951 pixels of its own surface drawn by the wrong face:
// the dark straps and the cape's own backing winning over the lava sheet they were authored to sit
// under, which in game is black cracks down a cape. inner counts those. All twelve went back too.
//
//     model                            front  back   inner(back)
//     infernal max cape manwear        3,382   623        10,951
//     infernal max cape womanwear      2,998   158         8,795
//     fire max cape manwear            3,010   546         7,759
//     castlewars cloak saradomin w.    3,832   438           802
//
// A cape's own layering between groups 4, 5, 6 and 7 is load-bearing in the same way the fixed
// order is that holds a helmet shut. Three separate measurements were needed to see it, and each
// one only after the artefact had already shipped.
//
// --culprits IS WHAT TO DO INSTEAD, and it is the whole lesson of the three rows above: the model
// is not the unit of the fix, the face is. Only some of a cape's faces are painted over a body
// they are behind, and those are the ones the artefact pixels belong to - found by moving each
// face into group 10 alone and seeing which pixels go. On the infernal Max cape in Armadyl
// armour it is SEVENTEEN of 645 faces, and moving those seventeen takes the marks across the
// skirt to zero while the back view changes by 277 pixels of near-black hem.
//
//   --culprits <model>|list   the faces, with --yaws and --frames to sweep angles and poses
//   --trial <model> --faces   what one face list costs, from any angle
//   --trial <model> --probe   the same one face at a time
//   --trial <model> --variant <file>   the same for a rewritten copy of the model
//
// THE SET HAS TO BE NARROW. Taken over three kits, six angles and two poses the union is 57
// faces, and that version puts hairline cracks back down the cape from behind - 360 pixels of
// 1-px line along the strap edges, which is the same artefact in miniature. Collapsing the cape
// into the two depth-sorted groups, 10 for the sheet and 11 for the straps, is worse again:
// 11,000 to 17,000 inner pixels, because four authored layers do not fit in two. What ships is
// the union over the FRONT view only, where the artefact lives, checked as a whole across the
// grid: nothing gained, no more than 500 inner pixels, and every one of them looked at.
//
// --islands IS THE OTHER FAULT: mesh genuinely coming through mesh, rather than being painted over
// it. A patch of the model with no path to the background through its own pixels is surrounded on
// every side by the body, which is what a poke-through looks like and what an outline does not.
// Run it with --depth as well and draw order is taken out of the comparison, so what is left is
// the geometry.
//
// Swept on 30 October, after the capes and after two faults in this file were fixed (below):
// 26 of 2,135 models make an island at all, 171 pixels in total, and the ones that survive depth
// sorting come to 247 across 22 models. The largest single thing in the wardrobe is an amulet
// string crossing a neck at SIX PIXELS. There is no third class of fault here.
//
// The first numbers out of this said 61 models and 760 pixels, with hood linings through a face at
// 56 to 91 each. That was this file's own baseline: it hid the model by writing -1 into field1206,
// and on a merged kit that array is usually null, so ALLOCATING IT CHANGED HOW THE WHOLE KIT DREW -
// 16,139 pixels of body that had not moved. Faces are now hidden by pointing their three corners
// at one vertex, which has no area, fails method382's cross-product test and is culled, and leaves
// every other face and all the lighting exactly as they were.
//
// What makes the cape slot different is not its priorities - every slot splits them the same way -
// but that a cape is OUTSIDE the body. A helmet encloses a head and a stole is threaded through a
// collar, so for those the fixed order is load-bearing and depth has no way to know it.
//
//   java -cp javaclient/build/classes/java/main:. jagex2.client.WearSweep <dir> <objdir> <list> \
//        [--under a,b] [--frame N] [--yan N] [--dist N] [--size N] [--selfdiff]
//
// <objdir> may be content/models with names given as obj/<name> or idk/<name>, which is how a
// reference kit gets a head in it.
//
// <list> is one model name per line, optionally "name slot" - a torso is measured against the legs
// alone and legs against the torso alone, so a model is never measured against its own slot.
public class WearSweep {
    static int W, H;
    static int[] px;

    public static void main(String[] a) throws Exception {
        String dir = a[0], objdir = a[1], list = a[2];
        String under = "obj_saradomin_platebody_manwear,obj_saradomin_plateskirt_manwear";
        int frame = 2422, yan = 0, dist = 150, size = 700;
        boolean islands = false, depth = false;
        String bisect = null;
        boolean holes = false;
        boolean selfdiff = false;
        String culprits = null;
        String trial = null, trialFaces = "";
        String yaws = null, frameList = null;
        boolean probe = false;
        String variant = null, variantDir = null;
        for (int i = 3; i < a.length; i++) {
            switch (a[i]) {
                case "--under": under = a[++i]; break;
                case "--frame": frame = Integer.parseInt(a[++i]); break;
                case "--yan":   yan = Integer.parseInt(a[++i]); break;
                case "--dist":  dist = Integer.parseInt(a[++i]); break;
                case "--size":  size = Integer.parseInt(a[++i]); break;
                case "--islands": islands = true; break;
                // measure the islands on the depth-sorted drawing instead: what is left when draw
                // order is taken out of it is the mesh actually coming through
                case "--depth": depth = true; break;
                // name the faces of one model that make the island, in THIS process - see the
                // note on Pix3D.initColourTable below for why it cannot be done across two
                case "--bisect": bisect = a[++i]; break;
                // count the background showing THROUGH the dressed player instead: a hole is what
                // lets a cape be seen between an arm and a chestplate, and no amount of draw order
                // or priority will close one
                case "--holes": holes = true; break;
                // what the change does to the MODEL ITSELF, not to the body under it. The sweep
                // above only ever looked inside the body's silhouette, so a face the model loses
                // to its OWN mesh - against the floor, where a cape hem hangs clear of the body -
                // was outside everything it measured. That is the shape a hole in the back of a
                // cape has, and this is the measurement that can see one.
                case "--selfdiff": selfdiff = true; break;
                // name the FACES of one model that paint themselves onto the body, so those alone
                // can go to the depth-sorted group and the rest keep the layering the artist gave
                // them. Moving the whole model is what tore holes in the back of every cape.
                case "--culprits": culprits = a[++i]; break;
                // and check a face list that --culprits produced, from any angle: the set is only
                // worth having if the back view and the model's own layering survive it
                case "--trial": trial = a[++i]; break;
                case "--faces": trialFaces = a[++i]; break;
                // ONE FACE AT A TIME. A set that fixes the front can still cost something from
                // behind, and the face responsible is the one to leave out: a face is only worth
                // admitting if moving it alone costs nothing from the angles where the cape wins.
                case "--probe": probe = true; break;
                // measure a whole rewritten model rather than a face list: the two depth-sorted
                // groups are 10 AND 11, and 11 is drawn after 10, so a cape can keep its layering
                // and still be depth-sorted against the body - which no single group can do
                case "--variant": variant = a[++i]; break;
                // the same comparison for a whole list: <dir>/<name>.ob2 is the OTHER version of
                // each model in <list>, which is how a change to a hundred capes gets measured
                // without a hundred JVM starts
                case "--variantdir": variantDir = a[++i]; break;
                // a face is only a culprit from the angles and poses it is one in, so --culprits
                // and --trial sweep a set of each and report the union
                case "--yaws": yaws = a[++i]; break;
                case "--frames": frameList = a[++i]; break;
                default: throw new IllegalArgumentException("no such option: " + a[i]);
            }
        }

        World.lowMem = false; World3D.lowMem = false; Pix3D.lowMem = false; LocType.lowMem = false;
        Jagfile cfg = new Jagfile(Files.readAllBytes(Paths.get(dir, "config.jag")));
        ObjType.unpack(cfg); LocType.unpack(cfg); FloType.unpack(cfg); SeqType.unpack(cfg); VarbitType.unpack(cfg);
        Model.init(8, null);
        AnimFrame.init(70000);
        Path anims = Paths.get(dir, "anims");
        // sorted: see PlayerRender. Two .anim files can carry the same frame id and the last read
        // wins, so an unsorted listing poses the model differently from one run to the next.
        List<Path> animFiles = new ArrayList<>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(anims, "*.anim")) {
            for (Path p : ds) animFiles.add(p);
        }
        Collections.sort(animFiles);
        for (Path p : animFiles) {
            try { AnimFrame.method262(Files.readAllBytes(p)); } catch (Exception | Error e) { }
        }
        W = size; H = (int) (size * 1.4);
        px = new int[W * H];
        Pix2D.bind(W, H, px);
        Pix3D.unpackTextures(new Jagfile(Files.readAllBytes(Paths.get(dir, "textures.jag"))));
        Pix3D.initColourTable(0.8D);
        Pix3D.initPool(20);
        Pix3D.init3D(H, W);

        String[] underNames = under.split(",");
        // slot 0 is the model being measured; 1.. are the reference kit
        for (int i = 0; i < underNames.length; i++) {
            Model.method357(Files.readAllBytes(Paths.get(objdir, underNames[i] + ".ob2")), i + 1, (byte) 7);
        }

        int[] bare = new int[W * H];
        int[] asis = new int[W * H];

        int[] yanSet = split(yaws, yan), frameSet = split(frameList, frame);
        if (variantDir != null) {
            for (String line : Files.readAllLines(Paths.get(list))) {
                String nm = line.trim();
                if (nm.isEmpty() || nm.startsWith("#")) continue;
                String base = nm.substring(nm.lastIndexOf('/') + 1);
                Path other = Paths.get(variantDir, base + ".ob2");
                if (!Files.exists(other)) { System.out.println(nm + " NO-OTHER-VERSION"); continue; }
                try {
                    for (int fr : frameSet) for (int y : yanSet)
                        variantOf(nm, other.toString(), objdir, underNames, fr, y, dist);
                } catch (Exception | Error e) { System.out.println(nm + " THREW " + e); }
            }
            return;
        }
        if (variant != null) {
            for (int fr : frameSet) for (int y : yanSet) variantOf(trial, variant, objdir, underNames, fr, y, dist);
            return;
        }
        if (trial != null) {
            if (probe) {
                for (String t : trialFaces.split(",")) {
                    if (t.trim().isEmpty()) continue;
                    for (int fr : frameSet) for (int y : yanSet) trialOf(trial, t.trim(), objdir, underNames, fr, y, dist);
                }
            } else {
                for (int fr : frameSet) for (int y : yanSet) trialOf(trial, trialFaces, objdir, underNames, fr, y, dist);
            }
            return;
        }
        if (culprits != null) {
            // the list file names the models when --culprits is given "list", one per line
            List<String> names = new ArrayList<>();
            if (culprits.equals("list")) {
                for (String l : Files.readAllLines(Paths.get(list))) if (!l.trim().isEmpty()) names.add(l.trim());
            } else names.add(culprits);
            for (String nm : names) {
                TreeSet<Integer> union = new TreeSet<>();
                int worst = 0;
                for (int fr : frameSet) for (int y : yanSet) worst = Math.max(worst, culpritsOf(nm, objdir, underNames, fr, y, dist, union));
                StringBuilder sb = new StringBuilder();
                for (int f : union) { if (sb.length() > 0) sb.append(','); sb.append(f); }
                System.out.println("UNION " + nm + " " + union.size() + " faces: " + sb);
            }
            return;
        }
        if (bisect != null) {
            bisectOne(bisect, objdir, underNames, frame, yan, dist);
            return;
        }
        for (String line : Files.readAllLines(Paths.get(list))) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] f = line.split("\\s+");
            String name = f[0], slot = f.length > 1 ? f[1] : "";
            Path file = Paths.get(objdir, name + ".ob2");
            if (!Files.exists(file)) { System.out.println(name + " MISSING"); continue; }
            // never measure a model against its own slot - it would be replacing it, not clipping it
            List<Integer> kit = new ArrayList<>();
            for (int i = 0; i < underNames.length; i++) {
                if (slot.equals("torso") && underNames[i].contains("platebody")) continue;
                if ((slot.equals("legs")) && (underNames[i].contains("plateskirt") || underNames[i].contains("platelegs"))) continue;
                kit.add(i + 1);
            }
            if (kit.isEmpty()) { System.out.println(name + " 0 no-reference"); continue; }
            try {
                Model.method357(Files.readAllBytes(file), 0, (byte) 7);
                // THE KIT ALONE STILL HAS THE MODEL MERGED INTO IT, with its faces switched off.
                // Leaving it out entirely changes the merge - method362 welds vertices by position
                // and calculateNormals averages across what it welded - so the body's own SHADING
                // moves, and a with-against-without comparison counts that as the model.
                draw(kit, 0, frame, yan, dist, false, true);           // the kit, model hidden
                System.arraycopy(px, 0, bare, 0, px.length);
                draw(kit, 0, frame, yan, dist, false, false);          // as the model asks to be drawn
                System.arraycopy(px, 0, asis, 0, px.length);
                draw(kit, 0, frame, yan, dist, true, false);           // and as depth says it should be
                // THE MEASUREMENT. Not "does it cover the body" - a pauldron covers the body and is
                // meant to. It is "where does the model's own priority group disagree with its real
                // depth", which is the only thing that can put a model in front of a body it is
                // behind. Counted inside the body's own silhouette, so the model's outline against
                // the floor is not counted.
                if (selfdiff) {
                    // A = what the model covers as authored, B = what it covers depth-sorted.
                    // A \ B is ground the model has GIVEN UP, which is the only way the change
                    // can take a piece out of it; B \ A is ground it has taken.
                    int lost = 0, gained = 0, lx0 = W, ly0 = H, lx1 = -1, ly1 = -1;
                    for (int i = 0; i < px.length; i++) {
                        boolean wasMine = asis[i] != bare[i], nowMine = px[i] != bare[i];
                        if (wasMine && !nowMine) {
                            lost++;
                            int x = i % W, y = i / W;
                            if (x < lx0) lx0 = x;
                            if (y < ly0) ly0 = y;
                            if (x > lx1) lx1 = x;
                            if (y > ly1) ly1 = y;
                        } else if (nowMine && !wasMine) {
                            gained++;
                        }
                    }
                    // AND THE PIXELS THAT ARE STILL THE MODEL BUT NO LONGER THE SAME FACE.
                    // lost and gained are a silhouette test - is this pixel the model or not -
                    // so a face of the model beating ANOTHER FACE OF THE SAME MODEL registers as
                    // neither. That is what the black cracks down the infernal Max cape were: the
                    // dark straps and the cape's own backing winning over the lava sheet they
                    // were authored to sit under. A model whose own layering is load-bearing
                    // fails here and nowhere else.
                    int inner = 0;
                    for (int i = 0; i < px.length; i++) {
                        if (asis[i] != bare[i] && px[i] != bare[i] && px[i] != asis[i]) inner++;
                    }
                    System.out.println(name + " lost=" + lost + " gained=" + gained + " inner=" + inner
                        + " selfhole=" + (islands(asis, bare) + "->" + islands(px, bare))
                        + " bbox=" + (lost == 0 ? "-" : lx0 + "," + ly0 + ".." + lx1 + "," + ly1));
                } else if (holes) {
                    System.out.println(name + " " + holes(asis) + " " + visible(asis, bare));
                } else if (islands) {
                    int[] look = depth ? px : asis;
                    System.out.println(name + " " + islands(look, bare) + " " + visible(look, bare));
                } else {
                    int over = 0, body = 0;
                    for (int i = 0; i < px.length; i++) {
                        if (bare[i] != 0x141414) {
                            body++;
                            if (asis[i] != px[i]) over++;
                        }
                    }
                    System.out.println(name + " " + over + " " + body);
                }
            } catch (Exception | Error e) {
                System.out.println(name + " THREW " + e);
            }
        }
    }


    /**
     * The faces of one model that are painted over a body they are BEHIND.
     *
     * Moving a whole cape to the depth-sorted group fixes these and breaks everything else: the
     * body comes through the back of the cape, and the cape's own layering between groups 4, 5, 6
     * and 7 collapses into cracks. Only some of its faces are at fault, and this names them.
     *
     * The artefact pixels are the ones the model wins as authored and LOSES once depth decides -
     * so depth says the body is in front there and the fixed priority was overruling it. Each face
     * is then put in group 10 on its own, and the artefact pixels that go are that face's.
     */
    static int[] split(String csv, int fallback) {
        if (csv == null) return new int[] { fallback };
        String[] t = csv.split(",");
        int[] out = new int[t.length];
        for (int i = 0; i < t.length; i++) out[i] = Integer.parseInt(t[i].trim());
        return out;
    }

    static int culpritsOf(String name, String objdir, String[] underNames, int frame, int yan, int dist, TreeSet<Integer> union) throws Exception {
        List<Integer> kit = new ArrayList<>();
        for (int i = 0; i < underNames.length; i++) kit.add(i + 1);
        Model.method357(Files.readAllBytes(Paths.get(objdir, name + ".ob2")), 0, (byte) 7);
        int nf = Model.tryGet(0).field1199;

        int[] bare = new int[W * H], asis = new int[W * H];
        draw(kit, 0, frame, yan, dist, false, true);
        System.arraycopy(px, 0, bare, 0, px.length);
        draw(kit, 0, frame, yan, dist, false, false);
        System.arraycopy(px, 0, asis, 0, px.length);
        draw(kit, 0, frame, yan, dist, true, false);            // every face depth-sorted

        List<Integer> bad = new ArrayList<>();
        for (int i = 0; i < px.length; i++) {
            if (asis[i] != bare[i] && px[i] == bare[i]) bad.add(i);
        }
        int[] spot = new int[bad.size()];
        for (int i = 0; i < spot.length; i++) spot[i] = bad.get(i);
        System.out.println(name + " frame=" + frame + " yan=" + yan + ": " + nf + " faces, "
            + spot.length + " pixels painted over a body in front of them");
        if (spot.length == 0) return 0;

        StringBuilder list = new StringBuilder();
        int claimed = 0, n = 0;
        for (int f = 0; f < nf; f++) {
            drawRepri(kit, frame, yan, dist, f, f);
            int fixed = 0;
            for (int i : spot) if (px[i] == bare[i]) fixed++;
            if (fixed > 0) {
                claimed += fixed; n++;
                union.add(f);
                if (list.length() > 0) list.append(',');
                list.append(f);
            }
        }
        System.out.println("  " + n + " of " + nf + " faces account for " + claimed + " of " + spot.length + " pixels: " + list);

        // and what that subset actually costs, measured the same three ways as --selfdiff
        int[] sub = new int[n];
        int k = 0;
        for (String t : list.toString().split(",")) if (!t.isEmpty()) sub[k++] = Integer.parseInt(t);
        drawRepriSet(kit, frame, yan, dist, sub);
        int left = 0, lost = 0, inner = 0;
        for (int i = 0; i < px.length; i++) {
            boolean wasMine = asis[i] != bare[i], nowMine = px[i] != bare[i];
            if (wasMine && !nowMine) lost++;
            if (wasMine && nowMine && px[i] != asis[i]) inner++;
        }
        for (int i : spot) if (px[i] != bare[i]) left++;
        System.out.println("  with only those faces at 10: " + left + " artefact px left, "
            + lost + " px of the model given up, " + inner + " px of it drawn by a different face");
        return spot.length;
    }

    /** The same three numbers for a rewritten copy of the model, plus what is left of the artefact. */
    static void variantOf(String name, String file, String objdir, String[] underNames, int frame, int yan, int dist) throws Exception {
        List<Integer> kit = new ArrayList<>();
        for (int i = 0; i < underNames.length; i++) kit.add(i + 1);
        int[] bare = new int[W * H], asis = new int[W * H], dpth = new int[W * H];
        Model.method357(Files.readAllBytes(Paths.get(objdir, name + ".ob2")), 0, (byte) 7);
        draw(kit, 0, frame, yan, dist, false, true);
        System.arraycopy(px, 0, bare, 0, px.length);
        draw(kit, 0, frame, yan, dist, false, false);
        System.arraycopy(px, 0, asis, 0, px.length);
        draw(kit, 0, frame, yan, dist, true, false);
        System.arraycopy(px, 0, dpth, 0, px.length);

        Model.method357(Files.readAllBytes(Paths.get(file)), 0, (byte) 7);
        draw(kit, 0, frame, yan, dist, false, false);

        int lost = 0, gained = 0, inner = 0, artefact = 0, left = 0;
        for (int i = 0; i < px.length; i++) {
            boolean wasMine = asis[i] != bare[i], nowMine = px[i] != bare[i];
            if (wasMine && !nowMine) lost++;
            else if (nowMine && !wasMine) gained++;
            else if (wasMine && px[i] != asis[i]) inner++;
            if (wasMine && dpth[i] == bare[i]) { artefact++; if (nowMine) left++; }
        }
        System.out.println(name + " frame=" + frame + " yan=" + yan
            + " artefact=" + left + "/" + artefact + " lost=" + lost + " gained=" + gained + " inner=" + inner);
    }

    /** What one face list costs from one angle: the three numbers --selfdiff reports. */
    static void trialOf(String name, String faces, String objdir, String[] underNames, int frame, int yan, int dist) throws Exception {
        List<Integer> kit = new ArrayList<>();
        for (int i = 0; i < underNames.length; i++) kit.add(i + 1);
        Model.method357(Files.readAllBytes(Paths.get(objdir, name + ".ob2")), 0, (byte) 7);
        int[] bare = new int[W * H], asis = new int[W * H];
        draw(kit, 0, frame, yan, dist, false, true);
        System.arraycopy(px, 0, bare, 0, px.length);
        draw(kit, 0, frame, yan, dist, false, false);
        System.arraycopy(px, 0, asis, 0, px.length);

        List<Integer> f = new ArrayList<>();
        for (String t : faces.split(",")) if (!t.trim().isEmpty()) f.add(Integer.parseInt(t.trim()));
        int[] set = new int[f.size()];
        for (int i = 0; i < set.length; i++) set[i] = f.get(i);
        drawRepriSet(kit, frame, yan, dist, set);

        int lost = 0, gained = 0, inner = 0;
        for (int i = 0; i < px.length; i++) {
            boolean wasMine = asis[i] != bare[i], nowMine = px[i] != bare[i];
            if (wasMine && !nowMine) lost++;
            else if (nowMine && !wasMine) gained++;
            else if (wasMine && px[i] != asis[i]) inner++;
        }
        System.out.println(name + " frame=" + frame + " yan=" + yan
            + (set.length == 1 ? " face=" + set[0] : " faces=" + set.length)
            + " lost=" + lost + " gained=" + gained + " inner=" + inner);
    }

    /** Draw the kit with faces lo..hi of the model under test moved to the depth-sorted group. */
    static void drawRepri(List<Integer> kit, int frame, int yan, int dist, int lo, int hi) {
        int[] f = new int[hi - lo + 1];
        for (int i = 0; i < f.length; i++) f[i] = lo + i;
        drawRepriSet(kit, frame, yan, dist, f);
    }

    static void drawRepriSet(List<Integer> kit, int frame, int yan, int dist, int[] faces) {
        Arrays.fill(px, 0x141414);
        Model[] parts = new Model[kit.size() + 1];
        int n = 0;
        parts[n++] = Model.tryGet(0);
        for (int id : kit) parts[n++] = Model.tryGet(id);
        Model body = new Model(n, parts, (byte) -89);
        if (body.field1207 == null) {
            body.field1207 = new int[body.field1199];
            Arrays.fill(body.field1207, body.field1210 < 0 ? 0 : body.field1210);
        }
        for (int f : faces) body.field1207[f] = 10;
        body.createLabelReferences();
        body.calculateNormals(64, 850, -30, -50, -30, true);
        Model out = body;
        if (frame > 0 && !AnimFrame.isNull(frame)) {
            out = Model.field1190;
            out.method361(false, body);
            out.applyTransform(frame);
            out.method363();
            out.field1226 = null;
            out.field1225 = null;
        }
        out.method381(yan, 0, 65536, 0, 65536, 0, 85, dist, 0);
    }

    /**
     * Which faces of one model make the island, found by collapsing ranges of them until it goes.
     *
     * IN ONE PROCESS, DELIBERATELY. Pix3D.initColourTable jitters the palette by a random amount
     * on every startup - `arg0 + (Math.random() * 0.03 - 0.015)` - which is the client being the
     * client, and means two runs of the same render differ by ten thousand pixels. Anything that
     * compares one drawing against another has to make both of them without leaving the JVM.
     */
    static void bisectOne(String name, String objdir, String[] underNames, int frame, int yan, int dist) throws Exception {
        List<Integer> kit = new ArrayList<>();
        for (int i = 0; i < underNames.length; i++) kit.add(i + 1);
        Model.method357(Files.readAllBytes(Paths.get(objdir, name + ".ob2")), 0, (byte) 7);
        int nf = Model.tryGet(0).field1199;
        int[] base = new int[W * H];
        draw(kit, 0, frame, yan, dist, false, true);
        System.arraycopy(px, 0, base, 0, px.length);

        List<int[]> hidden = new ArrayList<>();
        int total = islandsWith(kit, hidden, nf, frame, yan, dist, base);
        System.out.println(name + " " + total + " island px over " + nf + " faces");
        while (total > 0 && hidden.size() < 24) {
            int lo = 0, hi = nf - 1;
            hidden.add(new int[] { lo, hi });
            boolean helps = islandsWith(kit, hidden, nf, frame, yan, dist, base) < total;
            hidden.remove(hidden.size() - 1);
            if (!helps) break;
            while (lo < hi) {
                int mid = (lo + hi) / 2;
                hidden.add(new int[] { lo, mid });
                boolean half = islandsWith(kit, hidden, nf, frame, yan, dist, base) < total;
                hidden.remove(hidden.size() - 1);
                if (half) hi = mid; else lo = mid + 1;
            }
            hidden.add(new int[] { lo, lo });
            int after = islandsWith(kit, hidden, nf, frame, yan, dist, base);
            if (after >= total) { System.out.println("  no single face accounts for the last " + total); break; }
            System.out.println("  face " + lo + "  -" + (total - after) + " px  (" + after + " left)");
            total = after;
        }
        StringBuilder sb = new StringBuilder();
        for (int[] h : hidden) { if (sb.length() > 0) sb.append(','); sb.append(h[0]); }
        System.out.println("faces: " + sb);
    }

    static int islandsWith(List<Integer> kit, List<int[]> hidden, int nf, int frame, int yan, int dist, int[] base) {
        drawHiding(kit, frame, yan, dist, hidden, nf);
        return islands(px, base);
    }

    /** Draw the kit with the model merged, collapsing the listed face ranges of it. */
    static void drawHiding(List<Integer> kit, int frame, int yan, int dist, List<int[]> hidden, int nf) {
        Arrays.fill(px, 0x141414);
        Model[] parts = new Model[kit.size() + 1];
        int n = 0;
        parts[n++] = Model.tryGet(0);
        for (int id : kit) parts[n++] = Model.tryGet(id);
        Model body = new Model(n, parts, (byte) -89);
        for (int[] h : hidden) {
            for (int f = Math.max(0, h[0]); f <= Math.min(nf - 1, h[1]); f++) {
                body.field1201[f] = body.field1200[f];
                body.field1202[f] = body.field1200[f];
            }
        }
        body.createLabelReferences();
        body.calculateNormals(64, 850, -30, -50, -30, true);
        Model out = body;
        if (frame > 0 && !AnimFrame.isNull(frame)) {
            out = Model.field1190;
            out.method361(false, body);
            out.applyTransform(frame);
            out.method363();
            out.field1226 = null;
            out.field1225 = null;
        }
        out.method381(yan, 0, 65536, 0, 65536, 0, 85, dist, 0);
    }

    /**
     * Background pixels with no way out: the dressed player has a hole in it there.
     *
     * This is the third fault, and the one neither of the others can see. Two worn models that do
     * not meet leave a gap, and whatever is behind the player - a cape, the floor - is seen
     * through it. Nothing about priorities or depth is wrong; there is simply nothing drawn.
     */
    static int holes(int[] img) {
        boolean[] seen = new boolean[img.length];
        int[] stack = new int[img.length];
        int sp = 0;
        for (int x = 0; x < W; x++) {
            for (int y : new int[] { 0, H - 1 }) {
                int i = y * W + x;
                if (img[i] == 0x141414 && !seen[i]) { seen[i] = true; stack[sp++] = i; }
            }
        }
        for (int y = 0; y < H; y++) {
            for (int x : new int[] { 0, W - 1 }) {
                int i = y * W + x;
                if (img[i] == 0x141414 && !seen[i]) { seen[i] = true; stack[sp++] = i; }
            }
        }
        while (sp > 0) {
            int i = stack[--sp];
            int x = i % W, y = i / W;
            if (x > 0 && img[i - 1] == 0x141414 && !seen[i - 1]) { seen[i - 1] = true; stack[sp++] = i - 1; }
            if (x < W - 1 && img[i + 1] == 0x141414 && !seen[i + 1]) { seen[i + 1] = true; stack[sp++] = i + 1; }
            if (y > 0 && img[i - W] == 0x141414 && !seen[i - W]) { seen[i - W] = true; stack[sp++] = i - W; }
            if (y < H - 1 && img[i + W] == 0x141414 && !seen[i + W]) { seen[i + W] = true; stack[sp++] = i + W; }
        }
        int n = 0;
        for (int i = 0; i < img.length; i++) {
            if (img[i] == 0x141414 && !seen[i]) n++;
        }
        return n;
    }

    /** How many pixels of the model under test are visible at all. */
    static int visible(int[] with, int[] without) {
        int n = 0;
        for (int i = 0; i < with.length; i++) {
            if (with[i] != without[i]) n++;
        }
        return n;
    }

    /**
     * The model's visible pixels that form an ISLAND - a patch with no path to the background
     * through its own pixels, so it is surrounded on every side by the body it is drawn against.
     *
     * THIS IS THE GEOMETRY FAULT, as distinct from the draw-order one. A cape hanging beside a
     * player reaches the background, and so does a pauldron's outline; a sliver of mesh that has
     * come through the middle of a skirt does not. Draw order can produce an island too - the max
     * capes' marks were islands - so a count here is not proof of an intersection, but an
     * intersection cannot help being one.
     */
    static int islands(int[] with, int[] without) {
        boolean[] mine = new boolean[with.length];
        for (int i = 0; i < with.length; i++) {
            mine[i] = with[i] != without[i];
        }
        // flood from the frame edge through everything that is NOT the model; whatever the flood
        // reaches is background or body, and any of the model's pixels next to it are on its outline
        boolean[] outside = new boolean[with.length];
        int[] stack = new int[with.length];
        int sp = 0;
        for (int x = 0; x < W; x++) {
            for (int y : new int[] { 0, H - 1 }) {
                int i = y * W + x;
                if (!mine[i] && !outside[i]) { outside[i] = true; stack[sp++] = i; }
            }
        }
        for (int y = 0; y < H; y++) {
            for (int x : new int[] { 0, W - 1 }) {
                int i = y * W + x;
                if (!mine[i] && !outside[i]) { outside[i] = true; stack[sp++] = i; }
            }
        }
        while (sp > 0) {
            int i = stack[--sp];
            int x = i % W, y = i / W;
            if (x > 0 && !mine[i - 1] && !outside[i - 1]) { outside[i - 1] = true; stack[sp++] = i - 1; }
            if (x < W - 1 && !mine[i + 1] && !outside[i + 1]) { outside[i + 1] = true; stack[sp++] = i + 1; }
            if (y > 0 && !mine[i - W] && !outside[i - W]) { outside[i - W] = true; stack[sp++] = i - W; }
            if (y < H - 1 && !mine[i + W] && !outside[i + W]) { outside[i + W] = true; stack[sp++] = i + W; }
        }
        // now flood the model's own pixels, starting from the ones that touch what the first flood
        // reached: those are its outline, and everything connected to them is its body
        boolean[] reached = new boolean[with.length];
        sp = 0;
        for (int i = 0; i < with.length; i++) {
            if (!mine[i]) continue;
            int x = i % W, y = i / W;
            boolean edge = x == 0 || y == 0 || x == W - 1 || y == H - 1
                || (x > 0 && outside[i - 1]) || (x < W - 1 && outside[i + 1])
                || (y > 0 && outside[i - W]) || (y < H - 1 && outside[i + W]);
            if (edge) { reached[i] = true; stack[sp++] = i; }
        }
        while (sp > 0) {
            int i = stack[--sp];
            int x = i % W, y = i / W;
            if (x > 0 && mine[i - 1] && !reached[i - 1]) { reached[i - 1] = true; stack[sp++] = i - 1; }
            if (x < W - 1 && mine[i + 1] && !reached[i + 1]) { reached[i + 1] = true; stack[sp++] = i + 1; }
            if (y > 0 && mine[i - W] && !reached[i - W]) { reached[i - W] = true; stack[sp++] = i - W; }
            if (y < H - 1 && mine[i + W] && !reached[i + W]) { reached[i + W] = true; stack[sp++] = i + W; }
        }
        int n = 0;
        for (int i = 0; i < with.length; i++) {
            if (mine[i] && !reached[i]) n++;
        }
        return n;
    }

    /** Draw the reference kit, with model id `with` merged in when it is not -1. */
    static void draw(List<Integer> kit, int with, int frame, int yan, int dist, boolean depthSorted, boolean hide) {
        Arrays.fill(px, 0x141414);
        Model[] parts = new Model[kit.size() + 1];
        int n = 0;
        if (with >= 0) parts[n++] = Model.tryGet(with);               // the cape slot comes first
        for (int id : kit) parts[n++] = Model.tryGet(id);
        Model body = new Model(n, parts, (byte) -89);
        if (hide && with >= 0) {
            // collapsed, not flagged through field1206: allocating that array changes how the rest
            // of the kit draws, which is the one thing a baseline must not do. See PlayerRender.
            for (int f = 0; f < parts[0].field1199; f++) {
                body.field1201[f] = body.field1200[f];
                body.field1202[f] = body.field1200[f];
            }
        }
        if (depthSorted && with >= 0) {
            // the merge keeps face order, so the model under test is faces 0.. of the result
            int faces = parts[0].field1199;
            if (body.field1207 == null) {
                body.field1207 = new int[body.field1199];
                Arrays.fill(body.field1207, body.field1210 < 0 ? 0 : body.field1210);
            }
            Arrays.fill(body.field1207, 0, faces, 10);
        }
        body.createLabelReferences();
        body.calculateNormals(64, 850, -30, -50, -30, true);
        Model out = body;
        if (frame > 0 && !AnimFrame.isNull(frame)) {
            out = Model.field1190;
            out.method361(false, body);
            out.applyTransform(frame);
            out.method363();
            out.field1226 = null;
            out.field1225 = null;
        }
        out.method381(yan, 0, 65536, 0, 65536, 0, 85, dist, 0);
    }
}
