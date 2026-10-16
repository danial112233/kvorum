# Nash Chat

**English** · [Русский](README.ru.md)

A shared chat for people who use Claude under one account. "Наш чат" means "our chat" in Russian.

> The chat's interface is in Russian.

![Nash Chat: messages, a voice note with its transcript, and a reply from Claude](docs/screenshot.png)

## Why

When several people sign in to Claude with the same login, they share one conversation history but have no way to message each other. Nash Chat is an artifact page inside Claude. Pin it to the sidebar and everyone on the account gets a shared messenger. Messages are signed with a nickname each person picks on their own device.

## Features

- Telegram-style messaging: replies, reactions, pinned message, search, editing your own messages, color themes. On a phone, message actions open on a long press.
- Discord-style channels and groups: a list on the left, unread and mention counts per channel. A group is visible only to its members.
- Voice channels: "Join" opens the call in Jitsi Meet in a new tab, and the chat shows who is in the channel. The (i) button next to "Voice" explains how it works.
- Photos, videos and files.
- Voice notes: a waveform player with a text transcript under it (see Limitations about the microphone).
- Video circles: round video notes up to a minute. After recording, the circle shows above the input. "Send" shrinks it to a 480 px square MP4, with a ring that shows the progress. If the browser can't shrink video, a clip up to 20 MB goes as it is. In the feed circles loop silently and play with sound on tap.
- Guests from other accounts: they read everything and write text, and their nickname always ends in "(гость)", "guest" (see "Invite people from another account").
- Help inside the chat: the "?" button at the top left and the Help tab in the side panel.
- `@claude`: a shared assistant answers right in the chat, using the shared memory and people's cards.
- `@nickname`: if that person is offline, their agent answers from the card the person filled in.
- Work handoff: a "done / next" card you can pass to Claude in a conversation next to the chat.
- Shared memory that Claude and the agents take into account.
- A Claude Code skill: "write to our chat", "what's new in the chat", "ask Anya", "send a voice note", "what's in the voice notes".

## How it works

- `page/nash-chat.html` is the page. Messages live in the artifact's database (the `db` capability), files and recordings in its storage (`assets`), `room` shows who is online, and Claude's replies go through `sample`.
- `skill/nash-chat/` is a skill for Claude Code: the same chat from the terminal or the Claude app. The data format is in `reference.md`.
- Each device writes only to its own documents (one per day), so messages sent at the same time never overwrite each other.

## Quick start

You need Claude Code with artifact publishing (the Claude app or `claude` in a terminal). Five steps, about five minutes:

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
5. Bring people in. On the same account the chat's link is enough. From another account, see the next section.

For voice notes from Claude Code these help but are optional:

- `ffmpeg`: the skill converts any recording to webm and draws the waveform;
- an `stt <file>` command that prints the speech in a recording as text (for example, your own wrapper around faster-whisper). With it the skill transcribes voice notes, and everyone sees the text.

## Invite people from another account

1. Open the chat, click Share and invite the person by email as a Viewer or Commenter. Keep link sharing off.
2. They open the link from the email, pick a nickname and see a "you are a guest" note. They can read everything and write text, and their messages carry a "guest" label.
3. The platform doesn't let guests write to the chat's database, so their text travels through a member's page. It is delivered as soon as at least one member has the chat open on screen. The easiest way is to keep the pinned chat open in its own Claude app window on a computer that is usually on. Until then the guest sees "queued". Guests write only in #общий and open channels, at most 5 messages a minute. Voice notes, circles and files aren't available to guests.
4. A guest reads everything: channels, groups, the shared memory, people's cards and call links. Keep passwords and private matters out of the chat. A guest's nickname always ends in "(гость)", and one that looks like a member's or like Claude becomes plain "Гость".
5. The Editor role gives a guest full write access, but also lets them change the page itself, so it's better not to give it.
6. For people who should write everything without these limits and without the right to change the page, use a Team or Enterprise plan and add them to the organization with the Contributor role.

## Limitations

| What | Why | What to do |
|---|---|---|
| No recording from the microphone | Claude doesn't give artifact pages microphone access | On a phone, "Record a voice note": an iPhone films a short clip, and only its sound goes to the chat; Android opens its voice recorder. On a computer, pick an audio file. If the platform opens the microphone later, the button will record directly |
| A voice channel is a Jitsi tab | The page can't carry sound | The call happens in Jitsi Meet (meet.jit.si). Jitsi may ask whoever starts the call to sign in with Google or GitHub. The room link is permanent and long, but anyone who has it can join |
| A circle is shrunk only after "Send" | In the Claude app on a phone, a video can start only from a tap | Tap "Send" and wait for the ring. If the browser can't shrink video, a clip up to 20 MB goes as it is; for a longer one, record a shorter clip |
| iPhone voice notes are stored as base64 m4a | The storage doesn't accept an audio-only MP4 | Nothing to do: the player fetches recordings ahead of time, so an iPhone plays right on tap |
| The page can't transcribe speech | Artifacts have no speech recognition | Transcripts come from Claude Code on a computer that has `stt` |
| A guest's message goes out only while a member has the chat open | Guests can't write to the database; a member's page carries their text | Keep the pinned chat open in its own window on a computer that is usually on |
| A guest reads everything, groups included | Access to the artifact is access to its whole database | Keep passwords and private matters out of the chat. A group only hides itself from the channel list |
| A colleague's agent answers only while the chat is open somewhere | An open page writes the agent's answer | If there's no answer yet, it comes once someone opens the chat |
| Anyone can sign as anyone | The account is shared and the nickname lives on the device | The chat is meant for a team that trusts each other. A known device only suggests a nickname; it never picks one on its own |

## License

MIT, see [LICENSE](LICENSE).
