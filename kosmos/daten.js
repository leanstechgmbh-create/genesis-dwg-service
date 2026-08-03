/* ==========================================================================
   LEANS KOSMOS — BEISPIELDATEN

   Alles hier ist erfunden. Diese Datei liegt im oeffentlichen Repo und
   zeigt nur, wie der Kosmos aussieht.

   Deine echten Vorgaenge gehoeren NICHT hier hinein, sondern in
   kosmos/zuordnung.json — daraus baut tools/kosmos-daten.py die Datei
   daten.privat.js, die diese hier beim Laden ueberschreibt. Beide stehen
   in .gitignore und bleiben auf deinem Rechner.

   typ:  projekt | kunde | rechnung | angebot | wartung | aufgabe
   verbunden: Liste von ids, mit denen der Knoten eine Linie bekommt
   ========================================================================== */

window.KOSMOS_DATEN = {

  firma: "LEANS TECH GMBH",
  stand: "Beispieldaten",

  knoten: [

    /* ---------- Projekte / Baustellen ---------- */
    { id: "bv-beispiel", typ: "projekt", bereich: "business",
      titel: "Beispielstr. 12",
      info: "Klima / Lüftung · laufend",
      verbunden: ["kd-muster-bau", "ar-2026-2", "ar-2026-1", "ang-999", "auf-aufmass"] },

    { id: "bv-dach", typ: "projekt", bereich: "business",
      titel: "Dachanlage Nord",
      info: "Wartung · Bestand",
      verbunden: ["kd-hausverwaltung", "wtg-dach", "auf-messprotokoll"] },

    { id: "bv-lieferung", typ: "projekt", bereich: "business",
      titel: "Split-Anlagen Lieferung",
      info: "Lieferung / Montage",
      verbunden: ["kd-hausverwaltung", "ang-1001"] },

    /* ---------- Kunden ---------- */
    { id: "kd-muster-bau", typ: "kunde", bereich: "business",
      titel: "Muster Bau GmbH",
      info: "Auftraggeber · § 13b",
      verbunden: [] },

    { id: "kd-hausverwaltung", typ: "kunde", bereich: "business",
      titel: "Hausverwaltung Beispiel",
      info: "Bestandskunde · Wartung",
      verbunden: [] },

    /* ---------- Rechnungen ----------
       status: gestellt | bezahlt | mahnung | unbekannt                       */
    { id: "ar-2026-2", typ: "rechnung", bereich: "business",
      titel: "2026-2 · 2. AR",
      info: "Muster Bau · Beispielstr.",
      netto: 14000.00, status: "gestellt", faellig: "2026-08-29",
      verbunden: ["kd-muster-bau"] },

    { id: "ar-2026-1", typ: "rechnung", bereich: "business",
      titel: "2026-1 · 1. AR",
      info: "Muster Bau · Beispielstr.",
      netto: 23000.00, status: "bezahlt", faellig: "2026-07-09",
      verbunden: ["kd-muster-bau"] },

    { id: "ar-2026-7", typ: "rechnung", bereich: "business",
      titel: "2026-7 · Rechnung",
      info: "aus dem Register · noch keinem Projekt zugeordnet",
      netto: 4310.00, status: "unbekannt",
      verbunden: [] },

    /* ---------- Angebote ----------
       status: offen | beauftragt | abgelehnt                                 */
    { id: "ang-999", typ: "angebot", bereich: "business",
      titel: "Angebot 999",
      info: "Beispielstr. · Lüftungsgerät",
      netto: 46000.00, status: "beauftragt", gueltig: "2026-06-30",
      verbunden: ["kd-muster-bau"] },

    { id: "ang-1001", typ: "angebot", bereich: "business",
      titel: "Angebot 1001",
      info: "Split-Anlagen 4x",
      netto: 9840.00, status: "offen", gueltig: "2026-08-20",
      verbunden: ["kd-hausverwaltung"] },

    /* ---------- Wartung ---------- */
    { id: "wtg-dach", typ: "wartung", bereich: "business",
      titel: "Wartung Dachanlage",
      info: "1x jährlich · 19 % MwSt.",
      netto: 233.00, termin: "2026-09-15",
      verbunden: ["kd-hausverwaltung"] },

    /* ---------- Offene Punkte ---------- */
    { id: "auf-aufmass", typ: "aufgabe", bereich: "business",
      titel: "Aufmaß nachreichen",
      info: "Beispielstr. · für die Schlussrechnung",
      verbunden: [] },

    { id: "auf-messprotokoll", typ: "aufgabe", bereich: "business",
      titel: "Messprotokoll ablegen",
      info: "Wartung · ins Drive",
      verbunden: [] },

    /* ---------- Privat ---------- */
    { id: "pv-fahrzeug", typ: "projekt", bereich: "privat",
      titel: "Fahrzeug",
      info: "Transporter · Inspektion",
      verbunden: ["pv-werkstatt-termin"] },

    { id: "pv-werkstatt-termin", typ: "aufgabe", bereich: "privat",
      titel: "Werkstatt-Termin",
      info: "offen",
      verbunden: [] }

  ]
};
