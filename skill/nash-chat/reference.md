# Наш чат: формат данных

Артефакт: `<ССЫЛКА_НА_ЧАТ>`. Все вызовы `ArtifactData` идут с этим `url`.

Форма вызовов `ArtifactData`:

```
чтение:   { action: "query", url, collection: "msgs", query: { where: [["day", ">=", "2026-10-09"]], limit: 1000 } }
          { action: "query", url, collection: "brain", query: { order_by: { field: "at", direction: "desc" }, limit: 200 } }
          { action: "list",  url, collection: "people" }
запись:   { action: "set", url, collection: "msgs", doc_id: "<msgs_doc_id>", data: { ... } }   — новый документ, без if_version
правка:   { action: "update", url, collection: "people", doc_id: "<people_doc_id>", data: { ... }, if_version: <из get> }
```

Каждая запись — новый документ `msgs` с одним сообщением в `items`. Свой прошлый документ не дописывай.

## `msgs` — сообщения

Документ = сообщения одного писателя за один день UTC. Ты всегда создаёшь новый документ (`set` без `if_version`), чужие не трогаешь.

```json
{ "day": "2026-10-16", "writer": "cc-k3v6q2rt", "items": [ { ...сообщение } ] }
```

| поле | у каких видов | что это |
|---|---|---|
| `id` | все | 12 символов `a-z0-9` |
| `at` | все | миллисекунды эпохи, 13 цифр |
| `kind` | все | `text`, `handoff`, `ask`, `claude`, `agent`, `ack`, `del`, `voice`, `react`, `pin`, `edit` |
| `nick` | все | ник автора; у `agent` — чей это агент |
| `text` | все | текст (markdown); у `handoff` — комментарий, может быть `""` |
| `via` | твои | всегда `"claude-code"` |
| `reply` | любые | `id` сообщения, на которое это ответ |
| `to` | `ask` | ник, кого спрашивают (`""` — всех) |
| `files` | любые | `[{ "id", "name", "type", "size", "enc"? }]`, до 10 |
| `handoff` | `handoff` | `{ "project", "done", "next" }` |
| `voice` | `voice` | `{ "dur": секунды, "peaks": 40 знаков 0-9a-v для полосок, "text": расшифровка }`, все поля можно опустить; сама запись — аудиофайл в `files` |
| `emoji`, `on` | `react` | эмодзи и `true`/`false` (поставил или снял) |
| `ref` | `ack`, `del` | `id` сообщения, которое приняли или скрыли |
| `askedBy` | `claude`, `agent` | кто позвал |
| `agentOf` | `agent` | чей агент ответил |
| `img` | старые | id картинки из первой версии чата, читай как файл-картинку |

Скрытие: `del` прячет сообщение того же ника (у `claude`/`agent` — того, кто позвал). Принятие: самый ранний `ack` на передачу.

Виды со страницы, при пересказе их не перечисляй: `react {ref, emoji, on}` — реакция, действует последняя по `at` у пары ник+эмодзи; `pin {ref, on}` — закреп, действует последний; `edit {ref, text}` — правка своего сообщения (`text` и `ask`), действует последняя от автора: показывай текст из неё.

Чтение: `query` с `where: [["day", ">=", "<week_ago>"]]`, `limit: 1000`, собрать `items` из всех документов, отсортировать по `at`.

## `brain` — общая память

Документ на запись: `brain/<12 символов>` = `{ "text", "by", "at", "src" }`. `src`: `manual`, `handoff`, `claude-code`. Читать: `query` с `order_by: { "field": "at", "direction": "desc" }`, `limit: 200`. Удалять только по прямой просьбе: `delete` с `if_version`.

## `people` — профили и карточки агентов

`people/p-<hex>` = `{ "nick", "face", "card", "updatedAt" }`. id документа и аватарка по умолчанию — из `python3 scripts/ids.py --nick "<ник>"`.

- Карточка (`card`) — то, по чему агент отвечает за человека, пока его нет в сети. До 3000 символов: проекты, где что лежит, кого спрашивать.
- Обновить свою: сначала `get` (версия), потом `update` `{ "card", "updatedAt" }` с `if_version`. Нет документа — `set` `{ "nick", "face": <default_face>, "card", "updatedAt" }`.
- Чужие карточки не меняй.

## `voicetext` — расшифровки голосовых

`voicetext/<id голосового сообщения>` = `{ "text", "by": "claude-code", "at", "engine": "stt" }`. Если в записи нет речи, пиши `"text": ""`: страница ничего не покажет, а следующий запрос не станет расшифровывать её снова. Страница показывает текст под плеером. Пишет только Claude Code, создаёт документ без `if_version`; если запись отклонили, значит расшифровку уже сделали — прочитай её.

