# Familyboard Planner für Home Assistant

Backend-Integration für einen Wochenkalender, der beliebige
Home-Assistant-Kalender (Google Calendar, CalDAV, lokale Kalender, ...)
farblich unterscheidbar zusammenführt.

Dieses Repository enthält **nur die Python-Integration**. Die passende
Lovelace-Karte (Frontend) lebt in einem eigenen Repository:
👉 **[familyboard-planner-card](https://github.com/GoDigitalizeMe/familyboard-planner-card)**

(Beide waren ursprünglich ein Repo, wurden aber getrennt, weil manche
HACS-Versionen ein Repository nicht gleichzeitig als „Integration“ und
„Dashboard/Plugin“ registrieren lassen.)

## Architektur

Lovelace-Karten laufen im Browser als JavaScript – das ist bei Home Assistant
nicht änderbar. "Nativ mit Python" bedeutet hier deshalb: **die gesamte
Logik steckt in dieser Python Custom Integration**, die Karte im anderen
Repo ist nur ein dünner, reiner Rendering-Layer.

**`custom_components/familyboard_planner/`** (Python) – eine Config-Flow-basierte
Integration. Pro "Planer" wählst du mehrere `calendar.*`-Entities aus und
vergibst Name + Farbe. Ein `DataUpdateCoordinator` fragt alle 15 Minuten
über den Bordmittel-Service `calendar.get_events` die Termine aller
gewählten Kalender ab, reichert sie mit Kalendername/-farbe an und stellt
sie über eine WebSocket-API (`familyboard_planner/get_events`) bereit. Zusätzlich
entsteht ein schlankes Sensor-Entity (`sensor.<planer>_termine`) mit der
Terminanzahl als Zustand – dieses Entity wählst du später in der Karte aus.

## Installation

### Über HACS (empfohlen)

HACS → Integrationen → benutzerdefiniertes Repository hinzufügen:
`https://github.com/GoDigitalizeMe/familyboard-planner-ha`, Kategorie
**Integration**. Danach Home Assistant **neu starten** (Integrationen
werden nur beim Start geladen, anders als Frontend-Ressourcen).

### Manuell

1. Ordner `custom_components/familyboard_planner` nach
   `config/custom_components/familyboard_planner` kopieren.
2. Home Assistant neu starten.

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen** →
   „Familyboard Planner“ suchen.
2. Einen Namen für den Planer vergeben (z. B. „Familie“), die
   gewünschten Kalender auswählen sowie **Tage in die Vergangenheit**
   und **Tage in die Zukunft** festlegen (Standard: 7 bzw. 60 Tage –
   die 7 Tage reichen, um die aktuelle Woche abzudecken).
3. Im zweiten Schritt jedem Kalender einen Anzeigenamen, eine Farbe und
   optional eine **Person** (`person.*`-Entity) zuweisen (Vorschlagsfarben
   werden automatisch vorbelegt). Ist eine Person hinterlegt, verwendet die
   Karte automatisch deren Profilbild statt eines Farbpunkts.
4. Fertig – es entsteht `sensor.<name>_termine`.

Farben/Kalender lassen sich später über **Konfigurieren** auf der
Integrationskarte jederzeit ändern. Du kannst mehrere Planer anlegen (z. B.
„Familie“ und „Arbeit“) – jeder bekommt sein eigenes Sensor-Entity und kann
in einer eigenen Karte angezeigt werden.

Installiere anschließend **[familyboard-planner-card](https://github.com/GoDigitalizeMe/familyboard-planner-card)**
und wähle dort im Karten-Editor das eben entstandene Sensor-Entity aus.

## Hinweise

- Termine werden alle 15 Minuten neu geladen (Coordinator) für den bei
  der Einrichtung festgelegten Zeitraum (Standard: -7/+60 Tage ab
  heute, über **Konfigurieren** jederzeit änderbar); die Karte fragt
  zusätzlich alle 5 Minuten aktiv nach – ideal für einen dauerhaft
  laufenden Wand-/Tablet-Dashboard-Einsatz.
- Für Ganztagestermine, die mehrere Tage umfassen, wird der Termin auf
  jedem betroffenen Tag angezeigt.
- Der Service `calendar.get_events` mit `return_response` setzt eine
  halbwegs aktuelle Home-Assistant-Version voraus (siehe `hacs.json`).
- Die Integration bringt eigene Icons mit (`custom_components/familyboard_planner/brand/`),
  sichtbar in Geräte & Dienste ab Home Assistant 2026.3. HACS selbst
  zeigt diese aktuell noch nicht an (bekannte Einschränkung,
  [hacs/integration#5223](https://github.com/hacs/integration/issues/5223)).

## Roadmap-Idee

Für To-Dos und Einkaufslisten (inkl. Bring!-Integration) gibt es ein
eigenes Schwesterprojekt:
👉 **[familyboard-tasks-ha](https://github.com/GoDigitalizeMe/familyboard-tasks-ha)**
