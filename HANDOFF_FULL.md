# MUDWATER SPIRE — FULL HANDOFF (read this first)

> Written 5 Nov 2026, end of session 6, for the next AI picking this project up.
> The owner is **Dinopawnz** (GitHub `dinopawnz`).
> **Talk to the owner in plain, non-technical words, with the simplest possible steps.** They said they don't follow technical walkthroughs.
> **Deliver files as attachments in the chat. Never save to their computer.**

---

## 0. The 60-second version

**What it is.** **Mudwater Spire** is a giant swamp-timber building made with MML (Metaverse Markup Language) for Otherside. It's for an **OtherGames event with 100+ players**. The goal, in the owner's words, is to be **"the unquestionable greatest build ever"** and to top their earlier *Pink Princess Castle* build.

**How the world loads.**
- The world document is **`spire.html`**; the host remote is **`spire_remote.html`** (PIN **7747**).
- Every model, sound and picture loads from the public GitHub repo **https://github.com/dinopawnz/spire** through `https://raw.githubusercontent.com/dinopawnz/spire/main/<file>?v=<version>`.
- The swamp decorations come from the owner's other repo **dinopawnz/mudwater** (the Mudwater Coliseum build).

**State: `main` (live).**
- **v13** (commit `fc78aad`) is live on `main`. That's what the owner has in-world now.

**State: branch `handoff-v14`.** Everything made after v13 is pushed to this branch, NOT to main. It has been tested in a simulated browser, but nobody has looked at it in Otherside yet.
- **v14:** the "Pandora" living-swamp glow layer, and no wooden beams across the portraits.
- **The new lounge (half-finished):**
  - giant mossy trees
  - puddles and grass
  - green banners and arched trusses
  - 2 indoor waterfalls and 4 shop booths
  - 46 more hanging lanterns
  - gold glowing veins
- **All source code** in `src/`, and **all the owner's reference images** in `reference/`.

**Next jobs, in order.**
1. Finish and render-check the new lounge against the owner's concept image (§6.1).
2. Rebuild the **outside** to match the owner's newest concept image (§6.2).
3. Build **Game 2, Mud Royale**, on floor 3 (§5.2).
4. Build **Game 3, Group Mud / the Heist**, on floor 4 (§5.3).
5. Put something on the roof.
6. Push to `main` once the owner is happy.

---

## 1. How to get everything (the files)

**Everything** is in the GitHub repo `dinopawnz/spire`, on branch **`handoff-v14`**:

```
/ (repo root)          every GLB / MP3 / PNG the world loads (the world fetches them from here) + spire.html + spire_remote.html
/portraits/            1,100 portrait GLBs (pf_0000..pf_1099) for the Hall of Fakes / finals
/src/                  ALL build scripts (Python) + the HTML templates + textures + card art + test tools
/src/viewer/           test + render tools (jsdom tests, three.js render viewer)
/reference/            every image the owner sent (concepts, screenshots of problems), the rules PDF, the territory game they liked
/HANDOFF_FULL.md       this file
```

Clone it like this:

```
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/dinopawnz/spire /home/claude/spire_repo
cd /home/claude/spire_repo && git checkout handoff-v14
# set up the work folders the scripts expect
mkdir -p /home/claude/spire && cp -r src/* /home/claude/spire/
mkdir -p /home/claude/viewer && cp -r src/viewer/* /home/claude/viewer/ && cd /home/claude/viewer && npm install
# the Coliseum decor and card art
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/dinopawnz/mudwater /home/claude/mudwater_repo
```

The scripts use these hard-coded paths. Keep them the same, or search-and-replace:

| Path | What lives there |
|---|---|
| `/home/claude/spire` | workspace: scripts, `tex/`, `cards/`, `out/` = build output |
| `/home/claude/spire_repo` | the git clone |
| `/home/claude/viewer` | tests and renders |
| `/home/claude/mudwater_repo` | the Coliseum repo |

Built GLBs land in `out/` and `out/glb/`, sounds in `out/snd/`, glow textures in `out/bio/`.

