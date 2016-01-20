# list-to-table – Compare products in a spreadsheet

This script was written to parse a text, filter out interesting keywords and output it as CSV. It is written for one custom format which http://geizhals.de and http://www.heise.de/preisvergleich use in the feature list of products.

So, this line of input:

    LG Electronics 50PN6504 ab €399,--Diagonale: 50"/127cm • Auflösung: 1920x1080 • Panel: Plasma • Bildwiederholfrequenz: 600Hz (interpoliert) • Kontrast: 3000000:1 (statisch) • 3D: nein • Tuner: 1x DVB-C/-T-Tuner (MPEG-4 AVC) • Video-Anschlüsse: 2x HDMI 1.3, 1x SCART, Komponenten (YPbPr), Composite Video • Weitere Anschlüsse: 1x USB 2.0, LAN, 1x optisch • Gesamtleistung: 20W (2x 10W) • Audio-Codec: Dolby Digital • Energieeffizienzklasse: B • Jahresverbrauch: 187kWh • Stromverbrauch: 128W (typisch), 0.3W (Standby) • Abmessungen mit Standfuß: 116.8x75.5x29.3cm • Abmessungen ohne Standfuß: 116.8x69.9x5.7cm • Gewicht mit Standfuß: 26.10kg • Gewicht ohne Standfuß: 24.70kg • VESA: 400x400 • Herstellergarantie: zwei Jahre

Will result in this output:

    Model;Price;Diagonale;3D;Besonderheiten;Anschlüsse;Energieeffizienzklasse;Standfuß;Tuner;Bildwiederholfrequenz;Panel
    LG Electronics 50PN6504;399;50"/127cm;nein;;1x USB 2.0, LAN, 1x optisch;B;24.70kg;1x DVB-C/-T-Tuner (MPEG-4 AVC);600Hz (interpoliert);Plasma

Using this command: `./list-to-table.py compare_LG-TVs.txt --wanted 'Diagonale,3D,Energieeffizienzklasse,wnschlüsse,Weitere Anschlüsse,Standfuß,Tuner,Bildwiederholfrequenz,Panel,Besonderheiten`
