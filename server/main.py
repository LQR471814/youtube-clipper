import argparse
import subprocess
from datetime import timedelta
from os import mkdir, listdir, chdir

from flask import Flask, request
from flask_cors import CORS
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--directory', default="clips", type=str,
    help="the directory to place the output clips",
)
parser.add_argument(
    '-f', '--ffmpeg', default="ffmpeg", type=str,
    help="the path to the ffmpeg binary",
)
args = parser.parse_args()

app = Flask(__name__)
CORS(app)

ydl = YoutubeDL()

tag_index: set[str] = set()
clips_path = ""

def remove_ext(value: str) -> str:
    return ".".join(value.split(".")[:-1])


# @app.route("/audio")
# def audio():
#     return send_file("output.mp3", "audio/mp3")


# @app.route("/video")
# def video():
#     return send_file("output.mp4", "video/mp4")


@app.route("/query")
def query():
    term = request.args.get("q")
    if term is None:
        return "missing query term!", 400
    return YoutubeSearch(term, max_results=10).to_dict(), 200


@app.route("/watch")
def watch():
    video_id = request.args.get("id")
    if video_id is None:
        return "missing video id!", 400

    info = ydl.extract_info(
        f"https://youtube.com/watch?v={video_id}", download=False)
    sanitized = ydl.sanitize_info(info)

    return {
        "title": sanitized.get("fulltitle"),
        "duration": sanitized.get("duration_string"),
        "channel": sanitized.get("channel"),
        "chapters": sanitized.get("chapters"),
        "video": sanitized.get("requested_formats")[0].get("url"),
        "audio": sanitized.get("requested_formats")[1].get("url"),
        "captions": get_captions(sanitized),
    }, 200


@app.route("/tags")
def tags():
    # return list(tag_index), 200
    return [], 200


def execute(command: list[str]):
    child = subprocess.Popen(command, stdout=subprocess.PIPE)
    return child.wait()


@app.route("/splice", methods=["POST"])
def splice():
    global tag_index

    # expects request of shape
    # {
    #   tags: string[]
    #   video: string
    #   audio: string
    #   clips: {
    #     start: number
    #     end: number
    #   }[]
    # }
    results = request.get_json()

    tag_set = set(results["tags"])
    tag_index = tag_index.union(tag_set)

    output_prefix = '-'.join(sorted(tag_set))

    index_offset = 0
    for file in listdir("."):
        if file.startswith(output_prefix):
            found_index = int(remove_ext(file).split("-")[-1])
            if found_index > index_offset:
                index_offset = found_index

    for i, clip in enumerate(results["clips"]):
        start = timedelta(seconds=int(float(clip["start"])))
        end = timedelta(seconds=int(float(clip["end"])))

        clip_range = ["-ss", str(start), "-to", str(end)]

        returncode = execute([
            args.ffmpeg, "-hide_banner", "-loglevel", "error",
            *clip_range, "-i", results["video"],
            *clip_range, "-i", results["audio"],
            f"{output_prefix}-{index_offset+i+1}.mp4",
        ])
        if returncode != 0:
            return "failed to split clip!", 500

    return "successfully spliced clips", 200


def get_captions(video_info: dict) -> str | None:
    automatic_captions = video_info.get("automatic_captions")
    if automatic_captions is None:
        return None

    english = automatic_captions.get("en-en")
    if english is None:
        return None

    caption_source = None
    for source in english:
        if source.get("ext") == "vtt":
            caption_source = source
            break

    return caption_source.get("url")


if __name__ == "__main__":
    try:
        mkdir(args.directory)
    except:
        pass
    chdir(args.directory)

    app.run("localhost", 8000)