---

## 2. HOW TO UPLOAD GLBs STRAIGHT TO THE OWNER'S GITHUB (no manual uploading)

The owner does **not** want to drag files into GitHub by hand. Push them yourself.

### A. If you are Claude (claude.ai / Claude Code with the GitHub connector)

1. Call the tool **`add_repo`** with `owner: "dinopawnz"`, `repo: "spire"`, `access: "push"`.
   - It attaches the repo, sets up the credentials, and gives you a clone command. Do NOT pre-check the repo with curl first.
2. Clone it (command above), then `git config user.name` / `user.email` as the tool suggests.
3. After building, run the sync script. It finds every file the built world uses, copies only the new or changed ones into the clone, then commits and pushes:
   ```
   cd /home/claude/spire
   python3 build_html.py 15                       # 15 = the new version number (cache-buster)
   python3 sync_to_repo.py --dry                  # see what will be sent
   python3 sync_to_repo.py "v15: lounge + outside" --branch handoff-v14   # safe, NOT live
   python3 sync_to_repo.py "v15: lounge + outside"                        # to main = LIVE in Otherside
   ```
4. **Always bump the version number** (`build_html.py <ver>`). Every URL then gets a new `?v=`, so Otherside and GitHub's ~5-minute cache serve the fresh files.

### B. If you are another AI or a plain computer

1. The owner makes a **fine-grained personal access token** at GitHub → Settings → Developer settings → Fine-grained tokens:
   - Repository access: only `dinopawnz/spire` (and `mudwater` if needed).
   - Permissions: Contents = Read and write.
2. Store it in a private file (`umask 077; echo TOKEN > ~/.gh_token`). **Never** put it in a build file, the repo, a deliverable or chat output.
3. Point the clone at it:
   ```
   git remote set-url origin https://x-access-token:$(cat ~/.gh_token)@github.com/dinopawnz/spire.git
   ```
   Then `sync_to_repo.py` works exactly as in A.
4. Without git, the GitHub REST API also works: `PUT /repos/dinopawnz/spire/contents/<path>` with base64 content plus the old file's `sha`. It's slower, and git is better for big batches.

### Rules

- **The 100 MB per-file limit.** Keep GLBs well under it. `shrink_glb.py` re-encodes the textures smaller.
- **The lounge GLB is now 18.6 MB at 195k triangles.** Don't let it grow much more.
- **The repo is PUBLIC.** No keys, tokens or private screenshots go in it.
- **Pushing to `main` changes the live world.** Use a branch for experiments, and only merge or push to main when the owner says it's good.

---

## 3. The owner — preferences and how to work with them

- **Plain words, simple steps.** No jargon in replies. Say what changed and what they'll see.
- **Files go as chat attachments**: renders, the html, zips.
- **They test in Otherside themselves.** They paste the raw GitHub link of `spire.html` into their world, and use `spire_remote.html` as the host remote.
- **They react to screenshots.** Render previews (§8) and send them so they can judge before testing.
- **They want a SPECTACLE**: "wow everyone", "not boring", "not plain". But it must fit a **swamp / Mudwater** theme with a **rustic wooden** feel.

### Things they REJECTED (never bring back)

| Rejected | What to do instead |
|---|---|
| Neon or cosmic looks: neon streaks, disco or laser beams, a purple cosmic sky ("does that fit a swamp?") | Warm, natural swamp magic |
| Pop-out holograms (images coming out of cards) | Floating *cards* themselves |
| Blue card backs | Cards must look exactly like real Mudwater cards (real art front, real black-and-gold back) |
| A big summoning or rune circle on the ground, runes on the steeple | Nothing there |
| Columns or logs blocking the entrance | Keep the entrance clear |
| A dome over the finals room | No dome. An invisible lid stays so nobody jumps in, frosted until the finals |
| Wooden beams across the portrait walls | No battens on the Hall of Fakes walls |
| A card floating oddly on the lounge wall over a door | No cards behind the lifts or over the stair doors |
| A plain or empty first floor; a bar "randomly on the left" | Centre bar, a full room |
| Wasting space (the old spiral used a small part of the big building) | Use the whole building |
| Empty upper floors | Fill them |
| A guard with a searchlight and stealing in the Heist ("too many mechanics that can go wrong") | Lights-out and clues only |
| A secret room BELOW the floor | No elevation possible. A secret room behind a bookcase was offered; no answer yet |
| Living swamp animals (gators etc.) unless they are extremely realistic | Leave them out |

