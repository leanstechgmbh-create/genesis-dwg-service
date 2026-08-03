/* ==========================================================================
   LEANS KOSMOS — deine Daten
   Nur diese Datei anfassen. Alles andere bleibt, wie es ist.

   typ:  projekt | kunde | rechnung | angebot | wartung | aufgabe
   verbunden: Liste von ids, mit denen der Knoten eine Linie bekommt
   ========================================================================== */

window.KOSMOS_DATEN = {

  firma: "LEANS TECH GMBH",

  knoten: [

    /* ---------- Projekte / Baustellen ---------- */
    { id: "bv-mehringdamm", typ: "projekt", bereich: "business",
      titel: "Mehringdamm 44-46",
      info: "Klima / Lüftung · laufend",
      verbunden: ["kd-sp-construct", "ar-2026-40", "ar-2026-34", "ang-301", "auf-aufmass"] },

    { id: "bv-berlepsch", typ: "projekt", bereich: "business",
      titel: "Berlepschstr. 165",
      info: "Heizung / Sanitär · laufend",
      verbunden: ["kd-hausverwaltung", "ang-312", "wtg-klima-dach", "auf-kaeltemittel"] },

    { id: "bv-lg-klima", typ: "projekt", bereich: "business",
      titel: "LG Klimatechnik",
      info: "Lieferung / Montage",
      verbunden: ["kd-lg", "ang-305", "ar-2026-8"] },

    /* ---------- Kunden ---------- */
    { id: "kd-sp-construct", typ: "kunde", bereich: "business",
      titel: "SP Construct",
      info: "Auftraggeber · § 13b",
      verbunden: ["ar-2026-40", "ar-2026-34", "ang-301"] },

    { id: "kd-hausverwaltung", typ: "kunde", bereich: "business",
      titel: "Hausverwaltung Süd",
      info: "Auftraggeber · Bestand",
      verbunden: ["ang-312", "wtg-klima-dach"] },

    { id: "kd-lg", typ: "kunde", bereich: "business",
      titel: "LG Electronics",
      info: "Fabrikat / Lieferant",
      verbunden: ["ang-305"] },

    /* ---------- Rechnungen ----------
       status: gestellt | bezahlt | mahnung                                   */
    { id: "ar-2026-40", typ: "rechnung", bereich: "business",
      titel: "2026-40 · 2. AR",
      info: "SP Construct · Mehringdamm",
      netto: 18420.00, status: "gestellt", faellig: "2026-08-06",
      verbunden: [] },

    { id: "ar-2026-34", typ: "rechnung", bereich: "business",
      titel: "2026-34 · 1. AR",
      info: "SP Construct · Mehringdamm",
      netto: 12750.00, status: "bezahlt", faellig: "2026-07-14",
      verbunden: [] },

    { id: "ar-2026-8", typ: "rechnung", bereich: "business",
      titel: "2026-8 · Rechnung",
      info: "LG Klimatechnik",
      netto: 4310.00, status: "bezahlt", faellig: "2026-03-02",
      verbunden: [] },

    /* ---------- Angebote ----------
       status: offen | beauftragt | abgelehnt                                 */
    { id: "ang-301", typ: "angebot", bereich: "business",
      titel: "Angebot 301",
      info: "Mehringdamm · Lüftungsgerät",
      netto: 46800.00, status: "beauftragt", gueltig: "2026-06-30",
      verbunden: [] },

    { id: "ang-312", typ: "angebot", bereich: "business",
      titel: "Angebot 312",
      info: "Berlepschstr. · Heizungstausch",
      netto: 21500.00, status: "offen", gueltig: "2026-08-31",
      verbunden: [] },

    { id: "ang-305", typ: "angebot", bereich: "business",
      titel: "Angebot 305",
      info: "LG · Split-Anlagen 4x",
      netto: 9840.00, status: "offen", gueltig: "2026-08-20",
      verbunden: [] },

    /* ---------- Wartung ---------- */
    { id: "wtg-klima-dach", typ: "wartung", bereich: "business",
      titel: "Wartung Klima Dach",
      info: "1x jährlich · 19 % MwSt.",
      netto: 1290.00, termin: "2026-09-15",
      verbunden: ["auf-messprotokoll"] },

    /* ---------- Offene Punkte ---------- */
    { id: "auf-aufmass", typ: "aufgabe", bereich: "business",
      titel: "Aufmaß nachreichen",
      info: "Mehringdamm · für Schlussrechnung",
      verbunden: [] },

    { id: "auf-kaeltemittel", typ: "aufgabe", bereich: "business",
      titel: "Kältemittel bestellen",
      info: "Berlepschstr. · R32",
      verbunden: [] },

    { id: "auf-messprotokoll", typ: "aufgabe", bereich: "business",
      titel: "Messprotokoll ablegen",
      info: "Wartung · Drive",
      verbunden: [] },

    /* ---------- Privat ---------- */
    { id: "pv-steuer", typ: "aufgabe", bereich: "privat",
      titel: "Steuerunterlagen",
      info: "Q2 an Büro",
      verbunden: [] },

    { id: "pv-fahrzeug", typ: "projekt", bereich: "privat",
      titel: "Fahrzeug Wartung",
      info: "Transporter · Inspektion",
      verbunden: ["pv-termin-werkstatt"] },

    { id: "pv-termin-werkstatt", typ: "aufgabe", bereich: "privat",
      titel: "Werkstatt-Termin",
      info: "offen",
      verbunden: [] }

  ]
};
