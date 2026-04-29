#!/usr/bin/env python3
"""
Regenerates tracks.js from an iTunes Library.xml export.

Usage:
    python3 generate_tracks.py Library.xml

Outputs:
    tracks.js — track data for the DJ planner
"""

import plistlib, json, sys, os

TARGET_ARTISTS = {
    'William Onyeabor': 'WO', 'The Lijadu Sisters': 'LS', 'Commy Bassey': 'CB',
    'Ibibio Sound Machine': 'IS', 'Khruangbin': 'KB', 'Grace Jones': 'GJ',
    'Daft Punk': 'DP', 'Tim Maia': 'TM', 'Hot Chip': 'HC', 'Amadou & Mariam': 'AM',
    'DjeuhDjoah & Lieutenant Nicholson': 'DN', 'Kaytranada': 'KT',
    'BADBADNOTGOOD': 'BB', 'Poolside': 'PL', 'Bonobo': 'BO', 'Guts': 'GU',
    'Otis Redding': 'OR', 'Charles Bradley': 'CR', 'Masayoshi Takanaka': 'MT',
    'Chicano Batman': 'CI', 'Africa Express': 'AX', 'LCD Soundsystem': 'LC',
    'Evelyn "Champagne" King': 'EK', 'Flying Lotus': 'FL', 'RJD2': 'RJ',
    'Dizzy K': 'DK',
}

def load_bpms(bpm_file='bpms.json'):
    """Load manually curated BPMs from JSON file if present."""
    if os.path.exists(bpm_file):
        with open(bpm_file) as f:
            data = json.load(f)
        return {(b['artist'], b['name']): b['bpm'] for b in data}
    return {}

def generate(library_xml, output='tracks.js'):
    with open(library_xml, 'rb') as f:
        lib = plistlib.load(f)

    bpm_lookup = load_bpms()

    seen = set()
    tracks = []
    local_id = 1

    for t in lib.get('Tracks', {}).values():
        artist = t.get('Artist', '')
        name = t.get('Name', '')
        album = t.get('Album', '')
        duration_ms = t.get('Total Time', 0)
        itid = t.get('Track ID')
        itunes_bpm = t.get('BPM')

        if artist not in TARGET_ARTISTS:
            continue
        key = (artist, name)
        if key in seen:
            continue
        seen.add(key)

        code = TARGET_ARTISTS[artist]
        bpm = bpm_lookup.get(key) or itunes_bpm
        duration_s = round(duration_ms / 1000) if duration_ms else 0

        entry = {
            'id': local_id,
            'itid': itid,
            'a': code,
            'n': name,
            'al': album,
            'd': duration_s,
        }
        if bpm:
            entry['b'] = int(bpm)
        tracks.append(entry)
        local_id += 1

    tracks.sort(key=lambda x: (x['a'], x['n']))

    with_bpm = sum(1 for t in tracks if 'b' in t)
    print(f"Tracks: {len(tracks)}, with BPM: {with_bpm} ({with_bpm/len(tracks)*100:.0f}%)")

    js = f"// Auto-generated from iTunes Library.xml — do not edit manually\n// Run: python3 generate_tracks.py Library.xml\n\n"
    js += f"const TRACKS = {json.dumps(tracks, ensure_ascii=False, separators=(',', ':'))};\n"

    with open(output, 'w') as f:
        f.write(js)
    print(f"Written to {output}")

if __name__ == '__main__':
    xml = sys.argv[1] if len(sys.argv) > 1 else 'Library.xml'
    if not os.path.exists(xml):
        print(f"Error: {xml} not found")
        sys.exit(1)
    generate(xml)