### Things they LIKED

- Framed Mudwater cards as wall decorations.
- The square building.
- The rustic timber look.
- The Mud Royale idea.
- The 120 floating Mudwater cards circling the building like a galaxy.
- The "Pandora / Avatar" idea: the floor breathes and glows, lights up under your feet, and the walls glisten as you pass.
- Their two concept images (§6).

---

## 4. Security and API keys

The owner pasted a **Meshy** API key and an **ElevenLabs** key in an earlier chat.

- They were stored ONLY in `/home/claude/.meshy_key` and `/home/claude/.eleven_key` (umask 077). Those copies are gone in a new session.
- **Never** write keys into build files, the repo, deliverables, memory or chat output.
- `meshy_npcs.py` reads the key from that file.
- **ElevenLabs:** the key the owner gave lacked permissions. Voices need a real `sk_...` key with Text to Speech, Voices (read + write), Sound Effects and Music. Voices are NOT done; the NPCs use speech bubbles. `build_html.py <ver> --voices` turns voice lines on once the vo_*.mp3 files exist.
- Meshy credits left ≈ 4,160.

---

## 5. THE GAMES (official spec from the owner)

### 5.1 Game 1 — MUD MATCH in the Hall of Fakes — BUILT and working (v13)

**The hunt.**
- 200 portraits of **#62 "The Founder"** hang beside a winding stair. 199 are forgeries and 1 is real; a reference portrait stands on pillars.
- **4 rounds.** The first person to click the real one each round becomes a **finalist** (4 finalists in total).
- After each find, everything **reshuffles** and the next round starts.
- A wrong click locks that player out for **5 seconds**.

**The finals.**
- They happen in a **big, tall, non-claustrophobic glass finals hall in the centre of the Hall of Fakes floor**, on an island in a glowing moat. The owner asked for "WAY bigger, in the centre, tall and wide".
- The finals hall holds **99 fake + 1 real #100 "Black Flag"**. The first finalist to click the real one wins.
- The glass is **frosted until the host presses START THE FINALS**. Everyone else watches through the glass.

**The remote (Hall panel).** OPEN MUD MATCH, NEXT ROUND NOW, AUTO NEXT ROUND toggle, THIN (removes fakes), START THE FINALS (lights up when ready), Reset.

**In code:** `H.round`, `FINALISTS = 4`, `LOCKOUT_MS = 5000`, `ROUND_GAP_MS = 10000`; commands `hall open | next | auto on | auto off | thin | finals | reset`. Answer keys are in out/hall/answer.json and out/vault/answer.json (forge seeds 4062 / 9100).

### 5.2 Game 2 — MUD ROYALE on floor 3 ("cards", y 32) — APPROVED, NOT BUILT

**Basis.** The owner's own `reference/territory_v12.html` (a territory card game), as a **team** version.

**The board.** A **giant board on the floor** (about 100 squares). Players play Mudwater cards onto squares to **capture squares by the Mudwater card rules**. The rules are in `reference/Mudwater_Rules_Sheet.pdf`, `src/cards/cards.json` and `src/mudwater_sim.py`.

**Changes from territory_v12.**
- No flooding edges.
- A **2-minute timer**; when it ends, the **team with the most squares wins**.
- Show an MVP.

**Open question for the owner: 3 teams or 4?**

