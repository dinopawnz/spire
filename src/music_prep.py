"""THE SWAMP RADIO - real 1920s New Orleans / dixieland jazz records for the Spire's background music (owner: "something real").
Every record is a US public-domain sound recording (published 1925 or earlier) taken from Wikimedia Commons, where each file page
marks it Public domain. This cleans them up for a game world: trims the dead groove at the ends, rolls off the rumble and the
78 rpm hiss, softens clicks, levels them to the same loudness, mono 96 kbps mp3 -> out/snd/radio_NN.mp3.
Writes src/music_tracks.json: [[file, ms, title, artist, year, source url]] (build_html.py reads it into D['music'])."""
import json, os, subprocess, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-claude/5ddaad6a-f847-5413-a277-78b451d1faa9/scratchpad/music2/'
OUT = '/home/claude/spire/out/snd/'
# (downloaded file, title, artist, year, Commons file page)
TRACKS = [   # (v30, owner: "is there a better song?") clean modern studio recordings instead of the scratchy 78s:
    # U.S. military jazz bands (works of the U.S. government = public domain) + Kevin MacLeod (CC BY 3.0, credited on the remote)
    ('d01.audio', 'Panama', 'USAF Heritage of America Dixie Players', 2002, 'File:Panama - Dixie Players - United States Air Force Heritage of America Band.mp3'),
    ('d02.audio', 'That Da-Da Strain', 'USAF Heritage of America Dixie Players', 2002, 'File:That Da-Da Strain - Dixie Players - United States Air Force Heritage of America Band.mp3'),
    ('d03.audio', 'Tiger Rag', 'USAF Heritage of America Dixie Players', 2002, 'File:Tiger Rag - Dixie Players - United States Air Force Heritage of America Band.mp3'),
    ('d04.audio', "After You've Gone", 'U.S. Coast Guard Band', 0, "File:After You've Gone - U.S. Coast Guard Band.ogg"),
    ('d06.audio', 'Way Down Yonder in New Orleans', 'U.S. Coast Guard Band', 0, 'File:Way Down Yonder In New Orleans - U.S. Coast Guard Band.ogg'),
    ('d07.audio', 'Sweet Georgia Brown', 'U.S. Army Jazz Ambassadors', 2017, 'File:US Army Jazz Ambassadors Sweet Georgia Brown.opus'),
    ('d08.audio', 'Blues for Mundy', 'USAF Airmen of Note', 2011, 'File:Blues for Mundy - Airmen of Note - United States Air Force Band.mp3'),
    ('k00.audio', 'Whiskey on the Mississippi', 'Kevin MacLeod (incompetech.com, CC BY 3.0)', 2010, 'File:Whiskey on the Mississippi (ISRC USUAN1100709).mp3'),
    ('k01.audio', 'Porch Blues', 'Kevin MacLeod (incompetech.com, CC BY 3.0)', 2006, 'File:Porch Blues (ISRC USUAN1100108).mp3'),
    ('k02.audio', 'Night on the Docks (Sax)', 'Kevin MacLeod (incompetech.com, CC BY 3.0)', 2005, 'File:Kevin MacLeod - Night on the Docks - Sax.ogg'),
    ('k04.audio', 'Slow Burn', 'Kevin MacLeod (incompetech.com, CC BY 3.0)', 2009, 'File:Slow Burn (ISRC USUAN1100609).mp3'),
]
SKIP = set(os.environ.get('SKIP', '').split(','))

def dur_ms(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return round(float(r.stdout.strip()) * 1000)

out = []
for (src, title, artist, year, page) in TRACKS:
    if src in SKIP or not os.path.exists(SRC + src) or os.path.getsize(SRC + src) < 100000: print('skip', src, title); continue
    n = len(out); dst = OUT + 'jazz_%02d.mp3' % n
    trim = 'silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.2'
    af = ','.join([
        'aformat=channel_layouts=mono', 'highpass=f=35',
        trim, 'areverse', trim, 'areverse',                                 # dead groove off both ends
        'loudnorm=I=-17:TP=-1.5:LRA=11',
        'afade=t=in:d=0.4'])
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', SRC + src, '-af', af, '-ar', '44100', '-ac', '1', '-b:a', '96k', dst], check=True)
    # a short fade at the very end
    ms = dur_ms(dst)
    tmp = dst + '.tmp.mp3'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', dst, '-af', 'afade=t=out:st=%.2f:d=1.2' % max(0, ms / 1000 - 1.2), '-b:a', '96k', tmp], check=True)
    os.replace(tmp, dst); ms = dur_ms(dst)
    out.append(['jazz_%02d' % n, ms, title, artist, year, 'https://commons.wikimedia.org/wiki/' + page.replace(' ', '_')])
    print('%s  %-24s %-36s %d  %.1fs  %dKB' % (out[-1][0], title, artist, year, ms / 1000, os.path.getsize(dst) // 1024))
json.dump(out, open('/home/claude/spire/music_tracks.json', 'w'), indent=1)
print('tracks', len(out), 'total %.1f min' % (sum(t[1] for t in out) / 60000))
