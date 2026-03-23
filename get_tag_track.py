from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis as OGG
from pathlib import Path
import argparse

MUSIC_DIR = Path("~/Music/mpd").expanduser()


def main(track: Path, tag: str):
    # get type of tag
    # show tags for track

    assert track.is_file() and (suffix := track.suffix) in [".flac", ".mp3", ".ogg"]
    all_tags = []
    
    match suffix:
        case ".flac":
            audio = FLAC(track)
        case ".mp3":
            audio = MP3(track)
        case ".ogg":
            audio = OGG(track)

    try:
        tag = audio[tag]
        all_tags += tag
    except KeyError:
        print("") # blank str for pipe

    formatted_tags = "; ".join(set(all_tags))
    print(formatted_tags)


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("track", type=str)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", action="store_true", default=False)
    group.add_argument("--genre", action="store_true", default=False)
    group.add_argument("--title", action="store_true", default=False)
    group.add_argument("--albumartist", action="store_true", default=False)
    group.add_argument("--tracknumber", action="store_true", default=False)

    return parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()


    dict_args = vars(args)
    assert "track" in dict_args.keys()
    track = dict_args.pop("track", None)
    track_path = MUSIC_DIR / track

    assert track_path.exists(), track_path
    assert track_path.is_file()

    only_passed_tag = {k: v for k, v in dict_args.items() if v}

    if len(only_passed_tag) == 1:
        tag = list(only_passed_tag)[0]
        main(track=track_path, tag=tag)
