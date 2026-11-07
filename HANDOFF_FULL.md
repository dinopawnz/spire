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
| Cards (3) | 32.0 | **Mud Royale** (game 2) | built + bot-tested (v34-v37), floor dressed to lounge standard (v39) |
| Rooms (4) | 40.0 (+ upper level 45.3) | **Mudwater Escape** (game 3) | built + bot-tested (v43), looks still basic |
| Roof | 51.0 | grand finale photo terrace + light-curtain backdrop + fireworks + paintable art wall | done (v33) |

**Versions:**
| Where | Version | What |
|---|---|---|
| branch `main` | v13 | the old LIVE build. Untouched. Push to main ONLY when the owner says. |
| branch **`handoff-v14`** | **v56** | everything from sessions 6–11. This is what the owner tests. |

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


### v33 (session 11): lifts self-heal, roof backdrop, working art wall
- **Lifts** (owner: "worked earlier today, now clicking the button outside the lift does nothing at all"). Bots could not reproduce it (40 bots, 15 min: no problems), so a lift was most likely left stuck "busy" after a lost/failed timer step. Now: `later()`/`every()` catch errors (last one shown in `liftstat`); every busy spell has a **deadline**; `heal()` snaps a stuck lift to a clean state (cab at its target floor, all doors shut) - checked every 3 s and on every button press; a step from before a heal is ignored (`st.tok`); operator chatter can't break a ride. A press at the floor where the doors are already open re-sends the doors (re-inserts the leaves) + chimes, for clients that missed the opening. Host test commands: `liftjam B` (pretend B is stuck) and `liftstat` (JSON status incl. `heals`, `err`). Test: `/tmp/healtest.py` pattern (jam -> heals in <4 s; jam + call -> rides). **Ask the owner if the lifts still ever stop.**
- **Roof photo backdrop** (`roof.py backdrop()`, `sp_roof_backdrop.glb`): right behind the stage (z -9.2), a curtain of ~900 warm bulbs on 53 strands in front of a deep-green velvet drape, carved timber posts + gilt beam, Spanish-moss swags (Meshy `vines`), a Mudwater banner at each end. The steeple + floating pack still crown it. Solid pad behind it.
- **Art wall moved and made paintable** (owner: "wrong place... our art is probably going to suck, we need a beautiful backdrop and the art somewhere else on the side"): `roof.py artwall()` now builds it in a local frame and stands it on the WEST side towards the front (centre x -45.6, z 19, facing +x), out of every stage photo. 30 x 10 squares of 0.8 m (24 x 8 m). JS block "THE ART WALL" in `spire_src.html`: one big click target reads `e.detail.position` (element-local); if a client ever sends no position it switches to a grid of 300 small targets (`[GRID MODE]`). Paint stands (13 colours + pink eraser) on two tables, 70 ms per-player cooldown, painted squares are the only cubes created. Lectern prompt -> names on ONE m-label board along the top (newest 45). Remote panel "The art wall": CLEAR / LOCK / UNLOCK (`art clear|lock|unlock`, `art` = status).
- `meshy_meta.json` was missing the session-10 models (frogs, turtle, dragonfly, pool table/cue/rack); bounds added from the processed GLBs (`src/meshy_meta.json` updated). Without them the frogs and pool tables silently vanish from a rebuild.
- Tests on v33: simtest, roundtest, biotest, drinktest, musictest, pooltest, bandtest all pass; lifttest 40 bots / 15 min: NO PROBLEMS FOUND; art wall test (paint, erase, grid mode, sign, clear) passes.

