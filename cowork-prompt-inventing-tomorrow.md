# Cowork-Automation: inventing.tomorrow — 2x täglich Auto-Posting

Kopiere diesen gesamten Prompt in eine neue Cowork-Aufgabe und richte ihn
als wiederkehrenden Task ein (2 Läufe/Tag, siehe Zeitplan unten).

---

## AUFGABE

Du verwaltest den vollautomatischen Content-Auslieferungs-Workflow für den
Instagram-Account **@inventing.tomorrow** (Nischen-Edutainment: Erfindungen
& Zukunftskonzepte, jeweils als KI-bebildertes Slide-Carousel).

Bilder werden von Max manuell vorbereitet und liegen in einer Warteschlange
in diesem Repo (`/queue/`). Deine Aufgabe pro Lauf (2x täglich):

1. Nächsten unveröffentlichten Post aus der Warteschlange holen (liest
   `/queue/` in diesem Repo, siehe HOSTING-Abschnitt)
2. Slides rendern (Skript im Anhang) — nutzt das Rohbild aus `/queue/`
   als Hintergrund, legt Text/Hook/Fakten darüber
3. Fertig gerenderte Slides zurück ins Repo committen (Ordner
   `/rendered/<post_id>/`), damit sie öffentliche raw-URLs bekommen
4. Carousel via Instagram Graph API veröffentlichen (nur wenn
   `INSTAGRAM_POSTEN = ja`), unter Verwendung der raw-URLs aus Schritt 3
5. Ergebnis loggen, Post in `/queue/` als "gepostet" markieren (z.B. durch
   Verschieben nach `/queue/done/` oder Eintrag in `posted_log.json`)

## ZEITPLAN

2 Läufe pro Tag, zu den Tageszeiten mit üblicherweise hoher Instagram-
Aktivität (Mittagspause und Feierabend):

| Lauf | Uhrzeit (Europe/Berlin) |
|---|---|
| 1 | 12:00 |
| 2 | 18:30 |

> Diese Frequenz liegt im empfohlenen Bereich (1-2 Posts/Tag) und
> vermeidet, dass der Account mit sich selbst um Reichweite konkurriert.
> Bei Bedarf später auf Basis der Performance-Daten anpassen.

## WARTESCHLANGEN-SYSTEM

Struktur im Repo:
```
/queue/
  inv_003.png         <- von Max hochgeladenes KI-Rohbild
  inv_003.json        <- Post-Metadaten (siehe Format unten)
  zuk_003.png
  zuk_003.json
  done/                <- hierher verschieben, sobald gepostet
/rendered/
  inv_003/             <- von der Automation erzeugt (Schritt 3)
    01_hook.png
    02_fact.png
    ...
/posted_log.json      <- Verlauf aller veröffentlichten Posts
```

Post-JSON-Format:
```json
{
  "id": "inv_003",
  "rubrik": "Erfindung #003",
  "image": "queue/inv_003.png",
  "hook": "...",
  "facts": ["...", "...", "..."]
}
```

**Auswahl-Logik pro Lauf:**
1. Alle `.json`-Dateien in `/queue/` lesen, die noch nicht in
   `posted_log.json` als gepostet vermerkt sind
2. Rubriken abwechselnd wählen (Erfindung → Zukunft → Erfindung → ...),
   damit der Feed durchmischt bleibt
3. Ist die Warteschlange leer: **nicht raten oder improvisieren** —
   stattdessen Lauf überspringen und in `posted_log.json` vermerken
   `"status": "queue_empty"`, damit Max merkt, dass er nachlegen muss

## HOSTING: GITHUB (fest konfiguriert)

Repo: **Maxklee123/inventing-tomorrow-queue** (public)

**URL-Schema zum Lesen der Bilder:**
```
https://raw.githubusercontent.com/Maxklee123/inventing-tomorrow-queue/main/queue/inv_003.png
```
Das ist auch die URL, die 1:1 an die Instagram Graph API als `image_url`
übergeben wird — direkt aus GitHub, kein zusätzlicher Hosting-Schritt.

> Hinweis: raw.githubusercontent.com cached kurzzeitig (~5 Min). Falls ein
> frisch gepushtes Bild beim Lauf noch nicht aktuell ist, 5 Minuten warten
> und Media-Container-Call wiederholen, bevor ein Fehler geloggt wird.

**Bei jedem Lauf:**
1. Repo-Inhalt von `/queue/` abrufen (GitHub API: `GET /repos/Maxklee123/inventing-tomorrow-queue/contents/queue`)
2. `.json`-Dateien lesen, die noch nicht in `posted_log.json` als gepostet
   markiert sind
3. Zugehöriges Rohbild per raw-URL referenzieren, als Hintergrund fürs
   Rendering nutzen (siehe Renderer im Anhang)
