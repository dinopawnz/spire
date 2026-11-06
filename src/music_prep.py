"""THE SWAMP RADIO - real 1920s New Orleans / dixieland jazz records for the Spire's background music (owner: "something real").
Every record is a US public-domain sound recording (published 1925 or earlier) taken from Wikimedia Commons, where each file page
marks it Public domain. This cleans them up for a game world: trims the dead groove at the ends, rolls off the rumble and the
78 rpm hiss, softens clicks, levels them to the same loudness, mono 96 kbps mp3 -> out/snd/radio_NN.mp3.
Writes src/music_tracks.json: [[file, ms, title, artist, year, source url]] (build_html.py reads it into D['music'])."""
import json, os, subprocess, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-claude/5ddaad6a-f847-5413-a277-78b451d1faa9/scratchpad/music/dl/'
OUT = '/home/claude/spire/out/snd/'
# (downloaded file, title, artist, year, Commons file page)
TRACKS = [
    ('08.mp3', 'Panama', 'New Orleans Rhythm Kings', 1922, 'File:Panama (1922 sound recording).mp3'),
    ('11.mp3', 'Tin Roof Blues', 'The Original Memphis Five', 1923, 'File:Tin Roof Blues - Victor 19170 - The Original Memphis Five.mp3'),
    ('06.ogg', 'Krooked Blues', "King Oliver's Creole Jazz Band", 1923, 'File:King Oliver\'s Creole Jazz Band-- "Krooked Blues" (1923).ogg'),
    ('02.flac', 'Dippermouth Blues', "King Oliver's Creole Jazz Band", 1923, "File:Dippermouth Blues - KING OLIVER'S JAZZ BAND.flac"),
    ('03.mp3', 'Farewell Blues', 'The Virginians', 1923, 'File:Farewell Blues (1923 sound recording).mp3'),
    ('04.mp3', "Jazzin' Babies Blues", 'Richard M. Jones', 1923, "File:Jazzin' Babies Blues - Richard M Jones (1923).mp3"),
    ('00.mp3', '31st Street Blues', "Henderson's Club Alabam' Orchestra", 1923, "File:31st Street Blues - Henderson's Club Alabam' Orchestra (1923).mp3"),
    ('09.ogg', 'Riverboat Shuffle', 'Bix Beiderbecke & the Wolverines', 1924, 'File:Riverboat Shuffle - Bix Beiderbecke & Wolverine Orchestra (1924).ogg'),
    ('01.mp3', 'At the Jazz Band Ball', 'Original Dixieland Jass Band', 1918, 'File:At the jazz band ball (1918 sound recording).mp3'),
    ('10.ogg', 'Tiger Rag', 'Original Dixieland Jass Band', 1918, 'File:Tiger Rag ODJB.ogg'),
    ('05.flac', "Ory's Creole Trombone", "Kid Ory's Sunshine Orchestra", 1922, "File:Kid Ory's Sunshine Orchestra - Ory's Creole Trombone.flac"),
    ('07.mp3', 'Memphis Blues', 'Ted Lewis Jazz Band', 1923, 'File:Memphis Blues-Columbia A3813-Ted Lewis Jazz Band.mp3'),
]
SKIP = set(os.environ.get('SKIP', '').split(','))

def dur_ms(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return round(float(r.stdout.strip()) * 1000)

out = []
for (src, title, artist, year, page) in TRACKS:
    if src in SKIP or not os.path.exists(SRC + src) or os.path.getsize(SRC + src) < 100000: print('skip', src, title); continue
    n = len(out); dst = OUT + 'radio_%02d.mp3' % n
    trim = 'silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.2'
    af = ','.join([
        'aformat=channel_layouts=mono', 'highpass=f=70', 'lowpass=f=7800',
        'adeclick=w=40:o=75', 'afftdn=nr=10:nf=-42',
        trim, 'areverse', trim, 'areverse',                                 # dead groove off both ends
        'loudnorm=I=-17:TP=-1.5:LRA=11',
        'afade=t=in:d=0.4'])
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', SRC + src, '-af', af, '-ar', '44100', '-ac', '1', '-b:a', '96k', dst], check=True)
    # a short fade at the very end
    ms = dur_ms(dst)
    tmp = dst + '.tmp.mp3'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', dst, '-af', 'afade=t=out:st=%.2f:d=1.2' % max(0, ms / 1000 - 1.2), '-b:a', '96k', tmp], check=True)
    os.replace(tmp, dst); ms = dur_ms(dst)
    out.append(['radio_%02d' % n, ms, title, artist, year, 'https://commons.wikimedia.org/wiki/' + page.replace(' ', '_')])
    print('%s  %-24s %-36s %d  %.1fs  %dKB' % (out[-1][0], title, artist, year, ms / 1000, os.path.getsize(dst) // 1024))
json.dump(out, open('/home/claude/spire/music_tracks.json', 'w'), indent=1)
print('tracks', len(out), 'total %.1f min' % (sum(t[1] for t in out) / 60000))