### v34 (session 11): MUD ROYALE (game 2) is playable
**Owner's rules (they said these were agreed long ago; don't re-ask):** players WALK ONTO an area to join a team and can switch until the host clicks START. Then every player gets 5 cards and places them on squares of a 100-square board. After 3 minutes the team holding the most squares wins. (Earlier the owner asked for 4 teams with player counters.) Capturing follows the Mudwater card numbers (Triple-Triad style, like the owner's `reference/territory_v12.html` "giant-board card capture" idea): a placed card flips an enemy card next to it when its number on that side is higher.
- `royale.py` (called from build_html after roof.py): one model `sp_royale.glb` (board on a 12 cm dais with ramps: 10 x 10 squares of 2.6 m, green felt + gold inlay; 4 pens with rope fences, flag + name board; 4-sided scoreboard on chains; 4 tilted YOUR HAND boards over the board edges; rules signs on posts at the 4 corners). `out/royale/c_001..120.jpg` small card images, `t_0..3.png` team glow, `back.jpg` card back - committed in repo `royale/` (copy by hand, sync_to_repo doesn't see runtime images). `D.royale` = layout + card numbers.
- Teams: GATORS (green), CRAWDADS (red), BULLFROGS (gold), CATFISH (teal). Pads are the owner's Territory method: a VISIBLE `m-cube` slab 14 cm tall with `collide=true` + `collision-interval 90`, listening to `collisionstart`/`collisionmove` (connectionId) - NOT the position probe (which doesn't report in Otherside).
- JS block "MUD ROYALE" in spire_src.html: `rJoin` (only while open), `rStart` (deal 5 random cards to everyone on a team; hands drawn per player with `visible-to` on all 4 hand boards; click a hand card to select, gold frame shows it), `rPlace` (click a square: 350 ms cooldown, taken/no team/out of cards messages hang under the hand boards, captures, pop animation, sounds), `rEnd` (at 3:00 or when the board is full: winner/tie on the scoreboard, MVP = player whose cards hold most squares, shown in one m-label; host gets a summary), scoreboard digits only re-drawn when a number changes, timer bar is one m-attr-anim. Disconnects leave the team.
- Host: `royale start | stop | open | clear | demo` (+ status); remote panel "Mud Royale": START, END NOW, NEW GAME, EMPTY TEAMS, TEAM COUNTS. `royale demo` fills the board for renders.
- **v35 rule change (owner):** the game NEVER ends early - only after 3 minutes. When every square is filled, players UPGRADE: a card whose four numbers add up to MORE than the card on a square can be played on top of it (any square, own team or enemy); it takes the square and captures neighbours as normal. Weaker -> "NEED A STRONGER CARD TO UPGRADE". Everyone gets "BOARD FULL! UPGRADE CARDS" when it fills. (My interpretation of "upgrade" - confirm with the owner if they meant something else.) **v36: board is 14 x 14 = 196 squares** (owner approved; 36.4 m board), pens moved out to z ±29 / x ±33. **No hanging scoreboard** (owner: no jumbotron, the 8 m ceiling is too low; "we just need to clearly see who's winning from signs around the board"): four double-sided timber score signs stand at the board corners (±24) - scores + clock face the board (leader's column gets a gold glow while live), the rules sign is on the back. Only the YOUR HAND boards hang. royaletest uses 45 bots and reads the board size from the page.
- `viewer/mmlshot.py` now takes a `js` staging script (bots join + play) - see `viewer/F3D.json` for a mid-game render.
- **Bug fixed:** v24 scaled the Hall of Fakes banner HEIGHT by the floor-plan factor (`bannerAt`), lifting "FIND THE REAL FOUNDER" + the portraits-left counter through the hall ceiling onto floor 3. Back at 22.6.
- Tests: `viewer/royaletest.py` (40 bots: team counts, switching, late joiner blocked, 100/100 squares match the capture rule, board-full end, winner + MVP, reopen), `viewer/royaletimer.py` (ends at 180 s). All old tests pass.
- **v37 (owner: "those fixes were already supposed to be part of the game")**: (1) every card image has ONE BIG number on each SIDE (top centre, left middle, right middle, bottom centre; gold-rimmed dark badges baked into `royale/c_NNN.jpg` by `royale.badge_card()`, Inter ExtraBold) - owner's design: you only read the edge that touches the card you're battling; (2) REFILLS: a new card every 10 s into an empty hand slot, max 5 (`R.refill`), for the whole 3 minutes; (3) finale: at 0:30 the clock bars turn red + "30 SECONDS LEFT!" + chime, last 10 s tick at each corner sign. Test `viewer/royalerefill.py` (3.2 min).
### v38 (session 11): more lounge characters + zero text at load
- **Kodas 6833 + 2168** (owner's; downloaded from storage.googleapis.com, which the owner allow-listed this session). `koda_rig.py` new clips: `idle` (standing: weight shift, breathing, looking round) and `cigar`. **6833** walks a waypoint loop (`D.kodaPaths`: turn to face the next corner, walk at 0.45 m/s) through the open floor between the island bar and the front seating ((-7,17) (14,17) (14,27) (-7,27)); **2168** stands at (45.2, 7.75) between the pool tables, facing them. Owner: "ill add more later that can walk around the first floor or be standing around in empty spaces".
- **Guest ape #6136** (owner uploaded the GLB; NOT one of the hosts' apes - "just an ape lounging around... smoking a cigar"): 87 MB upload -> `sp_ape_6136.glb` 3.9 MB (textures 512). Same UE5 skeleton as the Kodas, so koda_rig works. Clip `cigar` (12 s): sitting back (knees bent 80 deg - he's tall), cigar hand on the armrest, raised to the mouth at 6.2-7.6 s (arm angles from a reach search: `CIGAR_UP`), leans back to blow at ~9 s. Cigar = `sp_cigar.glb` (leaf, gold band, ash, glowing ember) merged as a skinned prop on `hand_r`. Seated in the free fireside armchair (26.2, 37.5), scale 0.9. `D.loungers` = [file, x, y, z, ry, scale, mouth xyz, period, blowAt]; the model's `anim-start-time` is 0 so the JS can time the smoke: 4 grey spheres puff up from his mouth each cycle. The raw upload is NOT in the repo (too big); keep `sp_ape_6136.glb`.
- **Text audit (owner: "text brings frame rate down, images don't")**: `viewer/textaudit.py` counts m-labels after the build: **0**. The art-wall name board is a picture (`aw_sign`) until the first name is signed; the Mud Royale MVP name labels (4) disappear after 30 s; the Hall of Fakes finals list is the only other label (end of game). Keep it that way: every new sign/word must be a sprite (`sprites.py`).
### v39 (session 11): floor 3 dressed to the lounge's standard
`royale.decor()` -> `sp_royale_decor.glb` (string lights under the whole ceiling, 12 Mudwater banners, gold frames, light pools, 46 puddles) + sdeco (8 Meshy trees `sp_mtree_1/2` with collider pads, 4 Chesterfield lounges with fanned Mudwater hands + barrel, 4 card tables dealt with real cards + armchairs, 60 iron lanterns) + `D.chand3` (16 lantern rings over the pens, seating and board; JS concat in the ring block) + `D.royale.art` (7 framed cards on plain wall panels as m-images `royale/w_NNN.jpg`, never over windows - uses `ext_windows`). About +470k triangles, but the trees/furniture/lanterns are the lounge's own models (already downloaded); only the 7 MB decor GLB is new. Pen flags glow toned down (0.12).
### v40 (session 11): lift gates, roof photo spot, art wall dots
- **Lift landing gate stayed shut in Otherside** (owner, floor 3: "the second gate didn't open so I can't get out"). In Chrome the gate attributes always end open, so Otherside dropped/ignored the gate's m-attr-anim. Gates now use `stepAttr()`: 9 plain `sx` attribute steps over 1.1 s, then a +0.002 nudge and the final value again (500/700 ms later) so a client that missed a step catches up. No m-attr-anim on gates any more. `heal()` cancels pending steps. Also: `zoneUp()` returns immediately when `ZONING` is false (v24 moved ~1700 models into per-floor `visible-to` groups even with zoning off - now everything stays in the world root like before v24), and the landing gates / needles / call buttons are `_global`. Tests: `viewer/gatecheck.py`, `viewer/zonecheck.py`, healtest, lifttest 40 bots.
- **Roof** (owner: "this backdrop should be further back against the wall so we can take a picture with 100+ people"): backdrop now hangs against the steeple house front (zb -30.45), 36 m wide (`half 18`, top 8.0), banners at the ends; the stage (now 32 x 8.9 m, z -29.9..-21) stands right in front of it with the arch; the two planters that were in front were removed; Old Skipper at (-18.5, -19). The deck in front (~54 x 22 m) is free for the group photo; benches/fire pits further forward.
- **Art wall = tiny dots** (owner: "only allow players to draw using tiny dots, not giant squares"): painting worked in Otherside, so click positions arrive. Each click paints a 10 cm dot (one per 10 cm spot, a new colour replaces it), 90 ms per-player cooldown, max 5000 dots on the wall (oldest fade first) for frame rate; the eraser clears a 5 x 5 dot patch. The 0.8 m grid stays only as the fallback for a client that sends no click position. Test `viewer/dottest.py`.
### v41 (session 11): pool fixes, quiet songs out, first performance pass
- **Otherside animation quirk (important for everything):** when an `m-attr-anim` is removed, Otherside can fall back to the value the element had when the animation STARTED (that's why the cue "teleported back", the lift gate stayed shut, the white ball vanished). `tween()` now removes the anim, then sends the final value again as a fresh change (+0.001, then exact 70 ms later; the catch-up is cancelled if a newer move starts: `_fu`). Gates use stepped attributes (`stepAttr`), the pool cue turns instantly (plain setAttribute). Prefer plain attribute changes for anything whose end state matters.
- Pool: the white ball could be pulled back under the felt by a late sink animation after the re-spot -> `poolPlace` cancels every leftover animation/catch-up on the balls first. `viewer/cuetest.py`.
- Music: removed the 4 softest tracks (jazz_05 Sweet Georgia Brown, 06 Blues for Mundy, 08 Porch Blues, 09 Night on the Docks) -> 7 tracks, ~23 min (`music_tracks.json`).
- **Performance audit** (`viewer/perfaudit.py`, `viewer/animaudit.py`): v40 drew ~4.5M triangles, ~3,600 mesh pieces + ~1,000 cubes/images, 1,146 running animations, all floors for everyone. v41 animation cuts: bio veins steady glow (-152), lantern rings no sway (-34), wisps 70 -> 12, sky lanterns a third, spores a quarter => 711 animations (320 in LITE). **The 120 floating cards keep spinning and bobbing (owner wants that) but in LITE MODE they hold still** (their anims carry `data-lite-anim` and LITE removes/restores just those; `gc_` is no longer in the DECOR regex so the cards stay). `viewer/litetest.py`.
- NEXT (planned, told the owner): combine repeated static models per floor into one GLB per kind (lanterns/chains/rings/furniture/vines/windows/railings/trees: ~3,600 pieces -> a few hundred), lighter versions of the heavy Meshy models (hanglantern 2k tris x138, floatlantern 2.5k x72, armchair, trees), then floor-only drawing via standing pads (collision events, like Mud Royale) if still needed.
- Owner also reported: "a small piece of the waterfall is getting cut off by the rock" (not yet looked at - ask for a screenshot / check the outdoor crag falls).
### v42 (session 11): fps pass 2, Kodas, chairs
- **Merge repeats** (`merge.py`, called at the end of `build_html.py`; `NOMERGE=1` builds without it): every copy of a static decor model (D.sdeco + the lantern rings, which are now placed through it) baked into ONE file `mg_<model>.glb` (textures stored once). Merging stores every copy's shape, so models are ranked by objects saved per extra MB and taken while >= 15/MB and within 15 MB: small lanterns a/b/c, chains, rings, dealt cards, coffee-table fans => **~780 fewer objects for +11.7 MB**. NOT merged (owner asked about chairs/vines/hanging lanterns, but they'd cost ~45 MB more download for ~300 objects - asked the owner): armchairs, sofas, vines, hanging lanterns, windows, railings, reeds, posts. LITE filter still works (merged names contain the original names).
- **Floating cards are one piece each** (`build_cards.py`: front | back | gold strip in one picture): 360 -> 120 objects, same look.
- `slim.py`: lighter versions (2% shape cap) of hanglantern, floatlantern, vines, cattails, window, railing, lanternpost, lantern_ring, bottles.
- Audit now: 2,467 draw pieces (was 3,485), 4.07M triangles (was 4.40M), 718 animations (319 in LITE). Portraits NOT merged: they're clicked in the Hall of Fakes game (owner).
- **Walking Kodas no longer "walk in place"** (owner): the timer-driven waypoint walk (6833) is gone; every walker rides a looping turn group (like the island-bar laps) and every 40 s each walker gets a fresh copy of its lap animation (same start time, added before the old one is removed) and its walk clip re-sent. 6833 now circles (3, 22) r 4.5.
- **New Kodas**: 6895 (walks a lap round (24, 2), r 4.2), 554 (stands near the stage at (-6, -28) watching the band, idle clip). Raw files in `src/kodas_raw/`.
- **Pack-ripping Kodas (5077, 9924)** (owner: cards farther from the face / turned to us): fan held at full stretch (a Koda's hand can't get more than ~0.16 m in front of its chest), cards bigger, and a SHOW-OFF: at 7.6-9.7 s of the 14 s clip the fan is turned round and pushed out in front of the hand, card faces to the room. The raw 5077/9924 files weren't kept, so `koda_pack.strip_props()` takes a built pack Koda back to a bare rig first (`/home/claude/kodas/raw_*.glb`).
- **Card tables / armchairs** (owner: chairs too short for the table): the Meshy card table was 1.7 m tall. `tables.py`: card tables squashed to 68 % height (top ~1.15 m), the armchairs round them 1.25x bigger and pulled back 0.12 m (lounge + Mud Royale floor). Koda 5077 re-seated (`_seat` is scale-aware).
- Waterfall "cut off by the rock": the lounge falls and the outdoor crag falls render fine here - waiting for the owner's screenshot with a circle.
### v43 (session 11): MUDWATER ESCAPE (game 3) built
- Owner's rules (this session): "all the teams will begin in a different room and to progress, they must solve clues/puzzles to get to the next room which may or may not be on another floor" -> no taller tower: floor 4 (y 40, ~10 m high) got an UPPER LEVEL at y 45.3.
- `escape.py` (called from build_html after royale.py) builds `sp_escape.glb` (walls, slabs, stairs, glass, door frames, team colour bars, keypad buttons, lantern caps, rug borders, boards), `sp_escape_col.glb` (invisible colliders), `sp_esc_door.glb`, `out/esc/k_NNN.jpg` + `back.jpg` (24 small Mudwater cards; **runtime images: copy `out/esc/` to the repo `esc/` by hand**), decor via D.sdeco, and `D.escape`.
- Layout: 6 lanes (west z -24/0/24 = red/gold/green, east = blue/purple/orange), complex |x| 8..44, |z| < 36; side aisles (lifts + stairs) stay free. Per lane: R1 lower outer (u 0-18 from the outer wall), R2 lower inner, an enclosed stair well inside R1's corner (u 14.5-18, v -3..12) from R2 up to R3 (upper outer), R4 upper inner, then the VICTORY HALL (upper, |x| < 8). Doors D0 start (outer wall, from the aisle), D1 R1->R2, D2 R2->well, D3 R3->R4, D4 R4->hall; doors slide 2.5 m along z into the wall (stepped attribute moves). Middle corridor downstairs (open at both ends) with glass into every R2 and a stair at the front end (z 33.5 -> 23.5) up to the Victory Hall (glass into every R4). Progress boards (6 teams x 4 lamps + clock + winner) at the back of both.
- Puzzles (JS block "MUDWATER ESCAPE" in spire_src.html; new random codes/colours/pairs every game): R1 LANTERN CODE (4 hidden lanterns - shelf top, under the table, behind barrels, hanging in a corner - show a digit when clicked; the painting's 4 gems give the colour order; 10-key keypad beside D1, 4 digits auto-checked); R2 LILY PADS (4 visible collide cylinders; need min(4, team size) occupied at once for 1.6 s; occupancy = collisionstart/move add, collisionend remove, 45 s expiry in case collisionend never comes); R3 CARD MEMORY (12 m-images, 6 pairs, mismatches flip back after 1.3 s); R4 FROG CHOIR (4 frogs, own croak + colour; rounds of 4/5/6, replays every 12 s if idle, wrong croak = red flash + replay).
- Joining: walk onto the team's rug in R1 (visible collide slab, collisionstart/move) before START; START shuts every start door; late joiners refused. First team to solve R4 wins (confetti in the hall, winner on the boards, host message); later teams get their place. Host: `escape open|start|end|clear|raffle|hint <team>|skip <team>` + remote panel "Mudwater Escape" (live progress line, 6 HINT + 6 SKIP buttons). END opens every door.
- `viewer/escapetest.py`: 45 bots, all checks pass (wrong code, too few pads, mismatches, wrong croak, finish order, hint/skip/raffle/end/open).
- Sprites: e_title + 6 colour words; sign `sg_escape_rules` (4 in the aisles); floor 4 renamed "MUDWATER ESCAPE" everywhere (lift plaques via `build_lift.py`, remote).
- **Found while rebuilding the lifts: the repo's `sp_lift_cab_col.glb` and `sp_lift_cgate_col.glb` were still the v1 size** (cab floor/walls 2.13 m half-width vs the 2.98 m cab since v24; cab gate collider 1.7 m wide vs the 2.4 m door). The pipeline step `cp spire_repo/*.glb out/glb/` kept overwriting the fresh colliders with the stale ones. v43 pushes the correct ones. **Don't blindly copy repo GLBs over freshly built collider files.**
- Still to do: dress the rooms to lounge standard (looks second, as the owner said), confirm click targets + collisionend in Otherside.
### v44 (session 11): owner bug reports
- **Hall of Fakes portraits mostly unclickable (major)** -> the v42 MERGE is now OFF by default (`MERGE=1` turns it on). Most likely cause: a merged file is ONE object spanning a whole floor (all the lanterns/chains/rings) and Otherside lets that big object catch clicks meant for things behind it. If merging comes back, merge only small, local clusters and never over clickable things - and confirm with the owner in Otherside.
- **"Ding dong" over the whole world when the build opened**: the two lifts arrived at the lounge with a chime + gate sound at build (now silent: `arrive(k, quiet)`), and the escape set-up opened/closed doors with chimes (now silent at open/start/reset/end; only a door a team just unlocked makes a soft click).
- **Drums didn't play**: each drum's click box sat INSIDE the drum; now the boxes sit on top of each piece (0.55 m tall) AND the drum kit model itself is clickable (`D.bandDrum`: the click's spot picks the nearest piece).
- **Roof photo wall**: the bulb curtain is replaced by ALL 120 MUDWATER CARDS (4 x 30 on gold mounts, two atlas pictures `tex/cardwall_0/1.jpg`, soft glow) + one row of bulbs along the top; the Mudwater logo now hangs IN FRONT of the arch (z0 + 3.3) so the posts don't cut it off.
- **Blue beam under the floating pack**: replaced by `sp_beam_soft.glb` (narrower, faint, see-through).
- **Art wall made big squares in Otherside**: one click without a position used to switch the whole wall to the 0.8 m grid for everyone. Now such clicks are ignored (counted in `art` status: "clicks with a spot / without"), the click target is solid (collide true) so clicks carry their spot, and dots are small round paint dots (11 cm). Host can still force squares with `art grid`.
- Escape puzzles: owner wants easy + fun + TEAMWORK (math like Dippy's Carrot Sums), no card memory (too easy), no frog choir (sound). Proposed: room 3 CRITTER SUMS (picture sums spread round the room -> 4-digit code), room 4 THE WEIGH-IN (math tells how many players stand on each critter pad, exactly). Waiting for the owner's OK.
### v45 (session 11)
- **Mud Royale card LEVELS** (owner: "im able to play cards that are not level 1 on the board without upgrading a card. that should not be a thing"): LEVEL 1 cards go on empty squares only; LEVEL 2+ cards are UPGRADES, played on top of a LOWER-level card (yours or an enemy's - an enemy square becomes yours), captures as before. With a full board a same-level card with a higher total may also upgrade. Levels from `cards/cards.json` (`lv`: 55 lv1, 30 lv2, 13 lv3, 14 lv4, 8 lv5) -> `D.royale.lv`. Starting hands get at least 2 level-1 cards; deals are level 1 ~55%+ of the time (always level 1 if a hand has none). Each card picture now has a clear **LV n** badge bottom-left (green LV 1 / gold LV 2+; `royale/c_NNN.jpg` regenerated - copy `out/royale/` to the repo by hand). New messages `r_lvup`, `r_lvlow`; rules sign updated. Test: `viewer/royalelevel.py` (the old `royaletest.py` places random cards, so it no longer fits the rules).
- Two framed cards on the Mud Royale floor hung at z +-10, just past the end of the stair tower wall (it runs z -9.5..9.5) - floating in air. Now at z -2 and 6 on that wall.
- **Escape**: the low wall under the Victory Hall windows ran across the bottom of every final door (owner: "the bottom of the door is blocked by wood") - fixed. Each start door now shows its team's PLAYER COUNT big over the door on the aisle side (updates every 3 s), so hosts can balance teams. The winner = the first team to open its final door (solve room 4): its colour + WINS on both progress boards, confetti in the Victory Hall, host message with the time; later teams get their place.
### v46 (session 11)
- **Lift jerk / riders dropped at the start of a ride** (owner): `glider()` (cab, ropes, counterweight, needles) used `tween()`, which writes the FINAL value first and then adds the animation - for an instant the cab (with its floor colliders) was at the destination. Now the animation starts from where the cab is, the final value is written under the finished animation 120 ms after the ride, and the animation is removed 450 ms after (plus the v41 resend). `heal()` cancels these timers too. lifttest (702 rides), healtest, gatecheck pass.
- **Escape keypad showed no numbers**: the button plates baked into sp_escape.glb sat in front of the number sprites (wrong side). Fixed; numbers at z 0.05.
- **Escape: a how-to sign in every room** (`sg_esc_r1..r4`, pictures of text): what to look for and do. Rooms 3-4 signs describe card memory / frog choir until those rooms are replaced.
### v47 (session 11): Mud Royale = the OFFICIAL Mudwater rules (owner's rules sheet: `src/Mudwater_Rules_Sheet.pdf`)
- Owner: "upgrades cannot go on an enemy's card and a card cannot jump more than 1 level. these are the official mudwater rules. the only thing we're changing is that the game doesn't automatically end when we fill up the board."
- PLACE: Level I face up on an empty square. UPGRADE: a card EXACTLY one level higher on top of a square YOUR TEAM controls (captured squares and rocks count; rock = level I). Never on an enemy square. ROCK: click a hand card twice (it turns face down, "ROCK") then an empty square: captures nothing, can never be captured, counts as level I, one uncovered rock per player at a time. Captures: higher touching number wins, ties hold, no chains (as before). The v45 "same level + higher total on a full board" rule is gone. The game still runs the full 3 minutes (team version, 196 squares, refills).
- New words r_enemy, r_rock1, r_rockon, r_tip (hint under every hand board), r_lvup/r_lvlow reworded; rules sign updated. Test `viewer/royalelevel.py` (place / upgrade +1 own / refused enemy / refused jump / rocks never captured / one rock at a time).
- NOTE: sprites.py SIGNS strings are single-quoted - escape apostrophes (a syntax error silently skipped all sprites once).
### v48 (session 11)
- **Sky dome smaller** (owner: "this dome is massive"): `build_sky.py` radius 260 m (was 480; the floating cards' outer ring is 158 m) and only down to 8 degrees below the horizon (the old full sphere's lower half lay like a dark bowl over the world's own swamp). The swamp water GLB scaled 2.1 (was 2.3) and the lake 0.48 (was 2.3 = 874 m!) so both sit inside the dome.
- **Solid water** (owner: people fall through): one invisible pad 356 x 356 m, top at y -0.25 (ankle-deep wading), centred on the water (0, 25).
- **Music volume on the remote**: MUSIC QUIETER / LOUDER (10 % steps) / 50 % NORMAL; commands `music down|up|vol <0-100>`; changes the record that's playing (no restart) and the next ones; the remote's "Now playing" line shows the %.
- **Hall of Fakes: no sound on a wrong pick** (owner worried about hundreds of wrong clicks); players still see FORGERY + countdown (private). The found sound stays (once per round).
### v49 (session 11)
- **Hall of Fakes: the portraits on the stair-tower walls couldn't be clicked** (owner, major): the stair towers' invisible wall in `sp_shell_col` stands 7 cm in front of the portraits hung at x +-51.74, z -9.5..9.5 (45 portraits), so it caught the clicks. Those portraits now hang 15 cm further out (build_html, D.hall).
- **NEW TEST - every clickable portrait: `viewer/clicktest/`**: `export.py <spire.html>` builds the world in a headless page and writes every element with its world matrix; `run.py` loads it all in three.js and casts a click ray at each of the 500 portraits from 9 spots (1.5/2.5/3.6 m out, straight and +-35 deg), listing anything in the way (colliders, visible models, invisible boxes). Now: all 400 hall portraits clear from all 9 spots; vault portraits clear from 1.5 and 2.5 m (only the 3.6 m spot hits the vault room's own walls - finalists stand inside). **Run it after any change near clickable things.**
- `viewer/hallload.py`: 100 bots clicking portraits for 60 s (~7,500 clicks): ~0.05 ms per click, worst <2 ms, no errors, winner registered.
- **Mud Royale**: a hand's first card is pre-selected, so a player's first click on it turned it into a ROCK - now a rock needs a second click on a card the player picked. Refills: every empty hand slot refills 3 s after it's played (was one card per 10 s for the whole hand). Sign + message updated.
### v50 (session 11)
- **No rocks in Mud Royale** (owner: "if every player puts down a rock, the game will end without anyone getting a point... only face up cards"): clicking a hand card only picks it; rock code kept but disabled (`rock = false`); hint under the hand boards removed; sign + message updated. Everything else = the official rules (level I on empty squares, upgrades exactly +1 on your own team's squares).
- Escape redesign under discussion (owner: no standing-on-pads puzzles - "I doubt the game can detect how many players are standing on a lily pad"; room 1 lanterns "way too easy"; forger's desk / card battle lock too easy for ~20 players who spam-click; Warden's Riddle OK if hard enough for 20+). Proposed set (all locks + 30 s team lockout on a wrong code): harder Critter Sums, the Swamp Cipher, the Witch's Eye (perspective digits), the Warden's Riddle (5-ape logic grid).
- Possible next looks items: the team pens read a bit like boxing rings (owner asked what the "gator ring" was) - offer a restyle (timber platform / moss-and-lantern clearing).
- (old note) NEXT for floor 3: decoration pass to lounge standard (owner: "every floor must keep the same standard as the first floor") - it's dark and bare apart from the arena: lantern rings + warm light pools, Mudwater banners, framed cards on the walls, spectator benches/bleachers, plants, moss on beams.

### v51 (session 11) - MUDWATER ESCAPE rebuilt: 4 code-lock rooms (owner: "give them something that stumps them... difficult enough for 20+ people"; approved "yes build those 4")
- Every door is a CODE LOCK: a 12-key keypad (1-9, CLR, 0, OK; face = `esc/keypad.jpg`, 12 invisible buttons in front of it). A wrong code locks that keypad for 30 s (red countdown). Key presses are SILENT (20 people clicking = no sound storm); only OK makes a sound. No pads, no frogs, no memory cards, no lanterns-puzzle any more.
- R1 CRITTER SUMS: 8 chests hold picture sums (5 critters, values 1-9, all different); 2 of the 8 sums are FAKE; the painting gives 4 critters in order = the code. R2 SWAMP CIPHER: a message in pigpen-style marks (letters shuffled per set), the key torn into 6 pieces in the 6 chests; the message asks a sum about things counted in the room - EXACTLY 7 candles, 4 frogs, 5 lanterns, 6 chests (escape.py builds exactly these; the corridor lanterns were removed because they show through the R2 glass). R3 WITCH'S EYE: 3 eyes painted on the floor, one true (random each game); 4 random digits are drawn as paint strokes pushed 60-100% of the way along the line from the true eye (+9 stray strokes), so they only line up from that eye (checked: readable from 2.5 m behind + 1 m above the eye too, scrambled from the room middle / the other eyes / the stair). R4 WARDEN'S RIDDLE: 5 apes on 5 numbered stools (stool 1 = left as you face the bar), hats/drinks/pets, 9-14 clues (8 pinned on the walls, the rest in chests, other chests hold junk notes); code = the stools of GATOR, FROG, CRAWDAD, CATFISH, TURTLE.
- Puzzle pools: `escape_puzzles.py` (12 sums sets, 8 ciphers, 12 riddles; every set checked to have exactly ONE answer) writes `out/esc/*.jpg` - copy them to the repo `esc/` by hand. Each team gets a different set every game; pictures only appear when the team reaches that room (no solving through the glass while teams are picked).
- Hints (remote HINT): R1 opens + marks the 2 fake sums "FAKE"; R2 shows the first half of the message; R3 a beam on the true eye for 30 s; R4 tells one pet's stool (press again for the next pet). SKIP still opens the current door.
- Chests: the body is baked into sp_escape.glb, the lid is `sp_esc_lid.glb` (hinge origin, opens with stepped rx); the note floats above the chest for everyone.
- Tests: `viewer/escapetest.py` (45 bots: chests, notes, CLR, wrong code -> 30 s lock (even the right code is ignored while locked), every code, witch strokes line up only from the true eye, hints, skip, raffle, end, open = fresh different sets) -> 45 OK. `viewer/clicktest/escclick.py` casts click rays at all 288 keypad buttons + 75 closed chests from straight on / the sides / above: all clear except a few steep side rays that pass through a real wall (a player just stands in front).

### v52 (session 11)
- **Water** (owner: "i want the other water under the bridge, not this shiny mudwater. that can be behind the start of the bridge"): `mwm_lake` is a RING with a round hole (~108 m x its scale). v48's 0.48 made the hole ~52 m, so the shiny lake covered the dark swamp water under the bridge. Now 0.95: the hole reaches ~103 m from (0, 25), the dark water fills everything round the building and under the whole bridge, the shiny lake starts just behind the bridge start (z 120.5). The solid water floor pad is 520 m (out to the dome wall).
- **Drums easier**: click boxes now wrap each drum/cymbal (95% of its width, 0.35 m below the head to 0.45 m above); the kit has 8 voices and each hit only holds its voice as long as its sound rings (was 4 voices x 2.4 s = ~1.7 hits a second). `viewer/drumtest.py` clicks every piece.
- **Hall of Fakes**: auto next round is OFF by default (owner starts each round from the remote).
- **Mud Royale**: fewer level I cards (was ~76%): each card picks its level first (I 35%, II 28%, III 17%, IV 12%, V 8%), a starting hand gets 1 guaranteed level I, an all-upgrade hand still always gets a level I. Score signs: each team's colour bar now GROWS with its squares (was a fixed strip in sp_royale.glb - removed); at the end the counts stay up, the winner goes on one line under them, the MVP name + squares under that and it stays until the next game (it used to vanish after 30 s - why the owner saw "MVP" with no name).
- **Escape room 3 (Witch's Eye)**: no eyes on the floor any more; sign is vague ("The numbers reveal themselves only to those who see as she saw"). Time-wasters that mean nothing: a crystal ball (shows random 4-digit numbers for 4 s - tempting wrong codes!), 5 potions (click = colour change), a spell book (6 pages of strange marks, `wb_page*.jpg`). Hint = a beam on the hidden spot.
- **Escape room 4 easier**: PET + HAT only (no drinks), 6-10 clues (most 6-7), up to 2 "sat on stool N" clues, no "was NOT" / "not at either end" clues; 5 wall frames (clues, a spare frame gets a junk note), at least 2 clues in chests. Board says "Tip: draw a 5 x 2 grid".
- **Escape progress boards redesigned**: a painted board (`esc/board_bg.jpg`: gold frame, title, team plates, room rows, gem sockets, winner plaque) + glowing gems per solved room (`gem_k.png`), place medals (`medal_j.png`), the winner banner (`win_k.jpg`), counts and clock on top. Board backing resized (8.9 x 4.6 m; the hall upstairs is only 4.7 m tall).
- **Escape celebration**: shock rings from the dais, 4 confetti cannons (2 at the door the winners come out of, 2 at the dais), 5 star bursts of light streaks under the ceiling, 90 fluttering paper pieces raining over the hall (team colour + gold + white). Everything is removed after 9 s.
- Tests: escapetest 47 OK (gems/medal/banner checks), royalelevel OK (level I share check), drumtest 8/8, v51 click-ray test unchanged.

### v53 (session 11) - lift trap fix
- Owner: "i went to hall of fakes and the elevator door opened but the 2nd door didnt open and im trapped in the elevator" (the screenshot showed the ESCAPE floor through the cab glass = his screen still had the cab at the floor he LEFT). Cause: every ride ended by REMOVING its m-attr-anim, and removing an anim can snap a client back to the anim's start value. Fix: `glider()` now leaves a finished ride's anim in place (it holds the end value) and removes it only at the start of the next ride, right after the new anim is added. `resync()` adds an already-finished here-to-here anim: used by heal() and when someone presses the button of the floor the cab is already at (so a trapped player can press their floor's button to fix their screen). `viewer/liftanim.py` checks exactly one y/sy anim stays on each lift part after rides; lifttest.py (30 bots, 15 min) no problems.

### v54 (session 11) - piano
- Owner: "what is this weird thing below the piano" - the stage piano model (sp_band_piano.glb, from the castle build) had a slanted board hanging from its body to the floor (62 triangles of its wood mesh). `fix_piano.py out/glb/sp_band_piano.glb` empties every wood triangle that sits fully below the body (legs are gold and stay). Already applied to the file in the repo - run it again only if the piano GLB is ever re-copied from the castle.

### v55 (session 11)
- **Hall of Fakes vault**: the door is LOCKED FOR EVERYONE until the host presses OPEN THE VAULT DOOR (`hall door open|close`); then only the finalists can pass (visible-to on the glass door + its invisible wall; late joiners stay shut out). REMOVE buttons per finalist (`hall unfinalist <id>`), also "Remove finalist" in the players table. The remote warns when a non-finalist stands inside the glass room. Wrong pick in the vault = 10 s (`VAULT_LOCK_MS`). Frost is now solid milky ice (`tex/frost_ice.jpg`, opaque, down to the floor). The real Black Flag pillar (`build_ref.py`) is 1.5 m wide with nothing across the card (was 0.72 m with the column cap crossing it). `viewer/vaulttest.py`.
- **Stair-tower portraits back on their frames** and still clickable: the SHELL collider's stair-tower boxes stuck 7 cm in front of them; `fix_shellcol.py out/glb/sp_shell_col.glb` moves that face 12 cm behind (RUN IT AGAIN after any build_rect_v9.py). build_fakes.py's own tower collider now starts 15 cm behind the wall face. Click test (`clicktest/export.py` + `run.py`): 400 hall portraits x 9 rays = 0 blocked.
- **Grand stair rail**: its collider was an upright box 4.5 m tall at the bottom step; now a sloped bar as high as the rail (jumpable). Ramp rail colliders 1.3 -> 1.1 m.
- **Lifts**: remote FORCE OPEN (`lift B open`: stops wherever it is, re-sends the cab position, opens at that floor) and OPEN ALL FLOORS (`lift B openall`: every landing door of the shaft; the next ride shuts them).
- **Players list**: never-seen connections (other people in the Otherside world) listed last as "never seen here"; the header counts people in the building.
- **Art wall**: click spot read in every likely form (wall axes / world axes / cm / Unreal axes) and the form that works is learnt; ART WALL CHECK button shows what the last click sent. No sounds on paint pots, art-wall signing or the sign-up book. `viewer/arttest.py`.
- **Mud Royale deal**: half of all new cards are an upgrade for one of your team's squares (one level up); rest random I 30 / II 32 / III 18 / IV 12 / V 8. With a board of level Is you now get ~55% level IIs (`viewer/dealtest.py`).
- **Fireworks** (CELEBRATE): `build_fireworks.py` makes 14 shell types (peony with pistil + colour change, chrysanthemum with crackle, golden willow, double ring, palm) x 3 stages (_a burst, _b droop/colour change, _c embers) + a rocket; the game launches a 30 s silent show (16 volleys + an 18-shell finale) over the tower; every piece removed after. ~13 MB of models, downloaded the first time a show runs.
- **Roof photo arch** 45% wider (sdeco entry gets an 8th field: x stretch), so its two lanterns hang outside the MUDWATER sign.
- Mud Match: confirmed the real Founder hangs in a new random spot every round (v55check).

### v56 (session 11)
- **Art wall** (owner: "still not working... nothing gets painted"): the click-ray test shows clicks DO reach the wall's big click box, so Otherside must be sending no usable click spot. Now: the click spot is also tried as a whole-document position; and if a click comes with NO spot (or 0,0,0), or two clicks fit nowhere, the wall switches itself (for everyone, once) to a CLICK NET of 768 invisible 50 cm squares - a click paints a small dot inside the clicked square. Remote: ART WALL CHECK (shows what the last click sent) and ART WALL: CLICK NET (force it; `art fine`). `viewer/arttest.py` (6 spot formats + no spot + 0,0,0, each in a fresh world). `clicktest/artclick.py`: rays to the wall and paint pots, none blocked.
- **Fireworks** (owner: "a little glitchy... 100 people tomorrow"): bursts popped in late / skipped stages because each model downloaded only when first needed. Now all shells are preloaded (microscopic, 160 m above the tower) 3 s after build for 12 s, and again for 7 s before every show; the show starts 5 s after CELEBRATE. Files ~half the size: 11 shell types, no normals (`no_normals` in glb.write), 2-quad sparkles: 34 files, 7.2 MB.

### Tests that pass on v32
`chrometest.py simtest.js` → ERRORS none · `bandtest.js` (instruments off blocks sounds) · `musictest.js` (13 speakers in sync, next/off/on, 6 Kodas animated, frogs croak on click) · `pooltest.js` (break shot works).

## 5. TO DO — in this order

### 5.1 Open bugs the owner reported at the very end (fix first)
1. **Frogs stop animating after being clicked** (owner: "after clicking on the toads, their animation stopped working"). Look at `frogHop()` / `frogCroak()` in `spire_src.html` (POND block). Likely causes: (a) `fr.busy` stays true if the `later(700)` that clears it is lost — make busy time-based (`fr.until = now() + 700`) instead of a flag; (b) `tween()` on `fr.body` `y` and `sy` plus `fr.g` `ry` leaves stale `m-attr-anim` children that Otherside keeps applying — after the hop, remove leftover anims and set plain attributes (`y 0`, `sy 1`). Test with a quick chrometest that clicks a frog twice and checks the next chorus croak still tweens.
2. **Confirm in Otherside**: beer steins visible (v31 skinned props), pack-opening Kodas show the pack and cards, music never stops (v32 watchdog), music no longer ducks when instruments play (v32 quieter instruments), drums sound different per piece, pool tables playable. Ask the owner to check each.
3. **Drum/guitar credit**: add "Drum samples by Clngre (CC BY-SA 3.0, Wikimedia Commons)" and "Music by Kevin MacLeod (incompetech.com), CC BY 3.0" to a small credits plaque (image, not text) or the README.

### 5.2 (DONE in v33) the roof ART WALL — kept below for reference
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

### 5.4 Mudwater Escape (game 3) - BUILT in v43, see the v43 section; the notes below are the older plan
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