## `jobs` — служебная

`jobs/<id вопроса>` ведёт страница: так открытые чаты договариваются, кто отвечает агентом на `ask`, и отмечают `done: true`. Только для чтения: не пиши и не удаляй.

## Файлы

Хранятся в ассетах артефакта, в сообщении лежит только описание.

Отправить:
0. Перед первой загрузкой в этом разговоре прочитай артефакт (`Artifact` read с `url`), иначе загрузку отклонят. Достаточно самого вызова: сохранённый им HTML страницы читать не нужно. Размер исходника — `stat -f%z <файл>`. Временные `.b64.txt` клади в scratchpad сессии, не рядом с оригиналом.
1. Нативные типы (`png jpg gif webp svg mp4 webm pdf csv md json txt`) — `Artifact` publish с `url`, `file_path`, `asset: true`. Ответ даёт `id`. Текстовые файлы — по одному за вызов.
2. Остальное (`docx xlsx pptx zip epub html mov ttf`) — `python3 scripts/b64.py encode <файл> <файл>.b64.txt`, загрузить этот `.txt`, в описании `"enc": "b64"`, `name` и `type` — от исходного файла.
3. Описание: `{ "id", "name", "type": "<mime>", "size": <байты исходника>, "enc": "b64" при упаковке }`.
   MIME: docx `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, xlsx `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, pptx `application/vnd.openxmlformats-officedocument.presentationml.presentation`, zip `application/zip`, epub `application/epub+zip`, html `text/html`, mov `video/quicktime`, ttf `font/ttf`. Имя файла — как есть, кириллица допустима.
4. Предел — 20 МБ (упакованные — 15 МБ исходника). rar, psd и прочее, чего нет в списке выше, страница не даст скачать: проси zip.

Получить: `Artifact` read с `url` и `path: "<id>"` — файл сохранится локально (путь в ответе). Если `"enc": "b64"` — `python3 scripts/b64.py decode <сохранённый> <имя>`.

## Голосовые

Сообщение `kind: "voice"`, `text: ""`, запись — один аудиофайл в `files`, у него `type` вида `audio/...`. Старые страницы покажут его просто файлом.

Отправить:
1. `python3 scripts/voice.py prep <файл записи> <scratchpad сессии>` — печатает `upload`, `name`, `type`, `size`, `enc` (если есть), `dur`, `peaks`. С ffmpeg любой формат превращается в webm.
2. Расшифровка: есть `stt` (`command -v stt`) — `stt <абсолютный путь к upload>`, текст в stdout. Нет `stt` — отправляй без текста.
3. Загрузи `upload`: `Artifact` publish с `url`, `file_path`, `asset: true` (перед первой загрузкой в разговоре — `Artifact` read). Ответ даёт `id`.
4. Запиши новый документ `msgs` (обёртка `{ day, writer, items }` — как в разделе `msgs`) с одним сообщением:

```json
{ "id": "<id>", "at": <at>, "kind": "voice", "nick": "<ник>", "via": "claude-code", "text": "",
  "files": [{ "id": "<id ассета>", "name": "<name>", "type": "<type>", "size": <size> }],
  "voice": { "dur": <dur>, "peaks": "<peaks>", "text": "<расшифровка>" } }
```
`type` бери из `voice.py` (`audio/...`), а не тот, что вернула загрузка (`video/webm`: так хранилище принимает звук). `"enc": "b64"` в описание файла — только если его напечатал `voice.py`. Пустые `peaks` и `text` не пиши.

Голосовое, которое дал пользователь, отправляй сразу вместе с расшифровкой: это его слова, а не твои. Расшифровку покажи ему в ответе.

Узнать, что в голосовых:
1. Голосовые — элементы `items` с `kind: "voice"` за тот же период, что и в «что в чате» (неделя, если не попросили иначе). Скрытые `del` пропускай.
2. Расшифровки: `list` коллекции `voicetext` с `query: { limit: 1000 }` (или `get voicetext/<id>` на каждое). Если есть и `voice.text`, и `voicetext`, бери `voice.text`. Документ с пустым `text` значит «речи нет»: повторно не расшифровывай.
3. Расшифровки нет — скачай запись (`Artifact` read с `url` и `path: "<id файла>"`), при `"enc": "b64"` распакуй `b64.py decode <сохранённый> <scratchpad>/<id сообщения>.<расширение из name>`, затем `stt <абсолютный путь>` (`stt <путь> auto`, если речь не на русском).
4. Запиши `voicetext/<id сообщения>` (это не чужое сообщение, согласовывать не нужно), чтобы текст увидели все. В пересказе помечай: «по расшифровке голосового».
5. Нет `stt` — скажи, что голосовое без расшифровки и его можно послушать на странице.
