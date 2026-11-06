# MUDWATER SPIRE — FULL HANDOFF (read this first)

> Written 6 Nov 2026, end of **session 8**, for the next AI picking this project up. Supersedes the session-7 handoff (still in git history).
> The owner is **Dinopawnz** (GitHub `dinopawnz`). The owner ran out of credits mid-session, so this handoff is meant to be complete.
>
> **How to work with the owner (important):**
> - Plain, simple, non-technical words. Short messages. The simplest possible steps.
> - **Deliver files as chat attachments. Never save anything to their computer.** They put `spire.html` in their "Otherside MMLs" folder and `spire_remote.html` in their "remotes" folder.
> - Show renders before and after big visual changes. When they're unhappy, change ONE thing at a time.
> - They send screenshots with yellow circles: fix exactly what is circled.
> - **Use Meshy for anything that has to look high quality.** They said this many times. They hate "primitive", "low quality", "cartoony" or "floating" things.
> - They care about frame rate in Otherside (100+ players): **text costs frame rate, images don't.** Prefer images and GLBs over m-label text.

---

## 0. The 60-second version

**What it is.** **Mudwater Spire**: a giant swamp-timber tower in MML for Otherside, for an **OtherGames event with 100+ players**. Goal: "the unquestionable greatest build ever". Theme: rustic bayou / Mudwater card game, NOT a castle, NOT neon or cosmic.

**The games inside (by floor):**
| Floor | y | Game / place | State |
|---|---|---|---|
| Lounge (1) | 3.0 | bar, fireplace, waterfalls, booths, card tables | done (2x bigger in v24) |
| Hall of Fakes (2) | 10.5 | find the real card among 400 portraits, 4 rounds, finals vault | **done, game 1** |
| Gallery | 24.9 | ramp/balcony over the hall | done |
| Cards (3) | 32.0 | **Mud Royale** (game 2) | **NOT BUILT** |
| Rooms (4+) | 40.0 | **Mudroom Escape** (game 3) | **NOT BUILT** |
| Roof | 51.0 | **grand finale photo spot** | **NOT BUILT** (only lift houses + gables) |

**Versions:**
| Where | Version | What |
|---|---|---|
| branch `main` | v13 | the old LIVE build. Untouched since session 6. |
| branch **`handoff-v14`** | **v24** (this commit) | all the work from sessions 6–8. This is what the owner tests. |

The owner's files load their assets from `https://raw.githubusercontent.com/dinopawnz/spire/handoff-v14/` (baked into spire.html by `build_html.py`). So **assets must be pushed to `handoff-v14` before the owner's HTML works.**

Remote PIN: **7747**, press LIVE BUILD.

**Commits on handoff-v14:** `40ff1a7` v22 · `8b11e5c` v23 · **v24 = this commit** (plus a possible follow-up commit with three new Meshy models, see §5.1).

---

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

## 2. Build → test → render → push (exact order)

