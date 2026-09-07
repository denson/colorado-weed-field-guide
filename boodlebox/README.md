# Colorado Weed Guide companion

Bot profile: https://box.boodle.ai/a/@ColoradoWeedGuide

Public entry: https://denson.github.io/colorado-weed-field-guide/companion/

The site builds static per-plant reference packets from the same Markdown as the human articles. A visitor selects zero, one or two profiles and prepares a short note with observations, profile warnings and source links. Full article/evidence text remains available in the packets, public Markdown mirrors and the bot’s uploaded snapshot. BoodleBox turns large pastes into knowledge attachments, so the automatic draft handoff intentionally stays short. No observation backend, API key, local storage, automatic submission or third-party page script is used. Selecting a profile does not identify a specimen.

`instructions.md` is the bot configuration source. `colorado-weed-guide-reference.md` is the uploaded dated knowledge snapshot. After updating profiles: run the normal revision/build/validation workflow, then `python boodlebox/build_reference.py` and replace the bot attachment if desired. Prepared field notes carry the newly deployed profile warning and links to the current text; the installed extension does not need an update for plant content changes. Do not describe the older attachment as a live copy of the site.

Fieldwork Companion Pane v0.5.0 adds this public HTTPS project to the earlier local demos. In Chrome split view it supports deliberate note placement into an empty matching chat draft, and clicked bot links returning to the paired guide page. The visitor still presses Send. Chrome must load the new extension version before those buttons are available. Without it, the copy icon and ordinary profile links work.

The avatar is decorative, generated using the built-in image-generation tool. It is not a botanical evidence photograph. Final prompt:

> A finished square bot avatar for a botanical field guide to garden weeds and native wildflowers. NOT CANNABIS: absolutely no marijuana leaves, no cannabis emblems, no palmate serrated leaves. Subject: a brass hand lens magnifying one simple smooth oval sage-green leaf with a single midrib, beside a little purple thistle flower and cream botanical field notebook. Premium dimensional enamel illustration, engraved brass trim and deep midnight navy background, subtle mountains behind. Elegant and rich, matches a suite of navy and brass fieldwork icons. No text or letters. Central compact composition with margins for circular crop, readable as a small icon. Decorative badge, not a species identification photograph. Render one final square image.

Final asset: `assets/colorado-weed-guide-avatar-v1.png`.