**Design notes so far (not approved in detail):**
- a hand of 5 cards per player
- team-coloured squares
- a big scoreboard and timer sign
- a host remote panel: start, stop, reset, teams
- Old helper GLBs from an earlier table version are in the repo (`sp_gt_*.glb`: table, squares, rims, highlight) and may be reused.

The floor is empty right now apart from the lift lobbies and stairs.

### 5.3 Game 3 — GROUP MUD / THE HEIST on floor 4 ("rooms", y 40–51) — APPROVED, NOT BUILT

**The basic game.**
- 6 team rooms (hideouts).
- **One player per team at a time** goes into the **Mudwater warehouse** to search for **clues**.
- The first team to enter the right **code** on their console wins.
- Then a **raffle among the winning team**, for a pack.

**Keep:** **lights-out** (dark warehouse, lantern / flashlight feel) plus clues.

**NO guard searchlight and NO stealing.** These are the owner's words.

The owner wants it "SOOOO AMAZING, not a boring escape room".

**Reference for riddles and remote style:** their earlier `dippys_lost_crown.html` and `dippys_lost_crown_remote.html` (escape room / scavenger hunt). Those were uploaded to the old chat and are NOT in this repo. Ask the owner to re-send them if needed.

### 5.4 Other spec bits

- Spawn is at the **front**, at the far end of the boardwalk (never in the centre).
- **Lifts:** 4 real elevators at the building's sides; everyone in the cab rides together like a real elevator.
  - The owner reported that the OLD lifts only carried 1 player and teleported others. They were rewritten to glide with `m-attr-lerp`, so every client moves the same cab smoothly.
  - **The new lifts still need a multi-player test in Otherside.**
- **Backup stairs must exist**: two stair towers at the ends of the building.
- **Buttons in the cab must be clickable** (not sunk in the floor).
- **NPC speech bubbles must never be hidden.**

---

## 6. THE OWNER'S TWO CONCEPT IMAGES (the current visual targets)

### 6.1 Lounge concept — `reference/18_lounge_concept.png`

Sent with "look at this for a first floor look". What's in the image:
- **Giant mossy trees** growing up through the floor into the ceiling, with **glowing shelf mushrooms** on the trunks and **candles** among the roots.
- A **wet, glossy, reflective wooden floor** with **puddles** and **grass tufts**.
- **Many warm hanging lanterns** and **big round lantern rings / chandeliers**.
- **Tall dark green banners with a gold emblem.**
- **A central round bar with a big MUDWATER sign** above it; a MUDWATER logo inlaid in the floor.
- **Indoor waterfalls** at the back.
- **Lit shop booths / stalls with screens** around the edges.
- **Arched timber ceiling trusses.**
- Overall **warm golden light**.

**What's done (branch handoff-v14, `build_lounge.py`):**
- `giant_trees()`: 7 huge trees with flared trunks, snaking roots, moss, vines, branches under the ceiling, glowing shelf mushrooms and candles. They replace the old columns.
- `wet_floor()`: 34 glossy puddles and grass tufts.
- `banners()`: 8 green banners using `tex/banner_mw.jpg`.
- `trusses()`: 4 arched trusses.
- `waterfalls()`: 2 rock-framed falls in the back wall at x = ±13.5 beside the stage, with pools.
  - The moving water sheets are `m-image` (`water_fall.png`) animated in `spire_src.html`, plus mist.
- `booths()`: 4 booths on the back wall — CARD SHOP, MUDWATER MERCH, TROPHY ROOM, PHOTO BOOTH — with green and gold striped awnings, lit counters, screens and glowing sign words (`ms_bt_*.glb`).
- 46 extra jar lanterns hanging at different heights (in `build_html.py`).
- The lounge glow veins and vines are **warm gold** (`bio_veins_gold.png`, `bio_wall_gold.png`); the Hall of Fakes keeps teal.

