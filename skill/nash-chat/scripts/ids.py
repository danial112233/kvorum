"""Values a Claude Code session needs to write into «Кворум» (formerly «Наш чат»).

Prints, from one clock reading: at (ms), day (UTC), week_ago (UTC),
a fresh writer suffix and message id, and, with --nick, the people
document id and default avatar seed for that nick (same hash the page uses).

    python3 ids.py
    python3 ids.py --nick "Аня"
"""
import argparse
import datetime as dt
import secrets
import string
import time

ABC = string.ascii_lowercase + string.digits


def rnd(n):
    return "".join(secrets.choice(ABC) for _ in range(n))


def fnv1a(text):
    h = 0x811C9DC5
    for ch in text:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nick")
    args = ap.parse_args()

    t = time.time()
    u = dt.datetime.fromtimestamp(t, dt.timezone.utc)
    writer = rnd(8)
    print("at", int(t * 1000))
    print("day", u.strftime("%Y-%m-%d"))
    print("week_ago", (u - dt.timedelta(days=7)).strftime("%Y-%m-%d"))
    print("writer", "cc-" + writer)
    print("msgs_doc_id", u.strftime("%Y%m%d") + "-cc-" + writer)
    print("id", rnd(12))
    print("brain_doc_id", rnd(12))
    if args.nick:
        key = args.nick.strip().lower()
        seed = fnv1a(key)
        print("people_doc_id", "p-%08x" % seed)
        print("default_face", seed)


if __name__ == "__main__":
    main()
