"""Install the nash-chat skill for Claude Code and point it at your chat.

    python3 install.py https://claude.ai/artifact/<your chat id>

Copies skill/nash-chat to ~/.claude/skills/nash-chat and writes your chat link
into SKILL.md and reference.md. Run it again to update the skill.
"""
import re
import shutil
import sys
from pathlib import Path

PLACEHOLDER = "<ССЫЛКА_НА_ЧАТ>"


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"https://claude\.ai/(code/)?artifact/[A-Za-z0-9-]+", sys.argv[1]):
        sys.exit("usage: python3 install.py https://claude.ai/artifact/<your chat id>")
    src = Path(__file__).resolve().parent / "skill" / "nash-chat"
    dst = Path.home() / ".claude" / "skills" / "nash-chat"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for name in ("SKILL.md", "reference.md"):
        p = dst / name
        p.write_text(p.read_text(encoding="utf-8").replace(PLACEHOLDER, sys.argv[1]), encoding="utf-8")
    print("installed to", dst)


if __name__ == "__main__":
    main()
