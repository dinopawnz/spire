# MUDWATER SPIRE — FULL HANDOFF (read this first)

> Written 6 Nov 2026, end of **sessions 9–10**, for the next AI picking this project up. It supersedes the session-8 handoff (that one is in git history).
> The owner is **Dinopawnz** (GitHub `dinopawnz`). The owner ran out of usage credits at the end of this session, so this handoff is meant to be complete.
>
> **How to work with the owner (important):**
> - Plain, simple, non-technical words. Short messages. The simplest possible steps.
> - **Deliver files as chat attachments. Never save anything to their computer.** `spire.html` goes in their "Otherside MMLs" folder and `spire_remote.html` in their "remotes" folder. After EVERY push, attach both files.
> - Show renders before and after big visual changes. When they're unhappy, change ONE thing at a time.
> - They send screenshots with yellow circles: fix exactly what is circled.
> - **Use Meshy for anything that has to look high quality.** They hate "primitive", "low quality", "cartoony" and "floating" things.
> - **Mudwater theme everywhere.** Session 10 lesson: ordinary playing cards on the card tables were a "HUGE MISSTEP". Anything card-like must be the real Mudwater cards (`mudwater_repo/mwc_001..120.jpg`, back `mwc_back.jpg`, pack `mw_pack.glb`).
> - They care about frame rate in Otherside (100+ players): **text costs frame rate, images don't.** Prefer images and GLBs over m-label text.
> - They often send several messages in a row while you work, and interrupt tool calls. Read each one; keep going on the rest.

---

## 0. The 60-second version

**What it is.** **Mudwater Spire**: a giant swamp-timber tower in MML for Otherside, for an **OtherGames event with 100+ players**. Goal: "the unquestionable greatest build ever". Theme: rustic bayou / Mudwater card game. NOT a castle, NOT neon or cosmic.

**The games and places, by floor:**
| Floor | y | Game / place | State |
|---|---|---|---|
| Outside | 0 | bridge, waterfalls, lanterns, cattails, sign-up book | done (Meshy lanterns + cattails placed in v25) |
| Lounge (1) | 3.0 | bar, fireplace, waterfalls, booths, card tables, stage band, pond, Kodas, **pool tables** | done; see §5 for open bugs |
| Hall of Fakes (2) | 10.5 | find the real card among 400 portraits, 4 rounds, finals vault | **done, game 1** |
| Gallery | 24.9 | ramp/balcony over the hall | done |
| Cards (3) | 32.0 | **Mud Royale** (game 2) | **NOT BUILT** |
| Rooms (4+) | 40.0 | **Mudroom Escape** (game 3) | **NOT BUILT** |
| Roof | 51.0 | grand finale photo terrace + fireworks + art wall | built; **art wall painting NOT wired yet** |

**Versions:**
| Where | Version | What |
|---|---|---|
| branch `main` | v13 | the old LIVE build. Untouched. Push to main ONLY when the owner says. |
| branch **`handoff-v14`** | **v32** | everything from sessions 6–10. This is what the owner tests. |

The owner's files load assets from `https://raw.githubusercontent.com/dinopawnz/spire/handoff-v14/` (baked into spire.html by `build_html.py`), so **assets must be pushed to `handoff-v14` before the owner's HTML works.** Remote PIN: **7747**, then press LIVE BUILD.

**Commits on handoff-v14 this session:** v25 … v32 (latest = "v32: playable pool tables …"), plus this handoff commit.

## 1. Setting up a fresh environment

