"""Pack a file the chat cannot store natively, or unpack one from the chat.

The chat stores docx, xlsx, zip and other non-web formats as base64 text
(`"enc": "b64"` on the file entry). Native types (png, jpg, gif, webp, svg,
mp4, webm, pdf, csv, md, json, txt) are uploaded as they are.

    python3 b64.py encode report.docx /tmp/report.docx.b64.txt
    python3 b64.py decode downloaded.txt ~/Downloads/report.docx
"""
import base64
import sys
from pathlib import Path

LIMIT = 15 * 1024 * 1024


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
        dst.write_bytes(base64.b64decode(b"".join(data.split())))
    print(dst, dst.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
