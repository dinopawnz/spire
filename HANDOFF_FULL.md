# MUDWATER SPIRE — FULL HANDOFF (read this first)

> Written 6 Nov 2026, end of session 7, for the next AI picking this project up. Supersedes the session-6 handoff (kept in git history).
> The owner is **Dinopawnz** (GitHub `dinopawnz`).
> **Talk to the owner in plain, non-technical words, with the simplest steps.** Short messages; they read on the go.
> **Deliver files as attachments in the chat. Never save to their computer.**
> **Show a render before changing anything big. Change ONE thing at a time when they're unhappy** — this session they nearly reverted everything after several big changes landed at once.

---

## 0. The 60-second version

**What it is.** **Mudwater Spire**: a giant swamp-timber building in MML for Otherside, for an **OtherGames event with 100+ players**. Goal: "the unquestionable greatest build ever". Every moment should look like a picture. Highest quality, realistic (they gave a concept image: `reference/19_outside_concept.png` + the one in §6).

**Two versions exist:**

| Where | Version | What it is |
|---|---|---|
| branch **`main`** | **v13** (`fc78aad`) | **LIVE** in Otherside. Untouched this session. To fully "revert", the owner just keeps using the main link. |
| branch **`handoff-v14`** | **v21** (latest) | Everything from sessions 6–7. Test link below. NOT live. |

**Test links (branch build):**
- World: `https://raw.githubusercontent.com/dinopawnz/spire/handoff-v14/spire.html`
- Host remote: `https://raw.githubusercontent.com/dinopawnz/spire/handoff-v14/spire_remote.html` (PIN **7747**, press LIVE BUILD)
- Live (main) world: same URLs with `main` instead of `handoff-v14`.

**Every version is a commit on `handoff-v14`** (roll back to any one by checking it out, rebuilding with a new version number and pushing):
`bf41634` v15 lounge rebuilt · `df5bd22` v16 · `92f3c8f` v18 lifts/400 portraits/fire/sign-up book · `d67383a` v20 outside · **v21** (this commit) = the owner's last corrections.

**The owner's mood at the end:** unhappy with parts of the outside (v20). v21 undid the parts they named (see §3). **Ask before adding more outside changes; show renders first.**

---

## 1. Getting set up (what actually works in this environment)

```
# repo (all files are real files, no LFS)
GIT_LFS_SKIP_SMUDGE=1 git clone --branch handoff-v14 https://github.com/dinopawnz/spire /home/claude/spire_repo
mkdir -p /home/claude/spire /home/claude/viewer
cp -r /home/claude/spire_repo/src/* /home/claude/spire/ ; cp -r /home/claude/spire_repo/src/viewer/* /home/claude/viewer/
# the Coliseum decor + card art (scripts expect /home/claude/dinopawnz/mudwater)
git clone --depth 1 https://github.com/dinopawnz/mudwater /home/claude/mudwater_repo
mkdir -p /home/claude/dinopawnz && ln -sfn /home/claude/mudwater_repo /home/claude/dinopawnz/mudwater
mkdir -p /home/claude/spire/out/cards_small /home/claude/spire/out/hall /home/claude/spire/out/vault /home/claude/spire/out/bio
echo '{"real": 821}' > /home/claude/spire/out/hall/answer.json      # real #62 Founder = forgery 821 (all 1000 pf_ GLBs are in the repo)
echo '{"real": 63}'  > /home/claude/spire/out/vault/answer.json     # real #100 Black Flag = vault slot 63
```
- **npm / pip installs were BLOCKED** this session. jsdom couldn't be installed, so:
  - **three.js**: `git clone --depth 1 --branch r170 --filter=blob:none --sparse https://github.com/mrdoob/three.js /home/claude/three_src` then `git sparse-checkout set build examples/jsm` and `ln -sfn /home/claude/three_src /home/claude/viewer/node_modules/three`.
  - **tests** run in real headless Chrome via `viewer/chrometest.py` (wraps the jsdom test files unchanged).
