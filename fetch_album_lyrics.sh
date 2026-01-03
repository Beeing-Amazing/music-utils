#!/usr/bin/env bash
# shamelessly copied from https://github.com/ericmckevitt/rmpc-config/blob/main/utils/fetch_album_lyrics.sh
set -euo pipefail

# Usage: fetch_album_lyrics_simple.sh "/path/to/Artist/Album"

LRCLIB_API="https://lrclib.net/api/get"

if [ $# -ne 1 ]; then
    echo "Usage: $0 \"/path/to/Artist/Album\""
    exit 1
fi

ALBUM_DIR="$1"
if [ ! -d "$ALBUM_DIR" ]; then
    echo "Error: '$ALBUM_DIR' is not a directory."
    exit 1
fi

ARTIST="$(basename "$(dirname "$ALBUM_DIR")")"
ALBUM="$(basename "$ALBUM_DIR" | sed -E "s/${ARTIST} - //")"
echo $ALBUM

# Try to fetch synced lyrics (only the [mm:ss.xx] lines) for a given title
# Arguments:
#   $1 = artist
#   $2 = album
#   $3 = title_to_try
# Returns stdout = JSON .syncedLyrics (or "null"/empty)
get_lyrics_for() {
    local artist="$1"
    local album="$2"
    local title_try="$3"

    curl -sG \
        --data-urlencode "artist_name=${artist}" \
        --data-urlencode "track_name=${title_try}" \
        --data-urlencode "album_name=${album}" \
        "$LRCLIB_API" \
        | jq -r '.syncedLyrics'
}

# Attempt a single fetch:
#   1) Try with TITLE_RAW (may include “(feat ...)”)
#   2) Try removing "ARTIST - ALBUM - TRACK_NUM " from filename
#   3) If that yields "" or "null", strip “(…)" and retry
#   4) If still no lyrics, give up
#   5) If we do get lyrics, write them verbatim to the .lrc file
#
# Arguments:
#   $1 = ARTIST
#   $2 = ALBUM
#   $3 = TITLE_RAW
#   $4 = OUTPUT_LRC_FILE (full path, e.g. /.../Song.lrc)
fetch_for_plain() {
    local artist="$1"
    local album="$2"
    local title_try="$3"
    local out_lrc="$4"

    # 1. First-pass lookup
    local lyrics
    lyrics="$(get_lyrics_for "$artist" "$album" "$title_try")"

    # 2. If empty or "null", try stripping "ARTIST - ALBUM - NUM " from title
    if [ -z "$lyrics" ] || [ "$lyrics" == "null" ]; then
        local wout_header
        wout_header="$(echo "$title_try" | sed -E "s/${artist} - ${album} - [0-9]* //")"
        if [ "$wout_header" != "$title_try" ]; then
            title_try="$wout_header"
            lyrics="$(get_lyrics_for "$artist" "$album" "$title_try")"
        fi
    fi

    # 3. If empty or "null", try stripping "(...)" from title
    if [ -z "$lyrics" ] || [ "$lyrics" == "null" ]; then
        local stripped
        stripped="$(echo "$title_try" | sed -E 's/ *\([^)]*\)//g')"
        if [ "$stripped" != "$title_try" ]; then
            title_try="$stripped"
            lyrics="$(get_lyrics_for "$artist" "$album" "$title_try")"
        fi
    fi

    # 4. If still empty/null → skip
    if [ -z "$lyrics" ] || [ "$lyrics" == "null" ]; then
        echo "✗ No lyrics for: \"$title_try\""
        return 1
    fi

    # 5. Write only the synced‐lyrics lines (timestamps + text)
    #    We drop any existing [ar:], [al:], [ti:] lines from the API payload,
    #    but typically lrclib returns only timestamped lines anyway.
    echo "$lyrics" | sed -E '/^\[(ar|al|ti):/d' > "$out_lrc"
    echo "✔ Saved lyrics: $(basename "$out_lrc")"
    return 0
}

echo "▶ Fetching lyrics for all .flac in: $ALBUM_DIR"
echo "  Artist: $ARTIST"
echo "  Album:  $ALBUM"
echo

shopt -s nullglob
for flac in "$ALBUM_DIR"/*.flac; do
    TITLE_RAW="$(basename "$flac" .flac)"
    LRC_FILE="${flac%.flac}.lrc"

    if [ -f "$LRC_FILE" ]; then
        echo "– Skipping \"$TITLE_RAW\" (already have .lrc)"
        continue
    fi

    if ! fetch_for_plain "$ARTIST" "$ALBUM" "$TITLE_RAW" "$LRC_FILE"; then
        # a failure just prints the “No lyrics for…” message and moves on
        continue
    fi
done

echo
echo "Done."
