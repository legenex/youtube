# Style 9 · Archival Print

**Matrix:** archival collage / mid grey to cream / texture / medium build.

## Look in one sentence
A mid century public information sheet: halftone photographs cut into cream,
heavy type on torn slabs, the ink slightly out of register.

## Palette
| Hex | Role |
| --- | --- |
| `#EFE7D6` | Cream stock. The ground, and the tone keyed out of every photograph. |
| `#22201C` | Print ink. Warm near black, never neutral. |
| `#B23A2E` | The one saturated ink, reserved for money and nothing else. |
| `#8C8578` | Caption grey under a figure. |

## Typography
Anton for display slabs, Oswald for a second voice, Source Serif for notes, IBM
Plex Mono at 0.22 em for kicker strips. Four faces is correct here: a period
sheet was set from whatever the shop had.

## Shot grammar
Every photograph is a cut block with a position on the page, and it moves on
every shot: right panel, full width band, left panel, small top corner, bottom
band, then gone. Elements slide in from an edge over 0.22 to 0.30 s, or stamp in
place. Nothing fades, ever. Misregistration is a 2 to 3 px channel shift applied
last, over everything, with paper grain on top.

## Rhythm spec
About 37 shots per minute. Maximum static hold 2.5 s; measured 1.97.

## Asset recipe
Photographs reduced to newsprint plus HTML cut paper. The halftone is real: blur
slightly, flatten contrast so midtones survive, dither to two tones with an
ordered Bayer matrix, then key the paper tone out so the stock shows through.
Any photograph works, which makes this the most tolerant style in the set.

## Cost per 10 minute episode
Generation calls: 0 if any photo library is available. About 4 hours to build
the element system, 6 hours edit.

## Three rules that must never be broken
1. Nothing fades. Elements slide or stamp.
2. Red is money. Never a heading, never a rule, never decoration.
3. The photograph must move on the page every shot. A held plate under changing
   type does not read as a cut.

## What this style is bad at
Anything current. The register says archive, so it undercuts a claim that
something is true right now, and it cannot carry an interface or a process at
all. Fine detail dies in the halftone, so faces and small print are unusable.