- Push access: call `add_repo` (owner `dinopawnz`, repo `spire`, access `push`). It worked once GitHub was linked in claude.ai. Pushing from `/home/claude/spire_repo` works.
- **Meshy**: the owner allowed `api.meshy.ai` + `assets.meshy.ai`. Key goes ONLY in `/home/claude/.meshy_key` (umask 077). **Never** in the repo, a build or chat output. ⚠️ The owner pasted the key into chat this session; recommend they regenerate it on meshy.ai. **Balance at end of session: 2,884 credits** (started 4,160).
- Hard-coded paths: `/home/claude/spire` (workspace), `/home/claude/spire_repo` (clone), `/home/claude/viewer` (tests/renders), `/home/claude/meshy` (Meshy downloads), `/home/claude/mudwater_repo`.

## 2. Build → test → render → push

```
cd /home/claude/spire
python3 textures.py > /tmp/t.log            # only if tex/ is missing pieces (the photo textures in tex/ are Meshy-made: keep them)
python3 build_rect.py > /tmp/br.log         # shell, balconies, stairs, gallery ramp, boardwalk  -> out/glb/sp_shell.glb, layout.json
python3 build_lift.py > /tmp/bli.log        # lifts (reads LIFTS from build_rect.py)
python3 build_fakes.py > /tmp/bf.log        # Hall of Fakes (400 slots)
python3 meshy_props.py                       # Meshy models -> out/glb/sp_m_*.glb + meshy_meta.json (only if /home/claude/meshy/models has new ones;
                                             #   the finished sp_m_*.glb are already in the repo root - copy them into out/glb/ instead)
python3 build_lounge.py > /tmp/bl.log       # lounge -> f1_layout.json (needs out/glb/meshy_meta.json!)
python3 npc.py; python3 sprites.py           # speech bubbles / glowing words
python3 build_html.py 22 https://raw.githubusercontent.com/dinopawnz/spire/handoff-v14/ > /tmp/bh.log    # ALWAYS bump the version number
cd /home/claude/viewer
python3 chrometest.py simtest.js  /home/claude/spire/out/spire.html     # remote, lifts, hall flow   -> "ERRORS: none"
python3 chrometest.py roundtest.js /home/claude/spire/out/spire.html    # 4 rounds -> finals -> winner
python3 chrometest.py biotest.js  /home/claude/spire/out/spire.html     # glow layer, LITE
python3 lifttest.py /home/claude/spire/out/spire.html 40 15             # 40 bots ride 15 simulated minutes -> "NO PROBLEMS FOUND"
python3 mmlshot.py O4.json                                               # render the REAL page (see below)
cd /home/claude/spire && python3 sync_to_repo.py "v22: ..." --branch handoff-v14     # safe test branch
#                       python3 sync_to_repo.py "v22: ..."                          # to main = LIVE (only when the owner says so)
```
- **Before pushing:** copy changed source into the repo: `cp spire/*.py spire/*_src.html spire_repo/src/; cp spire/tex/* spire_repo/src/tex/`, and grep the repo for `msy_` (no keys!).
- Before going live on main: rebuild WITHOUT the branch URL (`python3 build_html.py 22`) so files load from main, then sync to main.
- **Renders:** `viewer/mmlshot.py <scene.json>` loads the real spire.html in Chrome, presses LIVE BUILD, then draws the live MML with three.js (`viewer/mmlrender.js`; maps GitHub URLs to local files). Scene JSON: `{"page", "pos" (player position, picks zones), "opts": {"skip": [...substrings...]}, "shots": [{"out","cam","at","fov"}]}`. Cameras are in building coordinates. Examples: `M3.json` (lounge), `O4.json` (outside), `R1.json` (hall), `B2.json` (sign-up book). **The Chrome tab crashes (out of memory) if everything loads** — use `opts.skip` (e.g. `portraits/`, `sp_f2_`, indoor `sp_m_`) for outside/hall shots.

## 3. What changed this session (v15 → v21), and what the owner said

