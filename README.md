# Nash Chat

**English** · [Русский](README.ru.md)

A shared chat for people who use Claude under one account. "Наш чат" means "our chat" in Russian.

> The chat's interface is in Russian.

![Nash Chat: messages, a voice note with its transcript, and a reply from Claude](docs/screenshot.png)

## Why

When several people sign in to Claude with the same login, they share one conversation history but have no way to message each other. Nash Chat is an artifact page inside Claude. Pin it to the sidebar and everyone on the account gets a shared messenger. Messages are signed with a nickname each person picks on their own device.

## Features

- Telegram-style messaging: replies, reactions, pinned message, search, editing your own messages, color themes.
- Photos, videos and files.
- Voice notes: a waveform player with a text transcript under it (see Limitations about the microphone).
- `@claude`: a shared assistant answers right in the chat, using the shared memory and people's cards.
- `@nickname`: if that person is offline, their agent answers from the card the person filled in.
- Work handoff: a "done / next" card you can pass to Claude in a conversation next to the chat.
- Shared memory that Claude and the agents take into account.
- A Claude Code skill: "write to our chat", "what's new in the chat", "ask Anya", "send a voice note", "what's in the voice notes".

## How it works

- `page/nash-chat.html` is the page. Messages live in the artifact's database (the `db` capability), files and recordings in its storage (`assets`), `room` shows who is online, and Claude's replies go through `sample`.
- `skill/nash-chat/` is a skill for Claude Code: the same chat from the terminal or the Claude app. The data format is in `reference.md`.
- Each device writes only to its own documents (one per day), so messages sent at the same time never overwrite each other.

## Set it up

You need Claude Code with artifact publishing (the Claude app or `claude` in a terminal).

1. Get the repository:

   ```bash
   git clone https://github.com/danial112233/claude-nash-chat.git
   ```

2. Ask Claude Code to publish the page:

   > Publish claude-nash-chat/page/nash-chat.html as an artifact with the capabilities assets, db, downloads, room, sample and user, and pin it to the sidebar.

   Claude replies with a link like `https://claude.ai/artifact/…`.

3. Install the skill with your chat's link:

   ```bash
   python3 claude-nash-chat/install.py https://claude.ai/artifact/<your chat id>
   ```

   The skill goes to `~/.claude/skills/nash-chat`. Install it the same way on the other computers that use the account.

4. Open the chat, pick a nickname and an avatar, and fill in your card for the agent.

For voice notes from Claude Code these help but are optional:

- `ffmpeg`: the skill converts any recording to webm and draws the waveform;
- an `stt <file>` command that prints the speech in a recording as text (for example, your own wrapper around faster-whisper). With it the skill transcribes voice notes, and everyone sees the text.

## Limitations

- Microphone. Claude doesn't give artifact pages microphone access. So on a phone the microphone button offers "Record a voice note": an iPhone films a short clip with the camera, the page pulls out the sound and sends only that, and the video goes nowhere. Android opens its voice recorder. You can also pick an existing recording. On a computer the button opens an audio file picker. If the platform opens the microphone later, the button will record directly.
- The page itself can't transcribe speech. Transcripts come from Claude Code on a computer that has `stt`.
- A colleague's agent answers only while the chat is open on at least one device.
- The nickname is stored on the device and the account is shared, so anyone can sign as anyone. The chat is meant for a team that trusts each other.

## License

MIT, see [LICENSE](LICENSE).
