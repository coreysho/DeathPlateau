package jagex2.client;
import jagex2.graphics.*;
import jagex2.io.*;
import java.nio.file.*; import java.io.*;
import java.awt.image.BufferedImage; import javax.imageio.ImageIO;

// The skill icons out of the client's own media archive, one transparent PNG each.
//
// WHERE THEY LIVE. Two palette sprite sheets: "staticons" holds eighteen of them and "staticons2"
// the rest. Which sheet and which index belongs to which skill is NOT guessable and is not guessed
// here - Client.java carries the mapping, read out of interfaces/stats.if's own icon components,
// and this is the same table. Getting it wrong puts a fishing rod next to Runecraft and nothing
// about the picture tells you.
//
//   java -cp javaclient/build/classes/java/main:. jagex2.client.SkillIconFiles <media.jag> <outdir>
//
// media.jag is Engine-TS/data/pack/client/media, which the engine packs from content.
//
// PIXEL 0 IS TRANSPARENT, as it is everywhere else in this client: Pix8 keeps palette indices and
// index 0 is the hole. Written at the sprite's own size rather than padded out to the sheet's
// cell, because a web page sizes it with CSS and the padding would only make the icon smaller.
public class SkillIconFiles {
    // Stat order is PlayerStat's: attack, defence, strength, hitpoints, ranged, prayer, magic,
    // cooking, woodcutting, fletching, fishing, firemaking, crafting, smithing, mining, herblore,
    // agility, thieving, slayer, farming, runecraft, construction, hunter.
    static final String[] SLUG = {
        "attack", "defence", "strength", "hitpoints", "ranged", "prayer", "magic",
        "cooking", "woodcutting", "fletching", "fishing", "firemaking", "crafting", "smithing",
        "mining", "herblore", "agility", "thieving",
        "slayer", "farming", "runecraft", "construction", "hunter"
    };

    // Lifted verbatim from Client.SKILL_ICON_SHEET / SKILL_ICON_INDEX. If the client's table ever
    // changes, this one has to change with it.
    static final String[] SHEET = {
        "staticons", "staticons", "staticons", "staticons", "staticons", "staticons", "staticons",
        "staticons", "staticons", "staticons", "staticons", "staticons", "staticons", "staticons",
        "staticons", "staticons", "staticons", "staticons",
        "staticons2", "staticons2", "staticons2",
        "staticons2",
        "staticons2"
    };

    public static void main(String[] a) throws Exception {
        String mediaPath = a[0], outDir = a[1];
        Jagfile media = new Jagfile(Files.readAllBytes(Paths.get(mediaPath)));
        Files.createDirectories(Paths.get(outDir));

        int[] index = indices();
        int wrote = 0;
        for (int stat = 0; stat < SLUG.length; stat++) {
            Pix8 icon;
            try {
                icon = new Pix8(media, SHEET[stat], index[stat]);
            } catch (Exception | Error e) {
                System.out.println("no sprite for " + SLUG[stat] + ": " + e);
                continue;
            }

            BufferedImage out = new BufferedImage(icon.wi, icon.hi, BufferedImage.TYPE_INT_ARGB);
            boolean any = false;
            for (int y = 0; y < icon.hi; y++) {
                for (int x = 0; x < icon.wi; x++) {
                    int p = icon.pixels[y * icon.wi + x] & 0xFF;
                    if (p == 0) {
                        out.setRGB(x, y, 0);
                    } else {
                        out.setRGB(x, y, 0xFF000000 | icon.bpal[p]);
                        any = true;
                    }
                }
            }
            if (!any) {
                System.out.println("blank sprite for " + SLUG[stat]);
                continue;
            }

            ImageIO.write(out, "png", new File(outDir, SLUG[stat] + ".png"));
            wrote++;
        }
        System.out.println("wrote " + wrote + " of " + SLUG.length + " skill icons to " + outDir);
    }

    static int[] indices() {
        return new int[] {
            0, 2, 1, 6, 3, 4, 5,        // attack, defence, strength, hitpoints, ranged, prayer, magic
            15, 17, 11, 14, 16, 10, 13, // cooking, woodcutting, fletching, fishing, firemaking, crafting, smithing
            12, 8, 7, 9,                // mining, herblore, agility, thieving
            1, 2, 0,                    // slayer, farming, runecraft - staticons2
            5,                          // construction
            4                           // hunter - index 4 of staticons2, unused art already in the 377 cache
        };
    }
}