**Owner corrections at the very end (v21, applied):**
- **The sign-up book goes OUTSIDE**: now on the porch in front of the doors (`build_html.py` `'books': [[0.0, FL['lounge'], 37.0, 0]]`). Not yet render-checked out there; check it doesn't crowd the boardwalk/porch lanterns.
- **"Place back the GLBs that were in the water"**: the original Coliseum water decor (acorn houses, mangroves, trunks, glow plants, moonbeams) is back. The Meshy **floating islands/cliffs and bonsai islets are OFF** (`outside.py` flags `ISLANDS = False`, `BONSAI = False`): the owner circled them.
- **"You replaced the card in the top of the build with a book, switch that back"**: the original floating **Mudwater pack + gold & teal rings + teal disk beam** is back (book removed).
- The owner said they "almost want to revert the whole build". Ask what they want to keep before doing more outside work.

**Lounge (floor 1), to their concept `reference/18_lounge_concept.png`. They liked most of this:**
- Photo-quality wet muddy plank floor (Meshy image → `wet_tex.py`/`photo_floor.py` → `tex/wetfloor*.{jpg,png}`), warm photo wood (`tile_photo.py` → `tex/wood_planks.jpg`, `wood_dark.jpg`; faint warm self-glow in `kit.py`).
- Shiny water puddles (Meshy decals `tex/dec_puddle1..3.png`). The owner REJECTED the earlier mud splats with boot prints ("too unrealistic, wanted mudwater puddles").
- **Meshy models** (`sp_m_*.glb`, placed via `mp()` in `build_lounge.py`, solid via `SOLID`): two giant trees (`sp_mtree_1/2`, glowing mushrooms), sofas, wingback armchairs, card tables, stools, barrels, benches, coffee tables, 4 market-stall booths, stone fireplace, pond rim, waterfall grottos (+ rock basins).
- Waterfalls flow continuously (4 sliding sheets `water_fall2.png`, glow `fall_glow.png`, foam `foam.png`).
- **Animated fireplace** (flame cards `fire_flame.png` flicker, embers rise, floor glow pulses: `spire_src.html` "the fireplace").
- Iron lanterns (`sp_lantern_a/b/c`) + big lantern rings (`sp_lantern_ring`) + soft light pools under them; big framed MUDWATER signs on the round bar; gold MUDWATER plaque inlaid in the floor.
- Banners with the real card-back emblem (`tex/banner_mw.jpg`). The old "sun" symbol was made up. The owner LIKES these banners.
- Squared timber trusses. The owner disliked the earlier round "logs"; the thick green moss cones were removed.
- Tall glowing arched windows; floor glow veins removed from the lounge (Hall of Fakes keeps its teal glow).
- Z-fighting fixed (floor layers stacked at different heights: decals ~Y+0.022.., light pools Y+0.065, rugs Y+0.078, dance floor Y+0.09).

**Lifts:** the owner said they "teleport, one door opens, can't get out". Now:
- **Only 2 lifts, the back corners** (`build_rect.py` `LIFTS`: B east, D west). The front ones blocked the Hall of Fakes ramp.
- The cab glides with a synced timed `m-attr-anim` (`glider` → `tween` in `spire_src.html`). **Otherside ignores `m-attr-lerp`**: that was the teleporting.
- Both door leaves open together; invisible gate walls follow the leaves; thick cab floor; speed 1.8 m/s; floor buttons ordered lounge (bottom) → roof (top).
- `viewer/lifttest.py` (40 bots, 15 simulated min) → NO PROBLEMS FOUND. **Still needs a real multi-player ride in Otherside.**

