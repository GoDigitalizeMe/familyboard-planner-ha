# Daely Planner für Home Assistant

Ein Wochenkalender im Stil des [Dæly Familienkalenders](https://daely-shop.com/products/daely-calendar-familienkalender-familienplaner-15-6),
der beliebige Home-Assistant-Kalender (Google Calendar, CalDAV, lokale
Kalender, ...) farblich unterscheidbar in einer Lovelace-Karte darstellt.

## Architektur

Lovelace-Karten laufen im Browser als JavaScript – das ist bei Home Assistant
nicht änderbar. "Nativ mit Python" bedeutet hier deshalb: **die gesamte
Logik steckt in einer Python Custom Integration**, die Karte selbst ist ein
dünner, reiner Rendering-Layer:

- **`custom_components/daely_planner/`** (Python) – eine Config-Flow-basierte
  Integration. Pro "Planer" wählst du mehrere `calendar.*`-Entities aus und
  vergibst Name + Farbe. Ein `DataUpdateCoordinator` fragt alle 15 Minuten
  über den Bordmittel-Service `calendar.get_events` die Termine aller
  gewählten Kalender ab, reichert sie mit Kalendername/-farbe an und stellt
  sie über eine WebSocket-API (`daely_planner/get_events`) bereit. Zusätzlich
  entsteht ein schlankes Sensor-Entity (`sensor.<planer>_termine`) mit der
  Terminanzahl als Zustand.
- **`dist/daely-planner-card.js`** (JavaScript, ca. 500 Zeilen, keine
  externen Abhängigkeiten) – liest nur das Sensor-Entity plus die
  WebSocket-API aus und zeichnet das Daely-artige Wochenraster.

## Installation

### Über HACS (empfohlen)

Da dieses Repository sowohl eine Integration als auch eine Karte enthält,
fügst du es zweimal als benutzerdefiniertes Repository hinzu:

1. HACS → Integrationen → benutzerdefiniertes Repository hinzufügen,
   Kategorie **Integration** → dieses Repo installieren.
2. HACS → Frontend → benutzerdefiniertes Repository hinzufügen,
   Kategorie **Plugin** → dieses Repo installieren.
3. Home Assistant neu starten.

### Manuell

1. Ordner `custom_components/daely_planner` nach
   `config/custom_components/daely_planner` kopieren.
2. Datei `dist/daely-planner-card.js` nach
   `config/www/daely-planner-card.js` kopieren.
3. In **Einstellungen → Dashboards → Ressourcen** eine Ressource hinzufügen:
   URL `/local/daely-planner-card.js`, Typ „JavaScript-Modul“.
4. Home Assistant neu starten.

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen** →
   „Daely Planner“ suchen.
2. Einen Namen für den Planer vergeben (z. B. „Familie“) und die
   gewünschten Kalender auswählen.
3. Im zweiten Schritt jedem Kalender einen Anzeigenamen und eine Farbe
   zuweisen (Vorschlagsfarben werden automatisch vorbelegt).
4. Fertig – es entsteht `sensor.<name>_termine`.

Farben/Kalender lassen sich später über **Konfigurieren** auf der
Integrationskarte jederzeit ändern. Du kannst mehrere Planer anlegen (z. B.
„Familie“ und „Arbeit“) – jeder bekommt sein eigenes Sensor-Entity und kann
in einer eigenen Karte angezeigt werden.

## Karte einrichten

Dashboard bearbeiten → Karte hinzufügen → "Manuell" (YAML):

```yaml
type: custom:daely-planner-card
entity: sensor.familie_termine
title: Familienplaner
language: de           # "de" oder "en"
first_day_of_week: monday   # "monday" oder "sunday"
show_weekends: true    # false -> nur Mo-Fr (5 Tage)
show_legend: true
```

| Option | Standard | Beschreibung |
| --- | --- | --- |
| `entity` | *(erforderlich)* | Sensor-Entity des Daely-Planers |
| `title` | Entity-Titel | Überschrift der Karte |
| `language` | `de` | Sprache für Wochentage/Monate (`de`/`en`) |
| `first_day_of_week` | `monday` | Wochenstart |
| `days` | `7` (bzw. `5` bei `show_weekends: false`) | Anzahl angezeigter Tage |
| `show_weekends` | `true` | `false` blendet Sa/So aus |
| `show_legend` | `true` | Farblegende der Kalender ein-/ausblenden |

Termin antippen öffnet ein Detail-Popup mit Uhrzeit, Ort und Beschreibung.

## Hinweise

- Termine werden alle 15 Minuten neu geladen (Coordinator) und die Karte
  fragt zusätzlich alle 5 Minuten aktiv nach – ideal für einen dauerhaft
  laufenden Wand-/Tablet-Dashboard-Einsatz.
- Für Ganztagestermine, die mehrere Tage umfassen, wird der Termin auf
  jedem betroffenen Tag angezeigt.
- Der Service `calendar.get_events` mit `return_response` setzt eine
  halbwegs aktuelle Home-Assistant-Version voraus (siehe `hacs.json`).