**Still to do for the lounge:**
1. **Render it** (§8) and compare with the concept. Nobody has looked at the new lounge yet. Fix anything that looks off: tree sizes, trees clashing with furniture or lifts, puddle colour, truss heights, banner placement.
2. A **MUDWATER sign** over the round bar (the bar has logo boards; make it big and glowing like the concept), and a **MUDWATER logo inlaid in the floor** in front of the bar.
3. **Big lantern rings**: chandeliers exist (`D.chand`, `sp_chandelier.glb`); make a few larger ring chandeliers like the concept.
4. Booth **screens** could show card art (`m-image`) instead of plain glass.
5. Check the tests pass. The last test run was interrupted, so run `simtest.js`, `roundtest.js` and `biotest.js` (§8).

### 6.2 OUTSIDE concept — `reference/19_outside_concept.png` (the newest message: "this is how the outside should look")

What's in the image:
- **The building:** a tall, wide, multi-storey **dark wooden building**, warm and glowing. **Rows of lit, warm windows on every storey.** **Wraparound balconies with railings on every level**, with **hanging vines and moss**.
- **The front:** **two tall dark green banners with a gold tree emblem** hanging down the front. A **big glowing gold MUDWATER sign** with an ornate frame over the entrance. An **arched double wooden door** and **wide steps**. Many small lanterns along the eaves.
- **The boardwalk:** a long, **wet, reflective boardwalk** leading straight to the door, with **carved wooden railings** and **lantern posts on the railing posts** all the way down.
- **The water:** dark water with **lily pads (large round pads)** and **glowing teal crystals**, plus mist on the water.
- **Around it:** bonsai-like swamp trees on islands. **Waterfalls** pouring off cliffs and **floating rock islands** with trees.
- **Floating framed pictures (cards) in gold frames, strung together on strands of warm gold lights**, circling the building. This matches our existing 120-card galaxy (`D.galaxy`); add gold light-strand chains linking them.
- **On top:** a **giant glowing Mudwater card/book** floating above the roof, inside **slowly turning golden rings** (with gold glyphs on the rings) and a soft light beam. We already float the Mudwater pack over the roof with 2 rings and a disk beam (`D.fx`); restyle it to match.
- **The sky:** a starry night sky.