**Hall of Fakes:**
- **400 portraits** (two rows round both laps; `build_fakes.py` `ROW_Y`), 1 real (#62, forgery 821). The owner asked for at least 400.
- **No wood crossing portraits anywhere**: battens and plates are off on walls inside the hall (`rustic_wall(..., battens=False, plates=False)`).
- A ramp continues from the top landing (gallery, y 24.9) up to the stair tower's half landing so you can keep climbing to floor 3 (`build_rect.py` `gallery_ramp`). Render-checked only before it was lengthened, so walk it in Otherside.

**Characters:** NPCs are solid (`pad` in `npc()`); lines updated for 400 portraits, 2 lifts, sign-up book, Mud Royale, Mudroom Escape (`npc.py`).

**Outside (v20, partly reverted in v21).** Currently in:
- deep-brown facade (`plank_ext` in `kit.py`), arched glowing windows (`window(... arch)` in `kit.py`)
- wraparound balconies with carved railings + moss (`belts()` in `build_rect.py`)
- lanterns under every balcony edge, Meshy moss clumps
- two big lounge-style banners on the front (`sp_frontbanner.glb`). The owner asked for these to match the lounge banners exactly.
- gold baroque Meshy frame around the MUDWATER logo; Meshy double doors standing open; no pole in the doorway
- wet dark boardwalk with Meshy carved railings + glowing lantern posts; glowing teal Meshy crystals; Meshy lily pads; mist
- all placed in **`outside.py`** (called from `build_html.py`); `CARTOON` list no longer used
- The floating cards (galaxy) are UNCHANGED — the owner said leave them as is.

## 4. Things the owner REJECTED (never bring back)
Everything in the old list still holds (neon/cosmic, pop-out holograms, blue card backs, rune circles, entrance columns, finals dome, wood across portraits, cards over lift/stair doors, plain/empty floors, wasted space, guard + stealing in the heist, secret room below floor, unrealistic animals). New this session:
- Mud splats with boot prints (wanted real puddles).
- Round pipe-like ceiling "logs"; thick green moss cones.
- Any wood across the portraits (again!).
- The floating book replacing the Mudwater pack on top.
- Meshy floating islands / bonsai near the walkway (circled in their screenshot).
- Removing the original water GLBs.
- A glass lift for hosts in the escape game ("useless, we can't stop and watch").
- Lifts that teleport or only open one door.

## 5. Open to-do list (priority order, as the owner set it)
1. **Ask the owner what to keep** on the outside (v21). Render the porch with the sign-up book outside and send it.
2. **Railings on every open stair edge** (owner screenshot: stair tower landing edge at the lift side, so people don't fall). `stairs()` in `build_rect.py`: add collider + railing on the open landing edges next to the shafts.
3. "**I'm able to walk into this thing**": the owner's screenshot never arrived; ask what it was. Most Meshy furniture + NPCs are now solid; the booths/pond/grotto/trees use hand colliders.
4. **Make the building ~2x bigger floor plan** (owner chose "bigger floor plan", real-size furniture) for 100+ players. Big job: `X1, Z1` in `build_rect.py` (now 42.5 × 30), then everything placed from them; the lounge furniture lists in `build_lounge.py` have fixed coordinates and need spreading; `build_fakes.py` band/runs.
5. **Mud Royale** (floor 3, y 32): spec in the old handoff/§5.2 of git history (territory card game, team version, 2-minute timer, most squares wins, MVP). Ask 3 or 4 teams.
6. **Mudroom Escape** (replaces the old Heist), notes in `src/ESCAPE_TOWER_NOTES.md`: make the tower taller with 6 escape floors × 6 team rooms; solve a puzzle to unlock the door to the next floor (~6 puzzles); players pick one of 6 coloured doors; hosts take an express lift to a Victory Hall at the top; first team out wins → raffle. Hosts watch via a **stair with landings around a glass core** (rooms' inner glass walls kept clear, rooms bright / stair dim) + a 6-screen watch wall. (Proposed; the owner hasn't confirmed the glass-core stair.)
7. **Way cooler NPCs — LAST** (the owner said so). The current ones look "stubby low effort". Pipeline: `meshy_npcs.py` (text/image → 3D → rig → animations), `split_clips.py`. Keep the owner's own ape #5413 as the lift operator; every other character must be an original creature.
8. A real multi-player lift test in Otherside; then push to `main` with a version bump when the owner approves.

## 6. Meshy (how it was used)
- `src/gen.py out.png "prompt" [aspect]`: text-to-image (nano-banana-pro, 9 credits). Aspect ratios: 1:1, 9:16 (1:2 is invalid).
- `src/batch3d.py items.json`: for each item, reference image → image-to-3D (textured PBR, 30 credits) in parallel → `/home/claude/meshy/models/<name>.glb`; log in `models/batch.log`. Item lists: `src/lounge_items*.json`, `src/outside_items.json`, `src/door_items.json`, `src/book_items.json`.
- `src/remesh.py`: Meshy remesh to lower triangle counts (5 credits each) for repeated pieces.
- `meshy_props.py`: shrink textures, add glow (`glow_mask.py`: warm mushrooms/flames, teal crystals, gold), write `out/glb/sp_m_<name>.glb` + `meshy_meta.json` (bounding boxes used for placement/scale).
- Reference images that made each model: `src/meshy_refs/`. Raw Meshy GLBs are NOT in the repo (only the processed `sp_m_*.glb` in the repo root).
- Models made: armchair, balcony, barrel, bench, bonsai, booth, cardtable, cliff, coffeetable, crystals, door, doorleaf, archway, fireplace, grotto, island, lanternpost, lectern, lily, mossclump, pond, railing, signframe, sofa, stool, tome (+ trees `sp_mtree_1/2`). Unused now: tome, island, cliff, bonsai, archway, balcony, door.

## 7. File guide (new/changed this session; the rest as before)
| File | What it does |
|---|---|
| `src/outside.py` | ALL outside dressing (railings, lantern posts, crystals, lilies, mist, banners, sign frame, doors, balcony lanterns, moss); flags `ISLANDS`, `BONSAI` |
| `src/build_lounge.py` | lounge; `mp()` places Meshy props; `SOLID` colliders; `place_lanterns`, `light_pools`, `wet_floor` (puddle decals), `trusses`, `bar_sign`, `floor_plaque`, `iron_lantern`, `lantern_ring` |
| `src/build_rect.py` | shell; `LIFTS` (2), `belts()` = wraparound balconies, arched windows, `plank_ext` outer wood, gallery ramp, wet boardwalk |
| `src/build_fakes.py` | Hall of Fakes, `ROW_Y` two portrait rows (400) |
| `src/spire_src.html` | world logic: lifts (`glider`/`tween`), fireplace, waterfalls, sign-up book, solid NPCs, front banners, sky islands |
| `src/spire_remote_src.html` | remote (lift panel now B + D) |
| `src/npc.py` | character lines (updated) |
| `src/kit.py` / `glb.py` | materials (`wetfloor`, `plank_ext`, warm self-glow), `window(arch)`; `glb.write` supports `mr` roughness maps |
| `src/meshy_props.py`, `glow_mask.py`, `shrink_glb.py` | Meshy model prep |
| `src/wet_tex.py`, `photo_floor.py`, `tile_photo.py`, `bio_amber.py` | texture makers (photo floor/wood/water, amber glow, light pools) |
| `src/viewer/mmlshot.py` + `mmlrender.js` | render the real page |
| `src/viewer/chrometest.py` | run jsdom tests in Chrome |
| `src/viewer/lifttest.py` | 40-bot lift test |
| `src/sync_to_repo.py` | push changed files (now runs the ref check in Chrome; handles branch URLs) |
| `src/ESCAPE_TOWER_NOTES.md` | the Mudroom Escape spec so far |
| repo root `sp_m_*.glb`, `sp_mtree_*.glb`, `sp_lantern_*.glb`, `sp_frontbanner.glb`, `fire_*.png`, `water_fall2.png`, `foam.png`, `fall_glow.png`, `bio/*_amber.png` | the new world assets |

**Size budget:** shell ~392k triangles / 46 MB (grew with balconies + arched windows: watch it); lounge ~127k / 19 MB; Meshy props 0.7–5 MB each. Everyone downloads this, so prefer the same GLB placed many times.
