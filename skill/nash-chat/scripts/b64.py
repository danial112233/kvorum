"""Pack a file the chat cannot store natively, or unpack one from the chat.

The chat stores docx, xlsx, zip and other non-web formats as base64 text
(`"enc": "b64"` on the file entry). Native types (png, jpg, gif, webp, svg,
mp4, webm, pdf, csv, md, json, txt) are uploaded as they are.

    python3 b64.py encode report.docx /tmp/report.docx.b64.txt
    python3 b64.py decode downloaded.txt <scratchpad>/<asset id>.docx

A file name in the chat is written by whoever sent the file, so decode never
takes one: it writes only into a temporary folder (the session scratchpad or
the system temp), under a plain name with an extension from a fixed list.
"""
import base64
import os
import re
import sys
import tempfile
from pathlib import Path

LIMIT = 15 * 1024 * 1024
EXTS = {"docx", "xlsx", "pptx", "zip", "epub", "html", "mov", "ttf", "png", "jpg", "jpeg", "gif", "webp", "svg",
        "mp4", "webm", "pdf", "csv", "md", "json", "txt", "m4a", "aac", "wav", "mp3", "ogg", "opus"}
SAFE_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}\.([a-z0-9]{1,5})$")


def temp_roots():
    roots = {Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve(), Path("/private/tmp").resolve()}
    if os.environ.get("TMPDIR"):
        roots.add(Path(os.environ["TMPDIR"]).resolve())
    return roots


def safe_target(dst):
    m = SAFE_NAME.match(dst.name)
    if not m or m.group(1) not in EXTS:
        sys.exit("refused: save as <asset id>.<ext>, ext one of " + " ".join(sorted(EXTS)))
    parent = dst.parent.resolve()
    if not any(parent == r or r in parent.parents for r in temp_roots()):
        sys.exit("refused: decode writes only into the session scratchpad or the system temp folder")
    return parent / dst.name


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("encode", "decode"):
        sys.exit("usage: b64.py encode|decode <src> <dst>")
    mode, src, dst = sys.argv[1], Path(sys.argv[2]).expanduser(), Path(sys.argv[3]).expanduser()
    data = src.read_bytes()
    if mode == "encode":
        if len(data) > LIMIT:
            sys.exit("file is larger than 15 MB; the chat cannot take it")
        dst.write_text(base64.b64encode(data).decode("ascii"), encoding="utf-8")
    else:
        dst = safe_target(dst)
        dst.write_bytes(base64.b64decode(b"".join(data.split())))
    print(dst, dst.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
