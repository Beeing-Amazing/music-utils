from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis as OGG
from pathlib import Path
import argparse

MUSIC_DIR = Path("~/Music/mpd").expanduser()
TEST_MODE : bool = False


def main(track: Path, tag: str, arg: str):
    # get type of tag, then arg
    # set tag to arg
    
    assert track.is_file() and (suffix := track.suffix) in [".flac", ".mp3", ".ogg"]
    match suffix:
        case ".flac":
            audio = FLAC(track)
        case ".mp3":
            audio = EasyID3(track)
        case ".ogg":
            audio = OGG(track)

    expand_arg = arg.split("; ")
    try:
        old_tag = audio[tag]
        if old_tag != expand_arg:
            audio[tag] = expand_arg
    except KeyError:
        old_tag = [""]
        audio[tag] = expand_arg

        pretty_name = track.name.split(" - ")[-1]
        print(f"{pretty_name}: {old_tag} -> {audio[tag]}")
    finally:
        if not TEST_MODE:
            audio.save()



def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("track", type=str)
    parser.add_argument("--test", action="store_true", default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", type=str)
    group.add_argument("--genre", type=str)
    group.add_argument("--title", type=str)
    group.add_argument("--albumartist", type=str)
    group.add_argument("--tracknumber", type=str)

    return parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()


    dict_args = vars(args)
    TEST_MODE = dict_args.pop("test", False)
    assert "track" in dict_args.keys()
    track = dict_args.pop("track", None)
    track_path = MUSIC_DIR / track

    assert track_path.exists(), track_path
    assert track_path.is_file(), track_path

    only_passed_tag = {k: v for k, v in dict_args.items() if v is not None}

    if len(only_passed_tag) == 1:
        tag = list(only_passed_tag)[0]
        main(track=track_path, tag=tag, arg=only_passed_tag[tag])
