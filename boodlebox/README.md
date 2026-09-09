# Colorado Weed Guide companion

Bot profile: https://box.boodle.ai/a/@ColoradoWeedGuide

Tutorial starting page: https://denson.github.io/colorado-weed-field-guide/

Later field-note step: https://denson.github.io/colorado-weed-field-guide/companion/

Version 2 opens by explaining the site and offering an optional short tour, a practical lesson, or the visitor's own question. The first line links to the field guide so it can open in the paired pane. Both examples are then introduced before links to individual plant pages. The tour teaches search, photographs and separate evidence sections. The lesson uses fictional garden decisions: interrupt Russian thistle's seed production, then reduce a pet's access to showy milkweed while considering its native habitat value. It discusses each answer before moving on. No actual specimen or prior plant knowledge is required; the practice-note handoff is optional. `greeting.md` and `description.md` are separately published fields; `instructions.md` controls the conversation. The bot remains on unlimited ChatGPT 5-mini, with the same alias and extension mapping.

The September 8, 2026 lesson facts were checked against [CSU Extension's Russian thistle management guidance](https://extension.colostate.edu/resource/identification-and-management-of-kochia-and-russian-thistle/) and [ASPCA's milkweed entry](https://www.aspca.org/pet-care/aspca-poison-control/toxic-and-non-toxic-plants/milkweed), alongside our two plant profiles. Pet-access precautions are explicitly identified as reasoning from the ingestion hazard. Russian thistle's ecological behavior is distinct from legal noxious-weed status; showy milkweed is the native pet-risk example. Learners receive links to our plant pages, where the original sources are available. The reviewed teaching facts are in the bot instructions; the older full knowledge snapshot was not replaced. Website code and the extension do not need changes for this bot revision.

The site builds static per-plant reference packets from the same Markdown as the human articles. A visitor selects zero, one or two profiles and prepares a short note with observations, profile warnings and source links. Full article/evidence text remains available in the packets, public Markdown mirrors and the bot’s uploaded snapshot. BoodleBox turns large pastes into knowledge attachments, so the automatic draft handoff intentionally stays short. No observation backend, API key, local storage, automatic submission or third-party page script is used. Selecting a profile does not identify a specimen.

`instructions.md` is the bot configuration source. `colorado-weed-guide-reference.md` is the uploaded dated knowledge snapshot. After updating profiles: run the normal revision/build/validation workflow, then `python boodlebox/build_reference.py` and replace the bot attachment if desired. Prepared field notes carry the newly deployed profile warning and links to the current text; the installed extension does not need an update for plant content changes. Do not describe the older attachment as a live copy of the site.

Fieldwork Companion Pane v0.5.0 adds this public HTTPS project to the earlier local demos. In Chrome split view it supports deliberate note placement into an empty matching chat draft, and clicked bot links returning to the paired guide page. The visitor still presses Send. Chrome must load the new extension version before those buttons are available. Without it, the copy icon and ordinary profile links work.

The avatar is decorative, generated using the built-in image-generation tool. It is not a botanical evidence photograph. Final prompt:

> A finished square bot avatar for a botanical field guide to garden weeds and native wildflowers. NOT CANNABIS: absolutely no marijuana leaves, no cannabis emblems, no palmate serrated leaves. Subject: a brass hand lens magnifying one simple smooth oval sage-green leaf with a single midrib, beside a little purple thistle flower and cream botanical field notebook. Premium dimensional enamel illustration, engraved brass trim and deep midnight navy background, subtle mountains behind. Elegant and rich, matches a suite of navy and brass fieldwork icons. No text or letters. Central compact composition with margins for circular crop, readable as a small icon. Decorative badge, not a species identification photograph. Render one final square image.

Final asset: `assets/colorado-weed-guide-avatar-v1.png`.
