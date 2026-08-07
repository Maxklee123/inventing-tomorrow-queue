# inventing-tomorrow-queue

Content-Warteschlange fuer die @inventing.tomorrow Instagram-Automation.

## Struktur

- `/queue/` - hier legst du KI-Rohbild (.png) + Post-Metadaten (.json) ab, z.B. inv_003.png + inv_003.json
- `/queue/done/` - hierher verschiebt die Automation Posts, die bereits gepostet wurden
- `/rendered/` - von der Automation erzeugte, fertig gerenderte Slides (Text-Overlay), werden per raw-URL an die Instagram Graph API uebergeben
- `posted_log.json` - Verlauf aller Automation-Laeufe

## Post-JSON-Format

```json
{
  "id": "inv_003",
  "rubrik": "Erfindung #003",
  "image": "queue/inv_003.png",
  "hook": "...",
  "facts": ["...", "...", "..."]
}
```

Details zum Gesamt-Workflow: siehe cowork-prompt-inventing-tomorrow.md im Projekt.
