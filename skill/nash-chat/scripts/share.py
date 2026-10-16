"""What the chat may take from this computer, and nothing else.

The person who owns this computer writes the policy himself, in
~/.config/nash-chat/share.json:

    {"allow": ["~/Shared/nash-chat", "~/Projects/site/exports"], "per_hour": 10}

    python3 share.py policy                 # allowed folders, or how to set them up
    python3 share.py ls                     # files directly inside the allowed folders
    python3 share.py check <path>           # may this file go? JSON: ok, path, size, sha256, type, pack, reason
    python3 share.py done <path> <sha256> <request id>   # count a sent file toward the hourly cap

Only files inside an allowed folder go, after symlinks are resolved. Keys,
passwords, tokens, hidden files and folders, system and browser folders
never go, even inside an allowed folder. The chat cannot change any of this:
the policy is a local file.
"""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

HOME = Path(os.path.expanduser("~")).resolve()
CONF = HOME / ".config" / "nash-chat"
POLICY = CONF / "share.json"
LOG = CONF / "fetch-log.jsonl"
LIMIT = 20 * 1024 * 1024        # the chat's storage takes up to 20 MB
PACKED_LIMIT = 15 * 1024 * 1024  # a file sent as base64 grows by a third
NATIVE = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4", ".webm", ".pdf", ".csv", ".md", ".json", ".txt"}
PACKED = {".docx", ".xlsx", ".pptx", ".zip", ".epub", ".html", ".mov", ".ttf"}
TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
         ".svg": "image/svg+xml", ".mp4": "video/mp4", ".webm": "video/webm", ".pdf": "application/pdf",
         ".csv": "text/csv", ".md": "text/markdown", ".json": "application/json", ".txt": "text/plain",
         ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
         ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
         ".zip": "application/zip", ".epub": "application/epub+zip", ".html": "text/html",
         ".mov": "video/quicktime", ".ttf": "font/ttf"}
# never, whatever the policy says
DENY_DIRS = [HOME / p for p in (".ssh", ".gnupg", ".aws", ".azure", ".kube", ".docker", ".config", ".claude",
                                ".local", "Library")] + [Path("/etc"), Path("/private"), Path("/System"), Path("/var")]
DENY_NAME = re.compile(
    r"(^|[^a-z0-9])(key|keys|secret|secrets|token|tokens|passwd|password|passwords|credential|credentials|"
    r"private|wallet|seed|mnemonic|cookie|cookies|keychain|vault|пароль|пароли|ключ|ключи|токен)([^a-z0-9]|$)"
    r"|^id_(rsa|dsa|ecdsa|ed25519)|\.(pem|p12|pfx|key|kdbx|keychain|ovpn|asc|gpg)$|^\.env|\.env$",
    re.IGNORECASE)


def say(obj):
    print(json.dumps(obj, ensure_ascii=False))


def load_policy():
    try:
        raw = json.loads(POLICY.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "no policy: create " + str(POLICY) + ' with {"allow": ["~/Shared/nash-chat"]}'
    except (OSError, ValueError) as e:
        return None, "policy unreadable: " + str(e)
    roots, bad = [], []
    for item in raw.get("allow", []) if isinstance(raw, dict) else []:
        if not isinstance(item, str):
            continue
        r = Path(os.path.expanduser(item)).resolve()
        why = root_problem(r)
        (bad if why else roots).append((r, why))
    per_hour = raw.get("per_hour", 10) if isinstance(raw, dict) else 10
    per_hour = per_hour if isinstance(per_hour, int) and 0 < per_hour <= 100 else 10
    return {"roots": [r for r, _ in roots], "bad": [(str(r), w) for r, w in bad], "per_hour": per_hour}, ""


def root_problem(r):
    """An allowed folder must be a real, narrow folder: not the home folder, not above it, not a hidden or system one."""
    if not r.is_dir():
        return "not a folder"
    if r == HOME or r in HOME.parents or r == Path("/"):
        return "too wide: name a folder inside your home folder"
    if any(r == d or d in r.parents for d in DENY_DIRS):
        return "system, hidden or private folder"
    if any(part.startswith(".") for part in r.relative_to(HOME).parts) if HOME in r.parents else False:
        return "hidden folder"
    return ""


def file_problem(p, roots):
    """Why this resolved path may not go, or "" when it may."""
    if not p.exists():
        return "no such file"
    if not p.is_file():
        return "not a file"
    root = next((r for r in roots if r in p.parents), None)
    if root is None:
        return "outside the allowed folders"
    if any(p == d or d in p.parents for d in DENY_DIRS):
        return "system, hidden or private folder"
    rel = p.relative_to(root).parts
    if any(part.startswith(".") for part in rel):
        return "hidden file or folder"
    if any(DENY_NAME.search(part) for part in rel):
        return "looks like a key, password or token"
    ext = p.suffix.lower()
    if ext not in NATIVE and ext not in PACKED:
        return "the chat cannot take this type: pack it into zip"
    size = p.stat().st_size
    if size > (PACKED_LIMIT if ext in PACKED else LIMIT):
        return "too big for the chat"
    return ""


def sent_last_hour():
    if not LOG.exists():
        return 0
    now, n = time.time(), 0
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            if now - float(json.loads(line).get("at", 0)) < 3600:
                n += 1
        except ValueError:
            continue
    return n


def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("policy", "ls", "check", "done"):
        sys.exit(__doc__)
    cmd = sys.argv[1]
    pol, err = load_policy()
    if cmd == "policy":
        say({"ok": bool(pol and pol["roots"]), "allow": [str(r) for r in pol["roots"]] if pol else [],
             "refused": pol["bad"] if pol else [], "per_hour": pol["per_hour"] if pol else 0, "reason": err})
        return
    if not pol or not pol["roots"]:
        say({"ok": False, "reason": err or "no allowed folders"})
        sys.exit(1)
    if cmd == "ls":
        out = []
        for r in pol["roots"]:
            for f in sorted(r.iterdir()):
                p = f.resolve()
                if not file_problem(p, pol["roots"]):
                    out.append({"path": str(p), "size": p.stat().st_size})
        say({"ok": True, "files": out[:200]})
        return
    if cmd == "check":
        if len(sys.argv) != 3:
            sys.exit("usage: share.py check <path>")
        p = Path(os.path.expanduser(sys.argv[2])).resolve()
        why = file_problem(p, pol["roots"])
        if not why and sent_last_hour() >= pol["per_hour"]:
            why = "hourly limit reached (" + str(pol["per_hour"]) + "): wait"
        if why:
            say({"ok": False, "path": str(p), "reason": why})
            sys.exit(1)
        ext = p.suffix.lower()
        say({"ok": True, "path": str(p), "name": p.name, "size": p.stat().st_size, "sha256": sha256(p),
             "type": TYPES[ext], "pack": ext in PACKED})
        return
    if len(sys.argv) != 5:
        sys.exit("usage: share.py done <path> <sha256> <request id>")
    p = Path(os.path.expanduser(sys.argv[2])).resolve()
    CONF.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": time.time(), "path": str(p), "sha256": sys.argv[3], "req": sys.argv[4][:64]}, ensure_ascii=False) + "\n")
    say({"ok": True})


if __name__ == "__main__":
    main()