```
# repo (real files, no LFS). Get push access first: call add_repo(owner "dinopawnz", repo "spire", access "push").
git clone --branch handoff-v14 https://github.com/dinopawnz/spire /home/claude/spire_repo
mkdir -p /home/claude/spire /home/claude/viewer
cp -r /home/claude/spire_repo/src/* /home/claude/spire/
cp -r /home/claude/spire_repo/src/viewer/* /home/claude/viewer/
# processed models the build expects in out/glb (the repo root holds every built asset)
mkdir -p /home/claude/spire/out/glb/hi
cp /home/claude/spire_repo/*.glb /home/claude/spire/out/glb/
cp /home/claude/spire_repo/src/hi_models/*.glb /home/claude/spire/out/glb/hi/      # full-detail Meshy originals that slim.py simplifies from
# meshy_meta.json (bounding boxes of every Meshy model, needed by build_lounge/outside): it is written by meshy_props.py into out/glb.
#   If missing, check src/ for a copy or re-run meshy_props.py (needs /home/claude/meshy/models raw files) - see §7.
# the Coliseum decor + card art
git clone --depth 1 https://github.com/dinopawnz/mudwater /home/claude/mudwater_repo
mkdir -p /home/claude/dinopawnz && ln -sfn /home/claude/mudwater_repo /home/claude/dinopawnz/mudwater
mkdir -p /home/claude/spire/out/cards_small /home/claude/spire/out/hall /home/claude/spire/out/vault /home/claude/spire/out/bio
echo '{"real": 821}' > /home/claude/spire/out/hall/answer.json      # real #62 Founder = forgery 821
echo '{"real": 63}'  > /home/claude/spire/out/vault/answer.json     # real #100 Black Flag = vault slot 63
```
- **⚠️ Before the first rebuild, copy `out/glb/meshy_meta.json`**: in session 8 it lived only in the workspace. A copy is now committed at `src/meshy_meta.json`; do `cp src/meshy_meta.json out/glb/`.
- **Tools:** this session `npm` worked for **gltfpack** (`npm i gltfpack` in `/home/claude/tools`, used by `slim.py`: path `/home/claude/tools/node_modules/.bin/gltfpack`). Session 7 found npm/pip blocked, so check. If gltfpack is missing, `slim.py` can't simplify, but the already-slimmed GLBs in the repo root are fine to reuse.
- **three.js for renders:** `git clone --depth 1 --branch r170 --filter=blob:none --sparse https://github.com/mrdoob/three.js /home/claude/three_src`, `git sparse-checkout set build examples/jsm`, `ln -sfn /home/claude/three_src /home/claude/viewer/node_modules/three`.
- **jsdom tests:** `node simtest.js <page>` worked this session (jsdom installed in viewer/node_modules). If not, use `python3 chrometest.py simtest.js <page>` (runs them in headless Chrome).
- **SECURITY:** API keys go ONLY in `/home/claude/.meshy_key` and `/home/claude/.eleven_key` (umask 077). **Never** in the repo (it is PUBLIC), builds, deliverables, memory or chat output. **Grep the repo for the key value before every push.** The owner pasted their Meshy key into chat in session 7; recommend they regenerate it on meshy.ai.
- **Meshy balance:** about **2,400 credits** at the end of session 8 (2,526 before the last three models).

