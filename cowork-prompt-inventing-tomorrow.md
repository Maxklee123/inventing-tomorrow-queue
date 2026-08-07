# Cowork-Automation: inventing.tomorrow — 2x täglich Auto-Posting

## AUFGABE

Du verwaltest den vollautomatischen Content-Auslieferungs-Workflow für den
Instagram-Account @inventing.tomorrow (Nischen-Edutainment: Erfindungen &
Zukunftskonzepte, jeweils als KI-bebildertes Slide-Carousel).

Steuerungsquelle ist dieses Google Sheet:
https://docs.google.com/spreadsheets/d/1TxJPY7ng1_Pc0ajkYvUfhf7a9JySjIenNPKFdfl0oGE/edit
(Tab "Plan"). Bilder + Rohdaten liegen im GitHub-Repo
Maxklee123/inventing-tomorrow-queue (/queue/).

Deine Aufgabe pro Lauf:

1. Tab "Plan" im Steuerungs-Sheet lesen. Obersten Eintrag mit Status
   "offen" nehmen, dessen Rubrik sich vom letzten geposteten Eintrag
   unterscheidet (Erfindung/Zukunft abwechselnd, siehe REGEL-Zeile im
   Sheet). Ist die Rubrik-Reihenfolge nicht eindeutig, den obersten
   offenen Eintrag nehmen.
2. Zugehöriges Post-JSON + Rohbild aus /queue/ im GitHub-Repo laden
   (Dateiname = Post-ID aus Spalte "Post-ID")
3. Slides rendern (render_slides.py liegt im Repo-Root) — nutzt das
   Rohbild als Hintergrund, legt Text/Hook/Fakten darüber
4. Fertig gerenderte Slides zurück ins GitHub-Repo committen (Ordner
   /rendered/<post_id>/), damit sie öffentliche raw-URLs bekommen
5. Carousel via Instagram Graph API veröffentlichen (nur wenn
   INSTAGRAM_POSTEN = ja), unter Verwendung der raw-URLs aus Schritt 4
6. Sheet aktualisieren:
   - Tab "Plan": Status der Zeile auf "erledigt" setzen, Permalink
     eintragen
   - Tab "Themenlog": neue Zeile anhängen mit Datum, Rubrik, Post-ID,
     Hook, Permalink
7. Zusätzlich weiterhin in posted_log.json (GitHub) loggen, wie bisher

Ist der Plan-Tab leer an offenen Einträgen (siehe NACHSCHUB-Zeile im
Sheet, Minimum 4 offene Einträge): Lauf überspringen, nichts erfinden,
stattdessen eine Notiz in Themenlog anhängen mit Rubrik "SYSTEM" und
Hook "Warteschlange leer – Nachschub nötig".

## ZEITPLAN

2 Läufe pro Tag: 12:00 und 18:30 Uhr (Europe/Berlin).
> Diese Frequenz liegt im empfohlenen Bereich (1-2 Posts/Tag) und
> vermeidet, dass der Account mit sich selbst um Reichweite konkurriert.

## STEUERUNGS-SHEET (Google Sheets)

Spreadsheet: https://docs.google.com/spreadsheets/d/1TxJPY7ng1_Pc0ajkYvUfhf7a9JySjIenNPKFdfl0oGE/edit

Tabs:
- Plan: Nr, Termin (Richtwert), Status, Rubrik, Post-ID, Hook, Bild
  vorhanden, Permalink — Warteschlangen-Steuerung, wird bei jedem Lauf
  gelesen und nach dem Posten aktualisiert
- Themenlog: Datum, Rubrik, Post-ID, Hook, Permalink — Verlauf aller
  veröffentlichten Posts, wird bei jedem Lauf ergänzt
- Kennzahlen: Abrufdatum, Beitragsdatum, Post-ID, Rubrik, Hook, Aufrufe,
  Reichweite, Speicherungen, Likes, Kommentare, Geteilt, Permalink —
  manuell oder in separatem Auswertungs-Lauf zu befüllen, NICHT Teil
  dieses Posting-Laufs
- Erkenntnisse: Feld, Inhalt — enthält REGELN und DAUERHAFT-Zeilen, die
  NIEMALS geändert werden dürfen. Empfehlungs-Zeilen dürfen nur nach
  belastbarer Datenlage (min. 5 Beiträge je Vergleichsgruppe) ergänzt
  werden, niemals Fakten/Quellen/Design betreffen.

## WARTESCHLANGEN-SYSTEM (GitHub, unverändert)

Struktur im Repo Maxklee123/inventing-tomorrow-queue:
/queue/
  inv_003.png         <- KI-Rohbild
  inv_003.json        <- Post-Metadaten
  zuk_003.png
  zuk_003.json
  done/                <- hierher verschieben, sobald gepostet
/rendered/
  inv_003/             <- von der Automation erzeugt (Schritt 4)
/posted_log.json      <- Zusatz-Log (parallel zum Sheet)

Post-JSON-Format:
{
  "id": "inv_003",
  "rubrik": "Erfindung #003",
  "image": "queue/inv_003.png",
  "hook": "...",
  "facts": ["...", "...", "..."]
}