4. Gerenderte Slides (fertige PNGs mit Text-Overlay) per GitHub Contents
   API (`PUT /repos/Maxklee123/inventing-tomorrow-queue/contents/rendered/<post_id>/<datei>`)
   ins selbe Repo committen
5. Deren raw-URLs als `image_url` an die Instagram Graph API übergeben
   (siehe Publishing-Flow unten)

```
HOSTING_METHOD = github
GITHUB_REPO = Maxklee123/inventing-tomorrow-queue
```

## INSTAGRAM GRAPH API — GESTUFTER PUBLISHING-FLOW

```
INSTAGRAM_POSTEN = nein        # <- erst auf "ja" setzen, wenn unten geprüft
IG_BUSINESS_ACCOUNT_ID = <TODO: von Max einzutragen>
ACCESS_TOKEN = <TODO: langlebiger Token von Max einzutragen>
HOSTING_METHOD = github
GITHUB_REPO = Maxklee123/inventing-tomorrow-queue
```

Solange `INSTAGRAM_POSTEN = nein`: Slides rendern, ins Repo committen,
aber **keinen** `media_publish`-Call ausführen. Stattdessen fertige
Carousel-Vorschau + Caption in `/drafts/<post_id>/` ablegen, damit Max sie
2 Wochen lang manuell prüfen und freigeben kann.

Ist `INSTAGRAM_POSTEN = ja`, für jeden Post:

1. **Pro Slide** einen Media-Container erstellen:
   ```
   POST https://graph.facebook.com/v21.0/{ig-business-account-id}/media
     image_url={raw_github_url}
     is_carousel_item=true
     access_token={ACCESS_TOKEN}
   ```
   → liefert `creation_id` je Slide, alle sammeln

2. **Carousel-Container** aus den Slide-IDs bauen:
   ```
   POST https://graph.facebook.com/v21.0/{ig-business-account-id}/media
     media_type=CAROUSEL
     children={creation_id_1},{creation_id_2},...
     caption={caption_text}
     access_token={ACCESS_TOKEN}
   ```
   → liefert `carousel_container_id`

3. **Veröffentlichen:**
   ```
   POST https://graph.facebook.com/v21.0/{ig-business-account-id}/media_publish
     creation_id={carousel_container_id}
     access_token={ACCESS_TOKEN}
   ```

4. Bei Fehlern (abgelaufener Token, Rate Limit, ungültige URL): **nicht
   wiederholt automatisch retryen** — Fehler mit vollem Response-Body in
   `posted_log.json` loggen und Max beim nächsten Kontakt aktiv darauf
   hinweisen. Rate-Limit der Content Publishing API: 25 Posts/24h pro
   Account — bei 2 Carousels/Tag unkritisch.

## CAPTION-TEMPLATE

```
{hook}

{facts_als_aufzählung_mit_emoji_bullets}

Folge @inventing.tomorrow für tägliche Fakten aus Technik & Zukunft 🚀

#erfindungen #zukunftstechnologie #innovation #techfacts #wusstestduschon
#futuretech #technologie #ki #wissenschaft #fakten
```

Falls ein Affiliate-Link in der Bio aktiv ist, IMMER folgende Zeile direkt
nach dem Hook einfügen (deutsche Kennzeichnungspflicht):
```
Werbung, da Affiliate-Link in der Bio.
```

## LOGGING

Nach jedem Lauf einen Eintrag in `posted_log.json` anhängen:
```json
{
  "post_id": "inv_003",
  "timestamp": "2026-08-08T12:00:00+02:00",
  "status": "posted",
  "instagram_media_id": "...",
  "run_slot": 1
}
```
Mögliche `status`-Werte: `posted`, `draft_saved`, `queue_empty`,
`hosting_not_configured`, `api_error`.

---

## ANHANG: render_slides.py

Siehe `render_slides.py` in diesem Repo (identische Version wie im
Projekt-Output geteilt).

---

## SETUP-CHECKLISTE FÜR MAX (einmalig, vor erstem Live-Lauf)

- [x] `GITHUB_REPO` = Maxklee123/inventing-tomorrow-queue (bereits angelegt)
- [ ] `IG_BUSINESS_ACCOUNT_ID` und `ACCESS_TOKEN` oben eintragen
- [ ] Cowork Zugriff auf dieses Repo geben (GitHub-Verbindung für die
      Contents-API, zum Lesen von `/queue/` und Schreiben nach `/rendered/`)
- [ ] Mindestens 4-6 Posts in `/queue/` vorbereiten (Puffer für 2-3 Tage)
- [ ] Diesen Prompt als wiederkehrenden Cowork-Task mit den 2 Zeiten oben
      einrichten
- [ ] Erste 2 Wochen mit `INSTAGRAM_POSTEN = nein` laufen lassen, Drafts in
      `/drafts/` prüfen
- [ ] Danach auf `ja` umstellen
