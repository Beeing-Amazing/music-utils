from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis as OGG
from pathlib import Path
import argparse

MUSIC_DIR = Path("~/Music/mpd").expanduser()
TEST_MODE : bool = False


def main(album: Path, tag: str, arg: str):
    # get album path
    # get type of tag, then arg
    # for every song:
        # set tag to arg

    if tag == "albumname": tag = "album"
    
    assert album.is_dir()
    exts = ("*.flac", "*.mp3", "*.ogg")
    p = [f for ext in exts for f in album.glob(ext)]
    files = [x for x in p if x.is_file()]
    files.sort()

    for track in files:
        match track.suffix:
            case ".flac":
                audio = FLAC(track)
            case ".mp3":
                audio = EasyID3(track)
            case ".ogg":
                audio = OGG(track)

        expand_arg = arg.split("; ")
        try:
            old_tag = audio[tag]
        except KeyError:
            old_tag = [""]
        audio[tag] = expand_arg
        if not TEST_MODE:
            audio.save()
        else:
            filename = track.name
            pretty_name = filename.split(" - ")[-1]
            print(f"{pretty_name}: {old_tag} -> {audio[tag]}")



def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("album", type=str)
    parser.add_argument("--test", action="store_true", default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", type=str)
    group.add_argument("--genre", type=str)
    group.add_argument("--artist", type=str)
    group.add_argument("--albumname", type=str)
    group.add_argument("--albumartist", type=str)

    return parser


if __name__ == "__main__":
    parser = init_parser()
    args = parser.parse_args()


    dict_args = vars(args)
    TEST_MODE = dict_args.pop("test", False)
    assert "album" in dict_args.keys()
    album = dict_args.pop("album", None)
    album_path = MUSIC_DIR / album

    assert album_path.exists(), album_path
    assert album_path.is_dir(), album_path

    only_passed_tag = {k: v for k, v in dict_args.items() if v is not None}

    if len(only_passed_tag) == 1:
        tag = list(only_passed_tag)[0]
        main(album=album_path, tag=tag, arg=only_passed_tag[tag])
