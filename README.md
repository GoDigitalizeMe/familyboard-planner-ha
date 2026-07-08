# Daely Planner für Home Assistant

Backend-Integration für einen Wochenkalender im Stil des
[Dæly Familienkalenders](https://daely-shop.com/products/daely-calendar-familienkalender-familienplaner-15-6),
der beliebige Home-Assistant-Kalender (Google Calendar, CalDAV, lokale
Kalender, ...) farblich unterscheidbar zusammenführt.

Dieses Repository enthält **nur die Python-Integration**. Die passende
Lovelace-Karte (Frontend) lebt in einem eigenen Repository:
👉 **[daely-planner-card](https://github.com/GoDigitalizeMe/daely-planner-card)**

(Beide waren ursprünglich ein Repo, wurden aber getrennt, weil manche
HACS-Versionen ein Repository nicht gleichzeitig als „Integration“ und
„Dashboard/Plugin“ registrieren lassen.)

## Architektur

Lovelace-Karten laufen im Browser als JavaScript – das ist bei Home Assistant
nicht änderbar. "Nativ mit Python" bedeutet hier deshalb: **die gesamte
Logik steckt in dieser Python Custom Integration**, die Karte im anderen
Repo ist nur ein dünner, reiner Rendering-Layer.

**`custom_components/daely_planner/`** (Python) – eine Config-Flow-basierte
Integration. Pro "Planer" wählst du mehrere `calendar.*`-Entities aus und
vergibst Name + Farbe. Ein `DataUpdateCoordinator` fragt alle 15 Minuten
über den Bordmittel-Service `calendar.get_events` die Termine aller
gewählten Kalender ab, reichert sie mit Kalendername/-farbe an und stellt
sie über eine WebSocket-API (`daely_planner/get_events`) bereit. Zusätzlich
entsteht ein schlankes Sensor-Entity (`sensor.<planer>_termine`) mit der
Terminanzahl als Zustand – dieses Entity wählst du später in der Karte aus.

## Installation

### Über HACS (empfohlen)

HACS → Integrationen → benutzerdefiniertes Repository hinzufügen:
`https://github.com/GoDigitalizeMe/daely-planner-ha`, Kategorie
**Integration**. Danach Home Assistant **neu starten** (Integrationen
werden nur beim Start geladen, anders als Frontend-Ressourcen).

### Manuell

1. Ordner `custom_components/daely_planner` nach
   `config/custom_components/daely_planner` kopieren.
2. Home Assistant neu starten.

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen** →
   „Daely Planner“ suchen.
2. Einen Namen für den Planer vergeben (z. B. „Familie“) und die
   gewünschten Kalender auswählen.
3. Im zweiten Schritt jedem Kalender einen Anzeigenamen, eine Farbe und
   optional eine **Person** (`person.*`-Entity) zuweisen (Vorschlagsfarben
   werden automatisch vorbelegt). Ist eine Person hinterlegt, verwendet die
   Karte automatisch deren Profilbild statt eines Farbpunkts.
4. Fertig – es entsteht `sensor.<name>_termine`.

Farben/Kalender lassen sich später über **Konfigurieren** auf der
Integrationskarte jederzeit ändern. Du kannst mehrere Planer anlegen (z. B.
„Familie“ und „Arbeit“) – jeder bekommt sein eigenes Sensor-Entity und kann
in einer eigenen Karte angezeigt werden.

Installiere anschließend **[daely-planner-card](https://github.com/GoDigitalizeMe/daely-planner-card)**
und wähle dort im Karten-Editor das eben entstandene Sensor-Entity aus.

## Hinweise

- Termine werden alle 15 Minuten neu geladen (Coordinator); die Karte
  fragt zusätzlich alle 5 Minuten aktiv nach – ideal für einen dauerhaft
  laufenden Wand-/Tablet-Dashboard-Einsatz.
- Für Ganztagestermine, die mehrere Tage umfassen, wird der Termin auf
  jedem betroffenen Tag angezeigt.
- Der Service `calendar.get_events` mit `return_response` setzt eine
  halbwegs aktuelle Home-Assistant-Version voraus (siehe `hacs.json`).

## Roadmap-Idee

Für eine spätere Version ist eine ToDo-Verwaltung angedacht (insbesondere
für Kinder), z. B. als eigene `todo.*`-Entities pro Person – bisher nicht
umgesetzt.
