# MUDWATER SPIRE — handoff

## Status (Nov 4 2026, session 2)
- All build scripts are included here (11 Python files + the preview viewer). Rerun them to regenerate everything (about 2 minutes).
- **Done this session:** the elevators are now INSIDE the tower (to-do #1), everything was regenerated, and screenshots were checked (to-do #2).
- **Not built yet:** spire.html (the MML game), spire_remote.html, Meshy models, ElevenLabs voices, Floor 4 escape room.
- This run's answer keys: **real #62 Founder = hall slot 821**, **real #100 Black Flag = vault slot 63** (seeds 4062 / 9100). Trust out/hall/answer.json and out/vault/answer.json after any rerun.

## The interior lifts (build_lift.py)
- Two octagonal glass-and-brass shafts stand in the hollow core of the Floor 2 helix stair, one on each side of the glass vault, so riders climb through the 1,000 portraits.
  - **Lift A, "The Grand Cage"** at x = +11.6, z = 0. Stops: lounge 3, hall 11, gallery 43, cards 53, deck 62.
  - **Lift B, "The Express"** at x = −11.6, z = 0. Stops: lounge 3, cards 53, deck 62.
  - All doors face +z (toward the front / entrance).
- A single shaft in the dead centre was not possible because the finals vault sits there at y 43.
- **Shaft** (world space, sp_liftA_shaft / sp_liftB_shaft):
  - 8 iron corner columns with brass collars, brass bands every 4 m, glass panes with mullions, and scroll ironwork.
  - A counterweight bay on the back (−z) with guide rails and buffer springs.
  - Skirting at every floor it passes through.
  - At each stop, a carved portal: pilasters, a brass sunburst fan, a floor dial (needle separate), a floor-name plaque, two lanterns and a brass threshold.
  - On top, a machine head: girder frame, motor, gauge and red lamp.
- **Cab** (local, sp_liftA_cab / sp_liftB_cab; origin = floor centre):
  - Octagonal birdcage with turned brass posts, wainscot, a brass handrail, cage bars with scrollwork and light glazing.
  - Green tufted bench round the back three faces, a stained-glass ceiling oculus and a hanging lantern.
  - Operator pedestal with a dial on the front-right diagonal. Floor dials inside and outside above the door.
  - Brass dome, stained-glass cupola, crest finials, crown-gear brackets, rope hitch at +4.35, and a compensating chain underneath.
- **Moving parts** (all separate GLBs; positions in out/lift_layout.json):
  - Cab and landing scissor gates (sp_lift_cgate / sp_lift_lgate): hinge at x = 0, the leaf runs to −x. Fold by scaling x from 1 down to ~0.15. The left leaf uses ry +180.
  - Gate colliders (sp_lift_cgate_col / sp_lift_lgate_col): switch them on while the gates are closed.
  - Spinning parts:
    - sp_lift_sheave: rx spin. The rate is sheave_rad_per_m × cab speed.
    - sp_lift_pinion: rx spin at spin_ratio_pinion × the sheave's rate.
    - sp_lift_gov: ry spin.
    - sp_lift_cabgear ×2 on the cab: rx spin.
  - Cables (sp_lift_cable): 1 m tall, hanging down from the origin; set scale y to the length.
    - Cab ropes: from cab_rope_top down to cab_y + hitch.
    - Counterweight ropes: from cw_rope_top down to the counterweight top.
  - Counterweight (sp_lift_cw): cw_top_y = sheave_y − (rope − (sheave_y − (cab_y + hitch))). x = lift x, z = lift z + cw_z.
  - Dial needles (sp_lift_needle): rotate z. dial_rz gives the angle for each stop, in the same order as stops.
    - Portal needles: portals[].needle, using needle_scale.
    - In the cab: needle_in (ry 180) and needle_out.
  - Operator's lever (sp_lift_lever, rx swing) and the operator NPC spot (cab.operator, operator_ry).
  - Call button (sp_lift_call) and its lit halo (sp_lift_callglow), at portals[].call.
- **Colliders:**
  - sp_lift_col: shaft walls with door openings, plus collars that close the gap between each floor hole and the shaft.
  - sp_lift_cab_col: cab floor, walls and door sill. The cab door side is open; use the gate collider.
  - The floors around the shafts were probed: solid at every door, open inside the shafts.
- **Sounds** (out/snd, synthesized, no assets needed): lift_chime (two-tone bell), lift_gate (rattle and clack), lift_hum (4 s loop), lift_lever.
- **Operator NPC:** Winnie Winch (npc.py key `operator`).
  - Lines: greet, t1–t4, up, down, close, and s_lounge / s_hall / s_gallery / s_cards / s_deck for each stop.
  - Voice: bright, brassy old-time lift attendant.
- **New sprites:** lift_here, lift_coming, lift_full, lift_express, lift_finalists, and fl_lounge / fl_hall / fl_gallery / fl_cards / fl_deck. The lift_e and lift_w signboards were rewritten.


## NPC characters (session 3, Nov 5) — DONE
- Seven rigged and animated characters in out/glb/npc_<key>.glb (1.3–1.9 MB each; 6 MB for the user's ape). Each file holds its mesh, skeleton and animation clips.
  - Play clips by name or index (MML m-model `anim`, or a separate anim GLB).
  - The clip order is listed below.
- Table of characters:

| key | character | made from | clips (in order) |
|---|---|---|---|
| operator | **the user's own ape #5413** (Mutant Ape) — the Grand Cage operator | their GLB → Meshy rig (lost its materials) → fix_ape.py put all 7 original materials back | Idle, Talk_with_Hands_Open, Formal_Bow, Wave_One_Hand, Cheer_with_Both_Hands_Up |
| ferryman | Ferryman Moss — old snapping turtle in an oilskin | text → 3D | Idle_02, Talk, Wave, Bow |
| barkeep | Mama Silt — bullfrog barkeep | concept picture → 3D (text kept giving humans) | Idle, Talk_with_Right_Hand_Open, Stand_and_Drink, Wave |
| gator | Gator Pete — big alligator in overalls | text → 3D | Idle_03, Talk, Shrug, Big_Wave_Hello |
| skipper | Old Skipper — elderly gorilla sea captain | concept picture → 3D | Idle_03, Talk_with_Left_Hand_Raised, Wave, Victory_Cheer |
| appraiser | The Appraiser — raccoon in tweed with a monocle | text → 3D | Idle, Talk_with_Right_Hand_Open, Gentlemans_Bow, Shrug |
| dealer | The Dealer — opossum with a green visor | text → 3D | Idle_01, Stand_and_Chat, Talk, Cheer |

- Scripts:
  - meshy_npcs.py: resumable; task ids are kept in out/meshy/state_<key>.json; the key is read from /home/claude/.meshy_key.
  - fix_ape.py
  - shrink_glb.py: re-encodes the embedded textures to 1024 px.
- Meshy credits: 4,404 → 4,160.
- The user has ONLY their own ape. Every other character is generated, and they must stay original creatures, not copies of other BAYC apes.
- Name or voice for the user's ape character: ask (npc.py still calls the operator "Winnie Winch").
- ElevenLabs key: the first key lacked permissions. It needs Text to Speech, Voices (read + write), Sound Effects and Music.
  - It is stored at /home/claude/.eleven_key (that copy will be lost in a reset; the user re-pastes it).


## spire.html v1 + spire_remote.html (session 3) — WORKING (tested in a simulated world + a live networked-dom server)
- Source: spire_src.html (the template).
  - `python3 build_html.py <ver> [BASE] [--voices]` bakes every position from out/*.json into out/spire.html.
  - BASE defaults to https://raw.githubusercontent.com/dinopawnz/spire/main/ (portraits in portraits/). Same pattern as the castle.
- Built on the castle's core:
  - placer cube with logo, LIVE BUILD / unbuild
  - PIN prompt sp-host, PIN **7747** (S-P-I-R)
  - hidden remote board sp-remote with data-ack / data-game / data-players
  - ZONES (f1 / f2 / f3 / f4 / out by height and radius; the 1000+100 portraits use data-zone="f2")
  - LITE, REFRESH
  - position probe, guest books (name prompt)
- What works:
  - NPCs: click to talk (cycles the t-lines), greet when you walk up (once a minute), talk animation while speaking. VOICES flag for vo_<npc>_<line>.mp3.
  - The bar: click a tap → the handle pulls, beer pours, and the mug slides down the bar to you; Mama Silt says a pour line.
  - The lifts:
    - SCAN logic, call buttons with a glow, floor buttons inside the cab (floor-name pictures).
    - Gates fold, with gate colliders. Chime, gate clank, hum.
    - Gears, sheave, pinion and governor spin. Ropes stretch and the counterweight runs. Dials and the lever move.
    - The operator (the user's ape) announces up / down / every floor.
    - Riders stand on m-cube pads inside the cab group (the castle's riding method).
    - An idle cage goes home to the lounge after 45 s.
  - Hall of Fakes:
    - `hall open` shuffles the portraits.
    - Wrong pick: 20 s lockout with a private FORGERY / WAIT and countdown.
    - Real pick: finalist; the vault door (sp_vault_door.glb + pad) disappears for finalists only.
    - The 10th finalist starts the finals automatically. The first correct vault pick wins: banner, spinning Black Flag, fanfare.
    - `hall thin` halves the remaining fakes (down to 10) in whichever round is running.
    - Finalists' names on two m-label boards (names are the only text).
  - Remote: LIVE BUILD, Hall (open / thin / finals / reset), both lifts to any floor, LITE / REFRESH, player list with "Make finalist".
- Commands: build, unbuild, lite, refresh, hall open|thin|finals|reset, lift A|B <floor>, name <id> <text>, finalist <id>.
- Sounds (synthesized): pour, wrong, found, finals, winner, lift_chime / gate / hum / lever.
- Upload set: spire/upload/ (190 MB: root GLBs + MP3s + portraits/). refcheck.js confirms every referenced file exists.
- Test tools in /home/claude/viewer:
  - simtest.js: jsdom poke test.
  - mmlserver.mjs: a local networked-dom server.
  - remotetest.py: drives the remote in Chrome.
  - mk10.py / shot.py: renders.
- WAITING ON THE USER:
  - (1) Create the GitHub repo `spire` (or use mudwater/spire).
  - (2) mudwater_coliseum.html, for the Floor 3 card game rules.
  - (3) ElevenLabs key permissions.
- Still to build:
  - Floor 3 Gauntlet logic.
  - Floor 4 escape room.
  - Opening show, storm finale and ghost ship.
  - Boats and zipline.
  - Swamp life.
  - Lounge minigames.
  - Music.

## Requirements (unchanged)
- **Event:** OtherGames, Saturday, 100+ players.
- **Look:** a very tall swamp timber tower in the Mudwater theme (image 1, but more epic). No primitives, highest-quality GLBs, reuse the Coliseum swamp GLBs. Use the Dippy's Lost Crown trick for the triangle budget. Images instead of text on signs.
- **Spawn:** origin at the front (foot of the boardwalk), never in the centre.
- **Floor 1 — lounge (image 2):** taps that pour, a barkeep who talks, talking NPCs.
- **Floor 2 — Hall of Fakes:**
  - Solomon spiral stair with 999 fake + 1 real #62 The Founder.
  - Wrong click = 20 s lockout for that player.
  - First 10 correct go to the glass finals vault; everyone else watches through glass.
  - Vault: 99 fake + 1 real #100 Black Flag; first correct click wins.
  - Remote button removes fakes in waves, down to 10 left.
- **Floor 3 — Swamp Gauntlet** (rules from mudwater_coliseum.html):
  - 16 tables, no elimination; play a person or the house Dealer NPC.
  - Win streaks climb a leaderboard; losers re-queue instantly.
  - Host ends it; the top 2 play a final on a centre stage shown on a giant screen.
- **Floor 4 — escape room:** Mudwater-themed riddles and scavenger hunt like Dippy's Lost Crown, run from the host remote.
- **Remote:** same core and style as tsd_remote.html / emberhold_remote.html (networked-dom-v0.1, hidden board, PIN keys, data-* attributes, ack).
- **Lifts:** inside the tower, the best-looking elevators ever. Done; see above.

## Decisions
- I drive Meshy and ElevenLabs via their APIs. **API keys not given yet** — paste them in chat next session.
- New repo dinopawnz/spire, served at dinopawnz.github.io/spire/.
- Domains allowed: api.meshy.ai, assets.meshy.ai, api.elevenlabs.io. npm now works (three.js is used for the previews).

## Layout (the `L` dict in build_shell.py → out/layout.json; keep in sync with spire.html)
- The tower is 3 m wider all round than before. Tower centre at the origin; water at y 0.1; front faces +z. "A" = octagon apothem.
- **Porch:** y 3, A 34.
- **Floor 1:** y 3–11, A 27.
- **Floor 2:** y 11–52, octagon A 24. The Hall's round wall is still r 18.5, the stair's inner edge r 14.3, and the gallery is at y 43.
  - The Hall has one door, at the front, leading out to the Floor 2 terrace. The old side doors and gallery bridges are gone.
- **Floor 3:** y 53–61, A 28, deck to 31. Tables moved out to r 17; the stage stairs are now on the diagonals.
- **Floor 4:** y 62–71, A 25, deck to 28.
- **Roof peak:** y 92.
- **Boardwalk:** 75 m × 6 m at y 0.6; spawn arch at the far end.
- **Lifts:** see `lifts`, `shaft_fp` (footprint polygon), `shaft_apo` 2.3, `cab_apo` 2.05, shaft from 3.0 to 67.6.
- Floor 1 changes: things on the walls moved out 3 m. The sofa groups are at (−4, 7.5) and (15, 12); the card tables are at (17, −8) and (8, −11.5).

## Triangle budget changes
- Big floors (porch, terraces, Floor 3 / 4 decks, lounge) are now one textured surface each (`deck(..., flat=True)`), with holes cut exactly.
- Wall boards are front and back faces only. Railings, windows and pilings are lighter. Inner stilts are sparser.
- The Hall floor, vault and cab keep individual bevelled planks.
- Result: the shell went from 954k triangles / 98 MB to 222k / 22 MB, and the lounge from 196k to 108k.
- New kit helpers:
  - `slab_collider()`: invisible walk-on floors with holes.
  - `flat_deck()`.
  - `subtract()`, `hole_range()`, `hole_poly()`.
- Old bug fixed: the skirt_roof() calls were missing the mesh argument.
- Added colliders that were missing: the Floor 2 Hall floor, the Floor 4 floor, the vault floor, and the ring at the Floor 2 level.

## Exterior
- Eight giant cypress trunks now climb the corners of the Hall tower (iron bands, knots, branch stubs).
- 32 glowing lanterns on iron brackets.
- Moss beards hang from every eave.
- Floor 2 has three bigger windows per face.
- The Coliseum mangrove GLBs (bog_mangrove_tree_a / _b) are root clusters about 22–28 m tall. They looked odd scaled up next to the tower, so placement is left to spire.html (try them part-sunk and small).

## Files
| File | What it does |
|---|---|
| glb.py | Numpy GLB writer and shapes. |
| textures.py | 18 seamless textures with normal maps → spire/tex/. |
| kit.py | Materials, timber parts, flat decks, slab colliders. |
| forge.py | Forgery press (see the build order). |
| build_shell.py | Tower shell, porch, storeys, roofs, crow's nest, logo sign, corner trunks, lanterns, moss, boardwalk, colliders, layout.json. |
| build_lift.py | **New.** Both lifts, all moving parts, colliders, sounds, lift_layout.json. |
| build_f1.py / build_f2.py / build_f3.py | The three floors (updated for the wider tower and the lifts). Floor 2 now has the vault underside and a big chandelier. |
| npc.py | Six NPCs (Winnie Winch added) → speech-bubble GLBs + npc.json. |
| sprites.py | Glowing words, digits, signboards. |
| viewer/view.html + shot.py + scenes.py | Preview renderer: three.js + headless Chrome (swiftshader). `npm install three@0.170.0` in /home/claude/viewer, then `python3 shot.py scenes.json`. |

## Environment notes
- Clone the assets: `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/dinopawnz/mudwater /home/claude/dinopawnz/mudwater` (call add_repo first).
- The card JPGs are real files, not LFS stubs.
- Logo: extract the embedded image from mw_logo.glb → spire/tmp/ext/mw_logo_0.png (snippet: read_glb, then the first image's bufferView).
- **Build order:** textures → logo → forge ×2 (`python3 forge.py 62 999 out/hall 4062`, `python3 forge.py 100 99 out/vault 9100`) → shell → lift → f1 / f2 / f3 → npc → sprites.

## To do
1. ~~Interior elevators~~ ✔
2. ~~Regenerate and check screenshots~~ ✔
3. ~~Meshy NPCs~~ ✔ (props still to do)
4. ElevenLabs voices, then rerun npc.py.
5. Floor 4 escape room (the lift shafts and machine heads stand at x = ±11.6 on that floor).
6. spire.html: all floor logic, lift logic (the call queue, door → chime → gates → ride; cab speed about 2.5 m/s), a hidden remote board, and Dippy's triangle trick (read dippys_lost_crown.html). Players' positions are only known while they stand on the build.
   - Check how moving colliders carry riders in MML.
   - Place the Coliseum swamp scenery.
7. spire_remote.html, including the "thin the fakes" waves.
8. Test, then update the Check My Game checker.

## Session 4 (v7-v9): the rectangle rebuild
- Official games (user spec): G1 Mud Match (200 portraits, 4 rounds = 4 finalists, 5 s wrong-pick wait, finals in a separate room: first to find the real Black Flag wins).
  G2 "Mud v One" 1v1 best-of-3 bracket (user still looking for something better: pitched Mud Royale giant board / Beat-the-Dealer ladder). G3 Group Mud: 6 team rooms, one player per team at a time searches the Mudwater warehouse for clues, first team to enter the code wins, raffle in the winning team.
- New building: build_rect.py (85 x 60 m, floors 3 / 10.5 / 19 / 26.5 / roof 34, stair towers at x = +-34.4..42.1, 4 lifts at z -25, x -15/-5/5/15, steeple, portico).
  build_match.py (F2 gallery: 8 display walls + front/back walls = 200 slots; finals room 18 x 16 glass box with frost sleeve + door). build_lounge.py (F1, old furniture code moved with Mesh.merge transforms, framed cards, columns).
  build_lift.py now writes ONE sp_lift_shaft.glb (placed at each x) + ONE sp_lift_cab.glb. F3/F4 are empty floors for now.
- Outside decor = the Mudwater Coliseum's own GLBs, loaded straight from raw.githubusercontent.com/dinopawnz/mudwater/main/ (list built in build_html.py, D.deco).
- Pending: G2 design decision, G3 build, spectacle (giant ape 5413, holo cards orbit, storm finale, roof slide), ElevenLabs sk_ key.

## Session 5 (v10)
- Levels: lounge 3 | hall 10.5 | gallery 24.9 | cards 32 (Mud Royale) | rooms 40 (Group Mud / Heist) | roof 51. Lifts stop at all six.
- build_hall.py = the Hall of Fakes TOWER (old helix code): centre (0, 3), r 18.5 / 19.1, 3 turns of stair (TH0 180), 200 portraits in 2 rows,
  gallery ring + glass vault (r 9, H 5.5, flat glass ceiling) at 24.9. build_match.py (museum gallery) is retired.
- build_rect.py: rustic boards (uneven, tinted, ragged), X braces, boarded/crooked windows, pent roofs every floor + mid-hall, mansard skirt,
  dormers, chimneys, water tower, balconies, porch shacks, stair cycles (tall storeys get two switchbacks).
- Lifts now move with m-attr-lerp (server sets the value, every client glides it) instead of timed m-attr-anim. Cab floor buttons on a
  panel 0.55 m in from the wall. NPC bubbles: D.npcCap (operator bubble rides inside his cab).
- STAIRS signs over every stair door. Galaxy: 120 holo_NNN.glb (mudwater repo) on 3 tilted spinning rings (D.galaxy).
- Next: Mud Royale (team version, 2-minute timer, like the user's territory_v12.html), the Heist (awaiting yes), wow items.

## Session 5b (v11): swamp magic
- Finals room moved into the hall floor at the centre of the spiral: glass rotunda r 11, 9.5 m walls + 3.2 m dome, 10 radial screens 4-9.6 m out.
  The top of the stair is now a balcony ring (r 11.6-14.3) looking down on the dome. Old top vault is gone (lift stop "gallery" = balcony).
- Galaxy uses gc_001..120.glb (real card art front, Mudwater card back, gold rim, glow) built by build_cards.py, each card slowly turning.
- Show (D.fx): mw_sky dome x3, floating mw_pack x4 over the roof with fx rings + diskbeam, 2 faint moonbeams (sp_moonbeam), 70 will-o'-wisps
  (sp_wisp_t/g) wandering over the water, 42 rising sky lanterns, rune circle + ring on the water, rings round the steeple, motes + fireflies.
  sp_neon.glb = warm string lights under every eave and down the steeple + glowing mud channel round the porch and boardwalk.
  User rejected neon/cosmic looks for the swamp theme (no neon streaks, no disco beams, no cosmic sky).
- Game 3 (Heist): keep lights-out + clues, NO guard, NO stealing. Living swamp only if photoreal. No speakeasy below the floor.