### 1b. Session 9–10 environment notes (read with §1)
- Workspace layout used: `/home/claude/spire` (= repo `src/`, flat), `/home/claude/spire_repo` (clone of handoff-v14), `/home/claude/viewer` (tests + renderer), `/home/claude/meshy` (gen.py, batch3d.py, `*_items.json`, `models/` raw Meshy downloads), `/home/claude/mudwater_repo` (card art, Coliseum decor), `/home/claude/castle_repo` (sparse clone of `dinopawnz/castle`: `citadel_toy_piano.glb`, `citadel_pool_harp.glb`, `citadel_fx_keyglow.glb`, `citadel_fx_string.glb`, `piano_48..83.mp3`, `harp_*.mp3`), `/home/claude/kodas` (raw Koda GLBs + rendered previews).
- **npm and pip were BLOCKED** in sessions 9–10 (gltfpack unavailable). Texture shrinking uses `shrink_glb.shrink` (python). The already-slimmed GLBs in the repo root are fine to reuse: after running builders do `cp /home/claude/spire_repo/*.glb out/glb/` and then put back only the GLBs you intentionally rebuilt.
- **Network allowlist (owner added):** `upload.wikimedia.org`, `commons.wikimedia.org`, `archive.org` (but NOT archive.org's data nodes `*.us.archive.org`/`dn*.ca.archive.org`, so archive downloads fail), `storage.googleapis.com` (Koda GLBs). Wikimedia ORIGINAL files often return **429 rate-limited**; the **transcoded** copies work: `https://upload.wikimedia.org/wikipedia/commons/transcoded/<h0>/<h0h1>/<Name>/<Name>.mp3` (or `.ogg`), `h = md5(Name with spaces→underscores)`. Use a User-Agent like `MudwaterSpireBuilder/1.0 (https://github.com/dinopawnz/spire)`, sleep a few seconds between requests.
- **Koda GLBs:** `https://storage.googleapis.com/ruukeibkumeeicgbwypcrwbxwizoehnt/fhsdjurbfbwruyoqwrsaf/M04TLO5GkVDivsyzkBCrQKvdcWQN6od5/a/<number>.glb`. The owner said "stick to my kodas": **5077, 119, 9372, 9929, 9923, 9924**. They will give more numbers later. Only use numbers the owner approves (each Koda belongs to its holder).
- `meshy_meta.json` (bounds of every Meshy model, needed by build_lounge/outside/band/roof/pool): `out/glb/meshy_meta.json`, copy committed at `src/meshy_meta.json`. Copy it to `out/glb/` before building.
- Meshy balance: about **1,950 credits** left (session 10 spent ~13 models × 39).
- Renders: `viewer/mmlshot.py <json>`. **mmlrender.js now poses animated models** (SkeletonUtils clone + AnimationMixer at `opts.animT`, default 6.8 s). Use the skip list from `viewer/KODA.json` / `POND.json` / `CARDS.json` or Chrome runs out of memory. A quick single-model viewer: `python3 -m http.server 8765 -d /home/claude` and `/home/claude/kodas/view/k.html?f=<glb,...>&ts=<anim times>&side=1&top=1&cy=&d=&sp=` with `shot.py url out.png`.

## 2. Build → test → render → push (exact order)

```
cd /home/claude/spire
python3 build_rect.py  > /tmp/br.log     # shell, stairs, balconies, roof, lift houses, gables  -> out/glb/sp_shell.glb, out/layout.json
python3 build_lift.py  > /tmp/bli.log    # lifts (cab, shaft, gates, gear)
python3 build_fakes.py > /tmp/bf.log     # Hall of Fakes (400 portraits + finals vault)
python3 build_lounge.py > /tmp/bl.log    # lounge (needs out/glb/meshy_meta.json)
python3 npc.py; python3 sprites.py       # speech bubbles (sb_*.glb) / glowing words (sg_*, ms_*)
python3 slim.py                          # (v24) shrink textures + gltfpack-simplify (needs npm gltfpack; if blocked, SKIP and reuse the repo-root GLBs) the heavy Meshy models (from out/glb/hi). RUN AFTER THE BUILDERS.
python3 build_html.py 33 https://raw.githubusercontent.com/dinopawnz/spire/handoff-v14/ > /tmp/bh.log   # ALWAYS bump the version number
cd /home/claude/viewer
node simtest.js   /home/claude/spire/out/spire.html    # remote, lifts, hall flow -> "ERRORS: none"
node roundtest.js /home/claude/spire/out/spire.html    # 4 rounds -> finals -> winner
node biotest.js   /home/claude/spire/out/spire.html    # glow layer + LITE mode
node drinktest.js /home/claude/spire/out/spire.html    # tap -> mug -> only the owner drinks it (updated in v24 for the mug's tip group)
python3 lifttest.py /home/claude/spire/out/spire.html 40 15   # 40 bots ride 15 min -> "NO PROBLEMS FOUND". It matches pads BY SIZE: if you resize lifts, update it.
python3 portrait_scan.py                                       # checks nothing touches/covers any portrait (z-fighting!)
python3 mmlshot.py V24O.json                                   # render the real page (see below)
# push:
cp /home/claude/spire/*.py /home/claude/spire/*_src.html /home/claude/spire_repo/src/ ; cp -r /home/claude/spire/tex/. /home/claude/spire_repo/src/tex/
grep -rlF "$(cat /home/claude/.meshy_key)" /home/claude/spire_repo --exclude-dir=.git     # MUST print nothing
cp /home/claude/spire/out/glb/sb_*.glb /home/claude/spire_repo/      # speech bubbles are NOT picked up by the ref check: copy by hand
cd /home/claude/spire && python3 sync_to_repo.py "v25: ..." --branch handoff-v14
```
- `sync_to_repo.py` runs a ref check in Chrome, copies every new/changed asset the page uses plus both HTML files, then commits and pushes. Commit message lines are taken from the argument.
- **Renders:** `viewer/mmlshot.py <scene.json>` loads the real spire.html in Chrome, presses LIVE BUILD, and draws the live MML with three.js. Scene JSON: `{"page", "pos" (player position, picks zones), "opts": {"skip": [...], "env", "hemi", "sun", "bloom"...}, "shots": [{"out","cam","at","fov"}]}`. Examples: `V24O.json` (outside), `V24M.json` (lounge), `V24R.json` (hall), `B2.json` (sign-up book). The Chrome tab runs out of memory if everything loads; use `opts.skip` (`portraits/pv_`, `gc_`, `sp_m_`...).
- Going live on `main` (only when the owner says): rebuild WITHOUT the branch URL (`python3 build_html.py 25`), then `python3 sync_to_repo.py "v25"` (no --branch).

## 3. Coordinates & layout (v24, building is 2x the v21 floor plan)

- `build_rect.py`: `X1, Z1 = 60.0, 42.5` (half width/depth; front is +z). `FL = dict(lounge=3.0, hall=10.5, gallery=24.9, cards=32.0, rooms=40.0, roof=51.0)`.
- `BAND` = the Hall of Fakes portrait band; `PORCH` = front porch box; `WALK` = boardwalk/bridge: `w 8, z0 = Z1+12, z1 = Z1+78, y1 0.6`.
- Stair towers `SW` on east and west sides (`xi, xd, xo, zl -9.5, z0 -6, z1 6, zm 9.5`). Every storey has a back wall (z = zm + 0.12) and a lift-side wall (z = zl - 0.12) on the landings, plus sloped hop-over rail colliders (height 1.05) so players can jump the rails.
- **Lifts** `LIFTS`: `B` "The Grand Cage" at (X1-4.25, -(Z1-11)), `D` "The Lucky Cage" at mirrored x. Normal slow lifts, 1.8 m/s, glide by timed `m-attr-anim` (Otherside ignores `m-attr-lerp`). v24 sizes: `shaft_apo 3.2, cab_apo 2.9, door_w 2.4, door_h 3.7, shaft_top = roof + 6.5`; the cab is stretched taller (`CE 0.85` in `build_lift.py`; cab walls 3.45, gate 3.35). Lifts no longer return home on their own. The Lift Boss bubble is on the cab back wall.
- **Roof** (y 51): two lift-head houses (sized from the shaft, 11 m tall, **front doorway out onto the deck** — v24 fix for "exit blocked by a wall"); three Meshy gables along the front edge at x 0 / ±31 (widths 18/12) **now with timber knee walls under them** (v24 fix: "floating structures"); chimneys, water tower, steeple with the floating Mudwater pack + gold/teal rings above.
- Galaxy of floating cards: radii 106/132/158 (owner said keep).
- Outside: Meshy crags with waterfalls at x ±33, z ≈ 84.5 (either side of the bridge); mist; vines/ivy; lodge windows; front banners ±20; braziers with animated fire.

## 4. What was done in sessions 9–10 (v25 → v32)

(Sessions 7–8 work, v22–v24, is described in the session-8 handoff in git history: 2x floor plan, lifts, zoning, slim.py, bar mug, gables, sky, waterfalls.)

### v25 – v27: fixes
- **Inside not loading** in Otherside: the v24 floor zoning relied on `m-position-probe`, which did not report players in Otherside → nothing indoors loaded. **`const ZONING = false`** in `spire_src.html`: everyone sees everything (`zoneSee/zoneOut` call `zoneAll`). Re-enable only after proving the probe works in Otherside.
- **Meshy lanterns + cattails placed** (`outside.py`): reeds → `cattails` (remeshed 4.9k → 1.3k triangles), jar lanterns → full-detail `hanglantern` hung on chains (`sp_lantern_chain.glb`) at the OLD jar height (owner: the remeshed ones looked deformed and too high), floating lanterns → `floatlantern`; sky lanterns use `F.skyLantern`. Balcony lanterns on the front face only (243 → 138 lanterns).
- **Lift doors**: `tween()` now sets the FINAL attribute value immediately and draws the `m-attr-anim` on top (doors were stuck open / one leaf open on clients that missed the end). 30-bot lifttest: no problems.
- Glass racks raised (`RACK_Y = 4.45`), end-wall cards only on plain wall bays (not over windows).

### v28: the roof grand finale (`roof.py`)
Raised dark-timber photo stage with steps, Meshy photo arch (8 m) with the Mudwater logo, 16 Meshy cypress planters, 12 benches facing the stage, 2 Meshy stone fire pits with animated flames (`D.roofFires`), 9 Meshy lantern posts with festival-light strands to the steeple eave (`sp_roof_lights.glb`), the Old Skipper by the stage. Invisible collider pads (`D.pads`). Remote: **CELEBRATE** (command `celebrate`) = 14 firework bursts + `winner.mp3`.

### v28–v32: the lounge stage band (`band.py`, `spire_src.html` BAND)
- Stage at `F1['stage']` = (0, 3.705, -36.2), front z -30.5.
- **Grand piano and harp copied from the owner's castle build** (`dippys_lost_crown.html`), recoloured mahogany, piano stool removed (stand to play). Every key / string is clickable and plays its own recorded note (`piano_48..83.mp3`, `harp_*.mp3` from the castle). Layouts in `castle_instruments.json`. Piano turned to face the crowd (`PA 115`); **harp turned round in v32 (`HA 160`)**.
- **Drum kit (Meshy) turned to face the audience in v32 (`DK 180`)**, one click zone per piece (hi-hat, 2 crashes, snare, 2 toms, floor tom, kick) at positions read from a top view of the model. **Real recorded drum hits** (Wikimedia Commons, CC BY-SA 3.0, by Clngre: Bass drum, Snare drum unmuffled, Hi hat closed, Tom 12 inch, Floor tom; crash = CrashCymbalSample.ogg, public domain) → `band_drum_<kick|snare|hihat|tom_hi|tom_lo|crash>.mp3`. **CREDIT NEEDED** somewhere (e.g. the handoff/README or a small credits plaque): "Drum samples by Clngre, CC BY-SA 3.0, Wikimedia Commons".
- **Guitar**: Meshy guitar, tilted so a player standing behind it looks like they're playing; **made bigger in v32** (1.6 m) with a bigger click zone; each click strums the next chord: **real acoustic guitar chords** (Commons `G-major.ogg`, `C-major.ogg`, `D-major.ogg`, `E-major.ogg`, public domain, by WBOSITG) → `band_guitar_0..3.mp3`.
- Microphone prop on stage (decor only; Otherside can't amplify voices from MML).
- Remote: **INSTRUMENTS ON/OFF** (against trolls).
- **v32 sound fixes:** each instrument has its OWN voice limit (`CAP = {drum 4, guitar 2, piano 5, harp 5}`); before, one shared limit let one fast player silence every other instrument. Instruments are quieter (0.45–0.5) because loud overlapping instrument sounds made Otherside turn the jazz down (owner: "after we started playing the instruments, the jazz music became very low"). The owner said **do NOT make the music louder**.

### v29–v32: background music (the "swamp radio")
- 13 speakers (lounge ×5, hall ×2, cards, rooms, roof ×2, bridge, outside) all play the same record with the same `start-time` so they stay in sync. Tracks are shuffled at load and loop as a playlist. Remote: **MUSIC ON/OFF**, **NEXT SONG**, and "Now playing" (commands `music on|off|next`).
- v29 used 1920s public-domain 78s (`radio_00..10.mp3`); the owner wanted better → **v30: clean modern jazz** (`jazz_00..10.mp3`, list in `src/music_tracks.json`, made by `music_prep.py`): U.S. Air Force Heritage of America Dixie Players (Panama, That Da-Da Strain, Tiger Rag), U.S. Coast Guard Band (After You've Gone, Way Down Yonder in New Orleans), U.S. Army Jazz Ambassadors (Sweet Georgia Brown), USAF Airmen of Note (Blues for Mundy) = US government works, public domain; **Kevin MacLeod** (Whiskey on the Mississippi, Porch Blues, Night on the Docks (Sax), Slow Burn) = **CC BY 3.0, credit shown on the remote's "Now playing"**. ~42 min.
- **v32: music watchdog** (owner: "the jazz music ended on its own"): `every(4000)` restarts the next record if the timer that should start it was lost/late. NOT yet confirmed in Otherside.
- The old original song (`swamp_jazz.py`, `swamp_jazz_00/01.mp3`) is the fallback if `music_tracks.json` is missing.

### v29–v31: the owner's Kodas in the lounge (`koda_rig.py`, `koda_pack.py`)
- Koda GLBs are rigged (UE5 mannequin skeleton, T-pose, no animation). `koda_rig.py` adds ONE looping glTF clip per Koda (posed with world-axis rotations per bone in the T-pose frame; later entries for the same bone apply after earlier ones) and shrinks textures to 512. In MML: `m-model anim = the same file, anim-loop true` (the castle's method).
- Placement (`build_html.py`, `D.kodas` = `[file, x, y, z, ry, scale 1.25, walk radius, lap ms]`): **5077** in the card-table armchair at (13.2, -8.8), **9924** in the fireside armchair at (21.8, 37.5) — both now **rip Mudwater packs** (koda_pack.py: holds the real `mw_pack` art, tears the strip off, fans out 5 real Mudwater cards, leans in to look, wiggles, a new pack appears; 14 s loop); **119** and **9929** on bar stools 0 and 2 with **beer steins**, sipping every 13 s; **9372** and **9923** walking laps round the island bar (radius 9.5 and 12.5, opposite directions, ~0.45 m/s).
- **v31 fix (owner: "i dont see the kodas holding a glass of beer")**: Otherside only draws SKINNED meshes of an animated model, so props are merged in as their own skinned mesh bound 100 % to a new joint `prop_N` under the hand bone (`Rig.attach`). Show/hide = animating that joint's scale. Steins made bigger. **Not yet confirmed in Otherside** — ask the owner.

### v29: the pond (bayou garden, lounge west, centre (-25, 4))
5 Meshy frogs (3 bullfrogs, 2 green treefrogs) on Meshy lily pads, a Meshy red-eared slider turtle on a log, 4 Meshy dragonflies darting over the water, a tea-dark water surface (`sp_pond_water.glb`). One random frog croaks every 2.6–7.8 s (real Everglades pig-frog recording, NPS, public domain → `frog_0..3.mp3`, pitch variants) with a throat puff; clicking a frog makes it croak, hop and turn. Fish were deliberately not added (shallow walk-through pond).

### v30: Mudwater cards, never playing cards
- The Meshy card table and coffee table had ordinary playing cards painted in their textures. `fix_cardtable.py <cardtable|coffeetable>` paints them out of the texture (originals kept as `meshy/models/*_orig.glb`), then `meshy_props.py cardtable coffeetable`.
- `card_spread.py`: real Mudwater cards dealt on every card table (`sp_mw_deal_0..3.glb`: a two-card hand facing each seat + a Mudwater deck + one card turned up) and a fanned hand + deck on every coffee table (`sp_mw_fan_0..1.glb`).

### v32: playable POOL TABLES (`pool.py`, `pool_balls.py`, `pool_assets.py`, `spire_src.html` POOL)
- Two Meshy pool tables at (49, 2.5) and (49, 13) on the open east side, turned 90°, 3.4 m long, felt 1.03 m high, playing area 3.01 × 1.58 m. Meshy cue rack on the east wall (z 7.75), "how to play" plaques on the wall at z -2.66 and 18.59 (plain bays, not windows).
- Balls: `sp_ball_0..15.glb`, painted textures (solids, stripes, numbers), radius 0.048.
- **How to play:** click the glowing ring on your side of the white ball (16 sectors) → the Meshy cue swings round; `<` `>` nudge 3°; **SOFT / MEDIUM / HARD** shoots; **NEW RACK** at both ends; clicking the cue ball itself also aims if the client sends a click position. Remote command `pool` racks both tables.
- Physics: the whole shot is simulated at once on the server (2D, 240 Hz, rolling friction, ball–ball and cushion collisions, pockets), then each ball is animated piece by piece (one `m-attr-anim` per straight piece between collisions). Sounds: `pool_cue`, `pool_clack_0..2`, `pool_rail`, `pool_pocket` (synthesised). Scratch → white ball back on the head spot. Cleared table → re-racks.
- `viewer/pooltest.js`: a HARD break moves 15/16 balls with 9 sounds. **Not yet tried in Otherside.**

### Roof art wall (started, NOT finished)
`roof.py artwall()` builds the 38.4 × 8 m canvas with timber frame (`sp_artwall.glb`) in front of the steeple house, 2 paint stands, a signing lectern, and writes `D.artwall` = `{cols 48, rows 10, cell 0.8, x0, y0, z, palette (13 colours + 'erase'), stands, sign, board}`. **The JS is not written yet**: the canvas is visible but blank and not paintable.

### Tests that pass on v32
`chrometest.py simtest.js` → ERRORS none · `bandtest.js` (instruments off blocks sounds) · `musictest.js` (13 speakers in sync, next/off/on, 6 Kodas animated, frogs croak on click) · `pooltest.js` (break shot works).

## 5. TO DO — in this order

### 5.1 Open bugs the owner reported at the very end (fix first)
1. **Frogs stop animating after being clicked** (owner: "after clicking on the toads, their animation stopped working"). Look at `frogHop()` / `frogCroak()` in `spire_src.html` (POND block). Likely causes: (a) `fr.busy` stays true if the `later(700)` that clears it is lost — make busy time-based (`fr.until = now() + 700`) instead of a flag; (b) `tween()` on `fr.body` `y` and `sy` plus `fr.g` `ry` leaves stale `m-attr-anim` children that Otherside keeps applying — after the hop, remove leftover anims and set plain attributes (`y 0`, `sy 1`). Test with a quick chrometest that clicks a frog twice and checks the next chorus croak still tweens.
2. **Confirm in Otherside**: beer steins visible (v31 skinned props), pack-opening Kodas show the pack and cards, music never stops (v32 watchdog), music no longer ducks when instruments play (v32 quieter instruments), drums sound different per piece, pool tables playable. Ask the owner to check each.
3. **Drum/guitar credit**: add "Drum samples by Clngre (CC BY-SA 3.0, Wikimedia Commons)" and "Music by Kevin MacLeod (incompetech.com), CC BY 3.0" to a small credits plaque (image, not text) or the README.

### 5.2 Finish the roof ART WALL (owner: "a wall where players can draw, sign their names and create a massive art piece")
Data is ready in `D.artwall` (§4). Write the JS:
- 480 cells (48 × 10, 0.8 m) as thin `m-cube`s on the canvas, opacity 0 until painted; clicking one sets that player's chosen colour (opacity 1, slight emissive). Per-player colour map; 70 ms cooldown per player. Consider 2 × 2 "brush" cells if too fiddly.
- Palette swatches (13 colours + eraser) on the two stands at `D.artwall.stands` (small Meshy-looking paint pots or image swatches).
- Signing: an `m-prompt` at the lectern (`D.artwall.sign`); names go onto ONE name board image/label at `D.artwall.board` (text costs frame rate: one board, not hundreds of labels).
- Remote buttons: **CLEAR WALL**, **LOCK WALL** (commands `art clear|lock|unlock`).
- Test (chrometest), render, push.

### 5.3 Mud Royale (game 2, floor "cards" y 32)
Owner: *"we probably need 4 teams for the mud royale… areas where we can separate the teams and then have a counter that shows how many players on a team."*
- 4 coloured team pens, each with a **live player counter** (digits as images/GLBs like `ms_d0..9`, NOT m-label). Counting needs player positions: the position probe did NOT work in Otherside (see v25). Alternatives: a big walk-in pad per pen with an `m-position-probe` of small range placed IN the pen (test if small-range probes work), or players click a "JOIN RED/BLUE/…" plaque (counts by click, with a LEAVE). Ask the owner which.
- Game rules were never fully defined. Old notes: territory card game on a giant board using Mudwater rules (cards have top/left/right/bottom values in `src/cards/cards.json`, Triple-Triad style), 2-minute timer, most squares wins, MVP. **Ask the owner for the rules before building**; propose a simple version (e.g. teams claim tiles of a giant Mudwater board by clicking; stronger card values steal neighbouring tiles; 2-minute rounds).
- Host panel on the remote: start, reset, timer, scores, team counts.

### 5.4 Mudroom Escape (game 3, floor 4 "rooms" y 40 and up)
See `src/ESCAPE_TOWER_NOTES.md`. Agreed: 6 teams pick one of 6 coloured doors on floor 4, host presses START; 6 escape floors × 6 rooms, one room per team per floor, each a puzzle unlocking the door to the next floor; first team out reaches the Victory Hall; raffle. No guard, no stealing. Hosts ride a NORMAL slow lift (glass/express lift REJECTED) and watch via a stair with landings round a glass core + a watch wall. **The tower must get taller** (raise `FL['roof']` in `build_rect.py` and everything that reads it: lifts `stops`, roof.py, outside.py, music speakers, sky/galaxy heights). Puzzle ideas (not yet approved): hidden keys in a shack, lily-pad pressure plates (4 people), Mudwater card code keypad, lights-out lanterns, valve order, frog-choir pattern.

### 5.5 Ideas offered to the owner, no answer yet
Interactive lounge items: firefly jars, wishing well, arm-wrestling, fortune-teller, photo booth, darts, cauldron, rocking chairs. More Kodas (owner will send numbers). NPCs LAST (owner said so; keep the owner's ape #5413 as the lift operator; pipeline `meshy_npcs.py`).

### 5.6 Then
Full multi-player test in Otherside (100+ players: check frame rate; the lounge is now heavy: Kodas ~2 MB each, pool, pond, band). Update this handoff. Push to `main` only when the owner approves (rebuild without the branch URL, `sync_to_repo.py` without `--branch`).

## 6. Things the owner REJECTED (never bring back)
neon/cosmic looks · **ordinary playing cards (use Mudwater cards)** · making the jazz louder · pop-out holograms · blue card backs · rune circles · entrance columns · finals dome · **any wood or object crossing/covering portraits** · cards over lift/stair doors · plain/empty floors · guard + stealing in the heist · secret room below floor · unrealistic animals · mud splats with boot prints (wanted real puddles) · round pipe-like ceiling logs · thick green moss cones · the floating book on top (keep the Mudwater pack) · Meshy floating islands / bonsai near the walkway · removing the original water GLBs · a glass/express lift for hosts · lifts that teleport or open one door · **castle turrets/spires/"castle look"** · too many windows · purple Milky Way sky · waterfalls coming out of nowhere · **floating structures** · **fog over the bridge** · **primitive low-quality lanterns/plants** · the jukebox.

## 7. Meshy pipeline
- `gen.py out.png "prompt" [aspect]`: text-to-image (nano-banana-pro, 9 credits).
- `batch3d.py items.json`: reference image (style suffix added) → image-to-3D (textured PBR, 30 credits), in parallel → `/home/claude/meshy/models/<name>.glb`, log `models/batch.log`. Item lists in `src/*_items.json` and `src/meshy_items/`.
- `remesh.py`: Meshy remesh (5 credits).
- `meshy_props.py [names]`: shrink textures (`BIG` sizes), glow masks (`GLOW`, modes warm/teal/gold/pane in `glow_mask.py`), → `out/glb/sp_m_<name>.glb` + `meshy_meta.json` (bounds used for placement).
- `slim.py`: simplifies the heavy ones from `out/glb/hi/` (originals now committed in `src/hi_models/`).
- Raw Meshy downloads are NOT in the repo; processed `sp_m_*.glb` are in the repo root.
- `build_sky.py`: sky panorama (`tex/sky_a.png`, `tex/sky_b.png` from Meshy) + moon (`tex/moon_src.png`).

## 8. File guide
| File | What it does |
|---|---|
| `src/build_rect.py` | shell: constants, walls/windows (`bay_spec`), balconies (`belts`), stairs (+walls, hop rails), roof (lift houses with doorways), `gable_spots` (+knee walls), portico, boardwalk |
| `src/build_lift.py` | lifts; `stretch()` makes cab/portal taller (`CE`, `PE`) |
| `src/build_fakes.py` | Hall of Fakes (400), vault |
| `src/build_lounge.py` | lounge (2x), Meshy furniture via `mp()`, bar bottles/racks, `meshy_mug()` |
| `src/build_sky.py` | sky dome + moon |
| `src/outside.py` | ALL outside dressing: railings, lantern posts, crystals, lilies, waterfalls/crags, mist (+bridge clearing), vines/ivy, lodge windows, gables, banners |
| `src/build_html.py` | gathers everything into `D` and bakes `out/spire.html` + remote; Coliseum decor list (`dz(...)`) |
| `src/spire_src.html` | world logic: zones (`zoneUp`), staged build, lifts, fireplace, waterfalls, goblet fire, sky, sign-up book, mug tip, NPCs |
| `src/spire_remote_src.html` | host remote (PIN 7747) |
| `src/slim.py` | performance: texture + triangle slimming |
| `src/glb.py`, `src/kit.py` | GLB writer, materials, `railing(cheap)`, `window()` |
| `src/npc.py`, `src/sprites.py` | speech bubbles, glowing words |
| `src/viewer/*` | tests (simtest, roundtest, biotest, drinktest, lifttest, portrait_scan) + renderer (mmlshot) |
| `src/sync_to_repo.py` | push changed assets + HTML |
| `src/hi_models/` | full-detail Meshy originals for slim.py |

### 8b. Files added in sessions 9–10
| File | What it does |
|---|---|
| `src/roof.py` | roof finale terrace + art wall canvas/data |
| `src/band.py`, `src/castle_instruments.json` | stage band layout, click zones, castle piano/harp key maps |
| `src/band_sounds.py` | (old) synthesised band sounds; drums/guitar now replaced by real recordings (see §4) |
| `src/swamp_jazz.py` | the original fallback song |
| `src/music_prep.py`, `src/music_tracks.json` | cleans/levels the playlist → `jazz_NN.mp3`; track list read by build_html.py |
| `src/koda_rig.py` | Koda animation clips (sit / bar / walk), skinned props (`Rig.attach`) |
| `src/koda_pack.py` | pack-opening Koda clip |
| `src/fix_cardtable.py`, `src/card_spread.py` | paint playing cards out of Meshy tables; deal real Mudwater cards |
| `src/pool.py`, `src/pool_balls.py`, `src/pool_assets.py` | pool tables placement, balls, sounds + button plaques |
| `src/pond_items.json`, `src/pool_items.json` | Meshy item lists (frogs, turtle, dragonfly; pool table, cue, rack) |
| `src/viewer/musictest.js`, `src/viewer/pooltest.js`, `src/viewer/bandtest.js` | tests (run with `python3 chrometest.py <test> /home/claude/spire/out/spire.html`) |
| `HANDOFF_FULL.md` | this file |

Key JS blocks in `src/spire_src.html` (search for these): `const ZONING = false`, `function tween(`, `const BAND =`, `const CAP =` (per-instrument voice limits), `const MUSIC =` + the watchdog `every(4000`, `(D.kodas || [])`, `const POND =`, `const POOL = []`, `function celebrate(`. Remote (`src/spire_remote_src.html`): panels "Music", "The stage band", "The roof - grand finale".