```
cd /home/claude/spire
python3 build_rect.py  > /tmp/br.log     # shell, stairs, balconies, roof, lift houses, gables  -> out/glb/sp_shell.glb, out/layout.json
python3 build_lift.py  > /tmp/bli.log    # lifts (cab, shaft, gates, gear)
python3 build_fakes.py > /tmp/bf.log     # Hall of Fakes (400 portraits + finals vault)
python3 build_lounge.py > /tmp/bl.log    # lounge (needs out/glb/meshy_meta.json)
python3 npc.py; python3 sprites.py       # speech bubbles (sb_*.glb) / glowing words (sg_*, ms_*)
python3 slim.py                          # (v24) shrink textures to 1024 + gltfpack-simplify the heavy Meshy models (from out/glb/hi). RUN AFTER THE BUILDERS.
python3 build_html.py 25 https://raw.githubusercontent.com/dinopawnz/spire/handoff-v14/ > /tmp/bh.log   # ALWAYS bump the version number
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

## 4. What was done in sessions 7–8 (v22 → v24)

**v22:** lantern posts by the sign-up book walk-through; MUDWATER sign raised 1.5 m.

**v23** (pushed, owner tested):
- Night sky: Meshy panorama stitched by `build_sky.py` → `tex/sky_pano.jpg` on `sp_sky.glb` (dome r 480), bayou colour grading (owner asked "does that fit our Mudwater theme?" → graded warmer/olive), **golden crescent moon** (`sky_moon.png`, from the owner's reference image; dark side navy, no glow ring).
- Waterfalls left and right of the entrance pouring from Meshy mossy crags (water sheets follow the measured groove in the crag model; owner complained twice that water came "out of thin air" — fixed by segmented tilted sheets).
- Animated swamp fire in the goblet braziers.
- Skirt + pilings close the gap under the bridge.
- Front: rustic Meshy bayou gables (owner REJECTED castle turrets/spires), fewer but grander Meshy lodge windows, hanging vines + ivy.
- Portraits: nothing covers or z-fights any of them (moved 10 cm proud of the wall; wall vines/shimmer off in the hall; high windows raised). The owner called z-fighting a "MASSIVE problem".
- Stair towers walled at the back; rails can be jumped over.
- Lift Boss bubble moved out of the way; lifts don't go home by themselves.
- Beer mug slides to the bar edge in front of the person; jukebox removed; rules sign says 400 portraits; sign-up book clickable (needs an invisible opacity-0 hitbox — `visible=false` cubes aren't clickable).

**v24** (this commit):
- **Building 2x floor plan** (X1 60, Z1 42.5) and everything spread to match: lounge furniture (+3 groups), card tables, trees, lantern rings, 100 lanterns, wet floor, 12 trusses, stage/dance floor, booths, Hall of Fakes (`build_fakes.py`: `RX, RZ = 15.5, 12`, exactly 200 portraits per row, screens and chandeliers moved), outdoor decor radii.
- **Lifts wider and taller** for tall avatars (sizes above). lifttest passes.
- **Performance** (owner: "make sure we aren't crashing people"):
  - `zoneUp` puts every still indoor model AND outdoor dressing into floor zones by position, so players only load what's on their floor; building models are `_global`; players at unknown positions see only "out".
  - Staged build: building first, decor/furniture at 2.5 s, sky + galaxy at 5.5 s.
  - `slim.py`: textures to 1024 and gltfpack simplify (`-noq -kn -km -si R -sp -se 0.02`); COLOR_0 stored as uint8; cheaper railings.
  - Before: ~4.06M triangles all visible, ~150 MB. After: outside ~1.4–1.6M visible, lounge zone ~0.97M, hall ~0.23M; shell 52 → ~30 MB.
  - Idea not done yet: the shell still has ~690k vertices (rustic boards); could be merged/simplified more.
- Objects left and right of the sign-up book removed (sign stands on two slim iron rods).
- **Bar:** Meshy high-quality beer mug (`sp_mug.glb` from `sp_m_beermug`), bottles on the shelves (`sp_m_bottles`), hanging glass racks (`sp_m_glassrack`).
- **The mug tips and pours toward the player who clicked it** (inner `tip` group turns to face the drinker, then tips).
- Wall on the stair landings facing the lift (no falling off).
- Roof lift houses: doorway so you can walk out of the lift onto the roof.
- **Roof gables no longer float**: timber knee walls with glowing windows under each gable (`gable_spots()` in `build_rect.py`). NOT render-checked yet.
- **Bridge kept clear of fog**: `outside.py` tests each mist piece's real footprint (the mist GLB is ~82×59 m at scale 1!) and slides it off the bridge/porch. NOT render-checked yet.
- **Old Coliseum hook-post lanterns removed from the bridge** (`build_html.py`, the `lantern_post` loop). The Meshy lantern posts on the rails stay.
- Tests: simtest, roundtest, biotest, drinktest: ERRORS none. lifttest 40 bots / 15 min: NO PROBLEMS FOUND (689 rides, max wait 61 s).

## 5. TO DO — in this order

### 5.1 Finish the owner's last requests (started, not finished)
The owner's last messages (with screenshots):
1. *"we cannot have hideous looking low quality primitive looking lanterns like those in the front of the house. please replace those with higher quality models. use meshy if you have to."*
2. *"if you have to use meshy for these plant things too, do it"* (the flat cattail reeds in the water by the bridge).

What's been done: three Meshy models were ordered (item list `src/meshy_items/items_v24b.json`, reference pictures in `src/meshy_refs/`):
| name | Meshy image-to-3D task id | use |
|---|---|---|
| `floatlantern` | `01a1b00d-f03b-7016-bb39-319968b14615` | replaces `mwm_floatlantern` (30 on the water in `build_html.py` + the sky lanterns rising in `spire_src.html` "sky lanterns drifting up off the water", which use `mw("mwm_floatlantern")`) — these are the floating white boxes the owner circled |
| `hanglantern` | `01a1b00d-f7c9-75de-a00b-4eea06f28213` | replaces `mwm_jarlantern` (Floor-2 eave lanterns all round the outside, `build_html.py` "jar lanterns"; and the hall's `F2['lanterns']`), and could replace `sp_lantern_a` under the balconies (`outside.py`) |
| `cattails` | `01a1b00e-1db8-724a-85ff-f4c51777a1e9` | replaces every `reeds` (Coliseum flat cards) in `build_html.py` (bridge, porch edge, lounge pond, hall moat) |

If the follow-up commit with `sp_m_floatlantern.glb`, `sp_m_hanglantern.glb`, `sp_m_cattails.glb` is in the repo root, they are processed already. If not: download each finished task with `GET https://api.meshy.ai/openapi/v1/image-to-3d/<task id>` → `model_urls.glb` into `/home/claude/meshy/models/<name>.glb` (Meshy keeps tasks for a while; otherwise re-run `python3 batch3d.py src/meshy_items/items_v24b.json`, ~39 credits each). Then:
- add to `meshy_props.py`: `GLOW['floatlantern'] = ('warm', 1.8)`, `GLOW['hanglantern'] = ('warm', 1.6)`; run `python3 meshy_props.py floatlantern hanglantern cattails`; add them to `slim.py` TARGET if heavy (cattails will be placed ~100 times: keep it ≤ 3k triangles).
- placing: Meshy models go in `D['sdeco']` via `place(name, x, y, z, ry, size, axis)` in `outside.py` (`size` along axis `'h'` height, `'w'` width, `'l'` longest). Convert the deco entries there, e.g. after the falls filter: for each `e` in `D['deco']` with `e[0] == 'reeds'` → `add(place('cattails', e[1], e[2], e[3], e[4], 1.8 * e[5], 'h'))` and drop it from deco; same for `mwm_jarlantern` → `place('hanglantern', x, y - 0.9, z, ry, 0.8, 'h')` (check the hang height in a render); `mwm_floatlantern` → `place('floatlantern', x, 0.05, z, ry, 0.9*s, 'h')`.
- sky lanterns in `spire_src.html`: replace `mw("mwm_floatlantern", {...})` with `model("sp_m_floatlantern.glb", {...})` (keep the rising tween). `sdeco` models are zoned by `zoneUp`; the decor regex `DECOR` in `spire_src.html` (LITE mode removes those) should include `m_floatlantern|m_hanglantern|m_cattails`.
- Render the bridge (V24O.json, camera on the bridge looking at the house) and send the owner before/after.