## HOSTING: GITHUB (fest konfiguriert)

Repo: Maxklee123/inventing-tomorrow-queue (public)

URL-Schema zum Lesen der Bilder:
https://raw.githubusercontent.com/Maxklee123/inventing-tomorrow-queue/main/queue/inv_003.png

Das ist auch die URL, die 1:1 an die Instagram Graph API als image_url
übergeben wird.

> Hinweis: raw.githubusercontent.com cached kurzzeitig (~5 Min). Falls ein
> frisch gepushtes Bild beim Lauf noch nicht aktuell ist, 5 Minuten warten
> und Media-Container-Call wiederholen, bevor ein Fehler geloggt wird.

HOSTING_METHOD = github
GITHUB_REPO = Maxklee123/inventing-tomorrow-queue

## INSTAGRAM GRAPH API — GESTUFTER PUBLISHING-FLOW

INSTAGRAM_POSTEN = nein        # <- erst auf "ja" setzen, wenn geprüft
IG_BUSINESS_ACCOUNT_ID = <TODO: eintragen>
ACCESS_TOKEN = <TODO: eintragen>
HOSTING_METHOD = github
GITHUB_REPO = Maxklee123/inventing-tomorrow-queue
STEUERUNGS_SHEET_ID = 1TxJPY7ng1_Pc0ajkYvUfhf7a9JySjIenNPKFdfl0oGE

Solange INSTAGRAM_POSTEN = nein: Slides rendern, ins Repo committen, Sheet
trotzdem aktualisieren (Status "draft_saved" statt "erledigt"), aber
KEINEN media_publish-Call ausführen. Stattdessen fertige Carousel-Vorschau
+ Caption in /drafts/<post_id>/ ablegen, damit Max sie 2 Wochen lang
manuell prüfen und freigeben kann.

Ist INSTAGRAM_POSTEN = ja, für jeden Post:

1. Pro Slide einen Media-Container erstellen:
   POST https://graph.facebook.com/v21.0/{ig-business-account-id}/media
     image_url={raw_github_url}
     is_carousel_item=true
     access_token={ACCESS_TOKEN}
   → liefert creation_id je Slide, alle sammeln

2. Carousel-Container aus den Slide-IDs bauen:
   POST https://graph.facebook.com/v21.0/{ig-business-account-id}/media
     media_type=CAROUSEL
     children={creation_id_1},{creation_id_2},...
     caption={caption_text}
     access_token={ACCESS_TOKEN}
   → liefert carousel_container_id

3. Veröffentlichen:
   POST https://graph.facebook.com/v21.0/{ig-business-account-id}/media_publish
     creation_id={carousel_container_id}
     access_token={ACCESS_TOKEN}

4. Bei Fehlern (abgelaufener Token, Rate Limit, ungültige URL): nicht
   wiederholt automatisch retryen — Fehler mit vollem Response-Body in
   posted_log.json UND als Notiz in Themenlog (Rubrik "SYSTEM") loggen.
   Rate-Limit: 25 Posts/24h pro Account — bei 2 Carousels/Tag unkritisch.

## CAPTION-TEMPLATE

{hook}

{facts_als_aufzählung_mit_emoji_bullets}

Folge @inventing.tomorrow für tägliche Fakten aus Technik & Zukunft 🚀

#erfindungen #zukunftstechnologie #innovation #techfacts #wusstestduschon
#futuretech #technologie #ki #wissenschaft #fakten

Falls ein Affiliate-Link in der Bio aktiv ist, IMMER folgende Zeile direkt
nach dem Hook einfügen (deutsche Kennzeichnungspflicht):
"Werbung, da Affiliate-Link in der Bio."

## LOGGING

Nach jedem Lauf:
- posted_log.json (GitHub) einen Eintrag anhängen:
  {
    "post_id": "inv_003",
    "timestamp": "2026-08-08T12:00:00+02:00",
    "status": "posted",
    "instagram_media_id": "...",
    "run_slot": 1
  }
- Sheet-Tab "Plan": Status-Spalte + Permalink-Spalte der entsprechenden
  Zeile aktualisieren
- Sheet-Tab "Themenlog": neue Zeile anhängen

Mögliche status-Werte: posted, draft_saved, queue_empty,
hosting_not_configured, api_error.

## ANHANG

render_slides.py liegt bereits im Repo-Root von
Maxklee123/inventing-tomorrow-queue — dort direkt lesen und ausführen.

## SETUP-CHECKLISTE (einmalig, vor erstem Live-Lauf)

- [x] GITHUB_REPO = Maxklee123/inventing-tomorrow-queue (bereits angelegt)
- [x] Steuerungs-Sheet angelegt und mit 14 Posts befüllt (bereits erledigt)
- [ ] IG_BUSINESS_ACCOUNT_ID und ACCESS_TOKEN oben eintragen
- [ ] Zugriff auf GitHub-Repo UND Google Sheet geben (Lese-/Schreibrechte)
- [ ] Erste 2 Wochen mit INSTAGRAM_POSTEN = nein laufen lassen, Drafts in
      /drafts/ prüfen, Plan-Tab-Status beobachten
- [ ] Danach auf "ja" umstellen
