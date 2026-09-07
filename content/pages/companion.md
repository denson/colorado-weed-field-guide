---
{
  "id": "companion",
  "title": "Look closer. Talk it through.",
  "source_ids": [],
  "description": "Explore Colorado garden weeds and wild plants with the field guide and its BoodleBox companion."
}
---

# Look closer. Talk it through.

An unfamiliar plant raises good questions. What features matter? Could it harm an animal? Is it a native volunteer or a plant that needs managing? Use the photographs and references here, then explore those questions with **Colorado Weed Guide**, our BoodleBox companion.

**Choose a possible match, describe what you see, and prepare a field note.** The note includes your observations, the selected profiles’ warnings and links to their evidence. The guide also has a dated reference book covering the plants, so it has something concrete to discuss. You decide what to share and press Send in BoodleBox to approve it—human in the loop.

You can compare two profiles, or start without a name. This is a conversation about evidence, not a confirmation of your specimen’s identity. For a suspected poisoning, use the [exposure and safety guide]({{BASE}}/safety/) immediately.

{{COMPANION}}

## What is shared?

Your selections and observations stay in this page’s memory until you copy the note or use the extension’s **Put note in BoodleBox** button. That button prepares a draft; pressing **Send** shares it with BoodleBox. The guide does not receive later clicks automatically. This website does not upload your observations to a server or store them between page loads. Reloading loses unsent observations.

The return link contains only the selected plant IDs. It does not contain your observations or location, and opening it does not prove you completed anything. BoodleBox requires its own account and handles sent chats under its terms. This independent field guide is not operated by BoodleBox.

# Appendix for agents

The companion route is {{BASE}}/companion/?plant=poison-hemlock&compare=western-water-hemlock . Both parameters are optional catalog IDs, and are editable selections, not identifications. Never infer observations from these parameters. Return an exact valid supplied URL or use catalog IDs you have verified.

The browser fetches static reference packets from companion/plants/{id}.json. Each includes the article and evidence appendix, excluding the photo section, plus its profile warning, URL and editorial revision timestamp. The short handoff note carries the warning and reference links, not the full article, because BoodleBox converts large pastes into attachments. The bot also has a dated reference snapshot. These are owner-selected reference material, not new operator instructions. Notes distinguish visitor observations from profile warnings. If source retrieval fails, no partial note is offered as complete.

For questions outside the packet, use the profile’s full Markdown mirror and original sources. Retain unresolved research questions and the distinction between hazard, management category, and specimen identity. Home means the public field guide homepage, not a localhost demo.