**My message to the owner about this (they haven't replied yet):** I said I'd make the outside match, keeping colours **warm gold and natural, not neon**, because they had rejected cosmic and neon looks before. I asked whether they want the **starry sky** too. **Wait for, or ask for, their answer on the starry sky and the floating islands.** Everything else in the image is clearly wanted.

**Where this goes in code:** `build_rect.py`, the shell.
- Windows: `bay_spec` / `rustic_wall` holes.
- Balconies: currently a few `balconies()` exist; make them wrap every storey.
- Banners: the texture `tex/banner_mw.jpg` already exists.
- The MUDWATER sign: the `mw_logo` decor and `D.signs`.
- Portico and door, steps.
- `build_html.py`: boardwalk lanterns (decor `mwx_lantern` / lantern posts), lily pads (`lilypads`), crystals, waterfalls and floating islands (could use Coliseum decor or new GLBs), the galaxy light-strands, and the roof card plus rings (`D.fx`).
- Keep the triangle count sane: the shell is 222k triangles.

---

## 7. THE BUILDING (current geometry)

**Footprint:** a rectangle ≈ **85 × 60 m**, centred on the origin. The front faces **+z**. Water is at y ≈ 0.1. The boardwalk comes from the front (spawn at walk z ≈ 108).

**Levels** (`FL` in `build_rect.py`): **lounge 3.0 | hall 10.5 | gallery 24.9 | cards 32.0 | rooms 40.0 | roof 51.0**.
- Full floors: `KEYS = lounge, hall, cards, rooms, roof`.
- `gallery` 24.9 is the top landing of the Hall of Fakes stair plus a slab in the east core (x 34.4..42.1, z 9.5..29.6). Only lift A stops there.

**Lifts** (`LIFTS` in `build_rect.py`; doors face +z):

| Lift | Position (x, z) | Stops |
|---|---|---|
| A "The Grand Cage" | (38.25, 14) | 6 stops, incl. gallery (`sp_lift_shaft_g.glb`) |
| B | (38.25, −20) | 5 stops (`sp_lift_shaft.glb`) |
| C | (−38.25, 14) | 5 stops |
| D | (−38.25, −20) | 5 stops |

- One cab model `sp_lift_cab.glb` serves all lifts.
- Lift speed is 2.4 m/s; m-attr-lerp gliders move the cab y, ropes, counterweight and needles.
- The floor-button panel sits 0.55 m in from the wall.
- The operator NPC (the owner's own ape #5413) rides in lift A only.
- Lift music is synced per lift.

**Stairs:** stair towers at x = ±34.4..42.1, z −9.5..9.5. Tall storeys get several switchbacks.

**Shell style** (`build_rect.py`):
- rustic uneven boards, X-braces, crooked windows
- pent roofs and belts at 10.5, 17.7, 24.9, 32 and 40; mansard, dormers, chimneys, water tower, balconies, porch shacks
- portico with only the 2 outer columns (±8)
- a steeple at the back centre, and lift-head houses on the roof
- `sp_neon.glb` = warm string lights under the eaves and down the steeple, plus a glowing mud channel round the porch and boardwalk

**Hall of Fakes** (`build_fakes.py`):
- A 4 m wide stair-ramp band runs 2 laps round all four walls. It goes from y 13.7 (grand steps up from the hall floor at the east-front) to 24.9 (the top landing, then a door into the east core).
- 200 portraits (1.3 m) hang on the walls beside the runs.
- The open hall inside is 60.8 × 51.2 m and 21 m tall.
- The finals hall is a glass box x ±13, z ±10, 9.5 m tall, with an invisible lid collider and a frosted sleeve. It has 10 screens in 2 rows of 5 and sits on an island in a 3.2 m glowing moat, with a bridge to the front door.
- Big chandeliers hang from the ceiling.

**Lounge** (`build_lounge.py`):
- the round centre bar (BAR_C (0, 1), radius 5.6 / 4.5, 8 taps; the beer mug slides to the edge nearest the player)
- a stage and dance floor at the back centre, and a jukebox
- a fireplace on the front wall
- a bayou garden with a pond at (−25, 4)
- sofa groups, card tables, framed Mudwater cards on the walls
- plus the new trees, puddles, banners, trusses, waterfalls and booths (§6.1)

**NPCs** (rigged and animated by Meshy, `npc_<key>.glb`, with `_idle` and `_talk` clips):

| NPC | Where |
|---|---|
| operator = the owner's own ape #5413 | lift A |
| barkeep Mama Silt (bullfrog) | at the bar |
| gator Gator Pete | lounge |
| appraiser (raccoon) | Hall of Fakes door |
| skipper (old gorilla captain) | roof |
| dealer (opossum) | floor 3 |
| ferryman Moss (turtle) | outside |

- Lines are in `npc.py`; speech bubbles are `sb_*.glb`.
- **The owner has only their own ape; every other character must stay an original creature.**

**The show and decor** (`build_html.py` → `D`):
- `D.deco`: Coliseum GLBs from the mudwater repo — water, lake, mangroves, acorn houses, a cypress ring, lantern posts, glow plants, reeds, lily pads, rowboats, floating lanterns, fireflies, mist, braziers, jar lanterns, shelf mushrooms, and `mw_logo` on the portico.
- `D.galaxy`: 120 real-card GLBs (`gc_001..120.glb`, real front plus the real black-and-gold back `mwc_back.jpg`, gold rim) on 3 slowly turning rings round the building.
- `D.fx`: swamp sky, the Mudwater pack floating at (0, 90, 4) with 2 rings and a disk beam, 2 faint moonbeams, 70 will-o'-wisps, 42 rising sky lanterns, motes and fireflies.
- `D.bio` (v14 "Pandora" layer):
  - glowing vein tiles on every floor and stair run, breathing slowly (emissive ping-pong)
  - glowing vines on the walls and 54 rising spores
  - **footsteps bloom with light** (`bio_ring`) and **walls shimmer as you pass** (`bio_sheen`), from the position probe
  - all of it is skipped in LITE mode

**Modes and zones:** `visible-to` zones (f1..f4 bands by height); **LITE** removes ~770 decor pieces for weak computers; **REFRESH**.

---

## 8. HOW TO BUILD, TEST AND RENDER

**Build order** (from `/home/claude/spire`; send output to log files, never pipe into `head`, which breaks the json writes):

```
python3 textures.py            > /tmp/t.log    # textures -> tex/ (only if missing)
python3 build_rect.py          > /tmp/br.log   # shell -> out/sp_shell.glb, layout.json
python3 build_lift.py          > /tmp/bli.log  # lifts -> lift_layout.json
python3 build_fakes.py         > /tmp/bf.log   # Hall of Fakes (+ --portraits to remake pf_ GLBs)
python3 build_lounge.py        > /tmp/bl.log   # lounge -> f1_layout.json
python3 build_cards.py                          # galaxy cards gc_*.glb (only if changed)
python3 build_fx.py                             # wisps, moonbeams
python3 npc.py; python3 sprites.py              # speech bubbles, glowing words (ms_*, ms1_*, sg_*)
python3 build_html.py 15       > /tmp/bh.log   # bakes everything into out/spire.html + out/spire_remote.html (15 = version)
```

**Forgeries** (once): `python3 forge.py 62 999 out/hall 4062` and `python3 forge.py 100 99 out/vault 9100`.

**Tests** (in `/home/claude/viewer`; each takes the page path as its first argument):

```
node simtest.js   /home/claude/spire/out/spire.html     # remote, lifts, hall flow
node roundtest.js /home/claude/spire/out/spire.html     # 4 rounds -> finals -> winner
node biotest.js   /home/claude/spire/out/spire.html     # glow layer, footstep blooms, LITE
node refcheck2.js /home/claude/spire/out/spire.html /home/claude/spire/out   # every referenced file exists
```

**Renders:** `viewer/shot.py` with `view.html` (three.js 0.170 in headless Chrome). Scene JSON lists models `{f, p, ry, s}`, `cam`, `at`, `fov`, `night`, `lights`; examples are `s1.json`..`s12.json`. Run `python3 shot.py s12.json` and send the PNGs to the owner.

**Live test without Otherside:** `viewer/mmlserver.mjs` (a networked-dom server) plus `remotetest.py`.

---

## 9. FILE GUIDE (`src/`)

| File | What it does |
|---|---|
| glb.py | numpy GLB writer + shapes (lathe, tube, box, quads, merge with matrices) |
| kit.py | materials (M_), timber parts, decks, slab colliders |
| textures.py | seamless textures + normal maps → tex/ |
| build_rect.py | the building shell, roofs, stairs, porch, boardwalk, neon string lights, layout.json (backups: build_rect_v9.py / _v12.py) |
| build_lift.py | lift shafts, cab, gates, gears, ropes, colliders, sounds |
| build_fakes.py | the Hall of Fakes (stair band, portraits, finals hall, moat, frost) |
| build_lounge.py | floor 1 (bar, stage, garden, fireplace, NEW trees, puddles, banners, trusses, waterfalls, booths) |
| build_cards.py | the 120 floating Mudwater cards |
| build_fx.py | wisps, moonbeams, fx textures |
| forge.py | makes the forged portraits |
| npc.py / sprites.py | NPC speech bubbles / glowing words and signboards |
| meshy_npcs.py, fix_ape.py, shrink_glb.py, split_clips.py | NPC model pipeline |
| lift_music.py | lift music |
| mudwater_sim.py, read_cards.py, cards/ | the Mudwater card game rules and card data (for Mud Royale) |
| build_html.py | collects every layout into the data object `D` and writes out/spire.html + spire_remote.html |
| spire_src.html / spire_remote_src.html | the world and remote templates (all game logic lives here) |
| sync_to_repo.py | **pushes new or changed files to GitHub** (§2) |
| build_f1/f2/f3.py, build_shell.py, build_hall.py, build_match.py | OLD octagon-tower versions, kept for reference only |
| viewer/ | tests + render tools |

---

## 10. REFERENCE IMAGES (`reference/`)

| # | File | What it shows / why it matters |
|---|---|---|
| 04 | 04_spawn_circle.png | Old build: a yellow glowing ring on the boardwalk (circled). Unwanted circle effects |
| 05, 12 | 05_other_build_neon.png, 12_… | **Someone else's** flashy neon event build. The owner's "look how crazy this is, we need to elevate super hard". Matches the ambition, NOT the neon style |
| 06 | 06_old_lounge_bar.png | Old lounge bar with the MUDWATER sign (bar was "randomly on the left") |
| 07 | 07_floor_glitch.png | Lounge: a circled odd floating/blue shape (one of the "weird thing" complaints) |
| 08 | 08_old_hall_helix.png | Old helix Hall of Fakes with counters |
| 09 | 09_old_finals_vault.png | Old small finals vault (too claustrophobic, so it was made huge) |
| 10 | 10_framed_cards_liked.png | Framed Mudwater cards on a wall. **Liked**, keep this decoration |
| 11 | 11_spiral_portraits.png | The spiral with portraits ("put the finals in the centre, way bigger") |
| 13 | 13_sky_test.png | Sky test with neon lightning ("what is this"). Rejected cosmic look |
| 14 | 14_blue_card_backs.png | Floating cards circled: blue backs. **Rejected**, must be real black/gold backs |
| 15 | 15_neon_beams.png | Pink neon beams on the water. Rejected |
| 16 | 16_entrance_columns.png | Columns circled blocking the entrance. Removed |
| 17 | 17_beam_through_portraits.png | Wooden beam through the portraits, plain wood. Led to the Pandora glow idea and no battens |
| 18 | **18_lounge_concept.png** | **THE LOUNGE TARGET** (§6.1) |
| 19 | **19_outside_concept.png** | **THE OUTSIDE TARGET** (§6.2), the newest message |
| — | Mudwater_Rules_Sheet.pdf | The official Mudwater card rules (for Mud Royale) |
| — | territory_v12.html | The owner's territory card game, the basis for Mud Royale |

Images 01–03 were the owner's own Meshy, ElevenLabs and GitHub dashboard screenshots. They're not needed and are left out of the public repo on purpose.

---

## 11. TO-DO LIST (priority order)

1. **Lounge:** render, compare with concept 18, fix; add the big MUDWATER bar sign, the floor logo inlay and big lantern rings; run all 4 tests.
2. **Outside** to match concept 19:
   - lit windows on every storey, wraparound vine balconies
   - 2 green gold-emblem banners on the front, a big glowing MUDWATER sign
   - an arched double door and wide steps, a wet boardwalk with lantern posts
   - lily pads, glowing crystals, waterfalls
   - gold light-strands linking the galaxy cards
   - a giant card in turning gold rings over the roof
   - Ask about the starry sky and floating islands. Stay warm gold, not neon.
3. Send renders, then push to branch, then the owner tests, then push to `main` with a version bump.
4. **Mud Royale** (floor 3): ask 3 or 4 teams, then build the board, cards, capture rules, 2-minute timer, scoreboard, MVP and remote panel.
5. **Heist / Group Mud** (floor 4): 6 hideouts, a dark warehouse, clues, a code console per team, a winner raffle, a remote panel. No guard, no stealing.
6. **Roof:** put something there (the owner said upper floors must not be empty).
7. Optional: secret bookcase room (offered, no answer); ElevenLabs voices (needs the sk_ key); photoreal wildlife only if it can truly look real.
8. A multi-player lift test in Otherside (the owner).

**Triangle and size budget:** shell ~222k triangles; lounge 195k / 18.6 MB; Hall of Fakes ~? (see `/tmp/bf.log` after a build). Everyone on the event has to load this, so prefer textures and instancing (the same GLB placed many times) over unique heavy meshes.
