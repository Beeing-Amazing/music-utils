from mutagen.flac import FLAC
from pathlib import Path
import argparse

MUSIC_DIR = Path("~/Music/mpd/")


def main(album: Path, tag: str, show_only_first: bool = False):
    # get album path
    # get type of tag, then arg
    # for every song:
        # set tag to arg
    
    assert album.is_dir()
    p = album.glob("*.flac")
    files = [x for x in p if x.is_file()]
    files.sort()

    for track in files:
        audio = FLAC(track)

        try:
            tag = audio[tag]
        except KeyError:
            print("") # blank str for pipe
        formatted_tags = "; ".join(tag)
        print(formatted_tags)

        if show_only_first:
            break


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("album", type=str)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", action="store_true", default=False)
    group.add_argument("--genre", action="store_true", default=False)
    group.add_argument("--artist", action="store_true", default=False)

    return parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()


    dict_args = vars(args)
    assert "album" in dict_args.keys()
    album = dict_args.pop("album", None)
    album_path = MUSIC_DIR.expanduser() / album

    only_passed_tag = {k: v for k, v in dict_args.items() if v}

    if len(only_passed_tag) == 1:
        tag = list(only_passed_tag)[0]
        main(album=album_path, tag=tag, show_only_first=True)