### 5.2 Render-check and send (not done for v24)
Render and look at: the roof (gable knee walls, lift-house doorways), the lift cab inside (taller), the bridge (no fog, no hook posts), the bar (bottles, glass racks, mug), the sign-up book, the lounge at 2x size, the Hall of Fakes (`portrait_scan.py` must be clean). Send the owner renders.

### 5.3 The roof = GRAND FINALE photo spot
Owner: *"the roof of the building should be the grand finale… very awesome looking picturesque place"* and *"players can celebrate the end of the build and take pictures together in the most scenic part of the tower and there better not be floating structures that look unrealistic up here."*
- Everything must sit on something (no floating pieces). The deck is y 51; it's big (120 × 85 m).
- Ideas to propose (show a render first): a timber rooftop terrace around the steeple with railings, Meshy string lights, lanterns, potted cypress/moss planters, benches, a photo stage/arch with the Mudwater logo (as an IMAGE, not text), the floating Mudwater pack and rings above as the backdrop, the golden moon framed behind; firework/sparkle FX for the finale; a host-triggered "celebration" from the remote.
- Remember the owner's "no castle" rule and the bayou-lodge look.

### 5.4 Mud Royale (game 2, floor 3, y 32)
Owner: *"we probably need 4 teams for the mud royale… areas where we can separate the teams and then have a counter that shows how many players on a team."*
- 4 team pens (colours), each with a **live player counter** (use `m-position-probe` or zone checks; show numbers with pre-made digit GLBs/images like the `ms_d0..9` sprites — NOT m-label text) so hosts can even out teams.
- Spec from old notes: territory card game, giant board, Mudwater rules, 2-minute timer, most squares wins, MVP. Host panel in the remote (start, reset, timer, scores). Ask the owner for the rules details if unclear.

### 5.5 Mudroom Escape (game 3, floor 4 up)
Notes in `src/ESCAPE_TOWER_NOTES.md`. Agreed so far:
- 6 teams; 6 coloured team doors on floor 4 with a START; 6 escape floors × 6 rooms; each room a puzzle that unlocks the door to the next floor; first team out reaches the **Victory Hall**; raffle. No guard, no stealing.
- **Hosts take a NORMAL slow lift like the existing ones** (owner: "hosts dont need a fast lift straight up"). A glass lift was REJECTED.
- Hosts watch via a **stair with landings around a glass core** (rooms' inner glass walls kept clear) + a watch wall. I said I'd go with this unless the owner said no; they didn't object.
- The tower must get taller to fit 6 floors (the roof moves up: `FL['roof']` and everything that reads it).

### 5.6 NPCs (LAST, owner said so)
Maybe resembling the Mudwater card characters (owner: "but that may be too hard"). Pipeline `meshy_npcs.py` (text/image → 3D → rig → animations), `split_clips.py`. Keep the owner's ape #5413 as the lift operator.

### 5.7 Then
A real multi-player test in Otherside; update this handoff; push to `main` only when the owner approves.

## 6. Things the owner REJECTED (never bring back)
neon/cosmic looks · pop-out holograms · blue card backs · rune circles · entrance columns · finals dome · **any wood or object crossing/covering portraits** · cards over lift/stair doors · plain/empty floors · guard + stealing in the heist · secret room below floor · unrealistic animals · mud splats with boot prints (wanted real puddles) · round pipe-like ceiling logs · thick green moss cones · the floating book on top (keep the Mudwater pack) · Meshy floating islands / bonsai near the walkway · removing the original water GLBs · a glass/express lift for hosts · lifts that teleport or open one door · **castle turrets/spires/"castle look"** · too many windows · purple Milky Way sky · waterfalls coming out of nowhere · **floating structures** · **fog over the bridge** · **primitive low-quality lanterns/plants** · the jukebox.

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
