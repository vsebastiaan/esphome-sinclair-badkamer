# Badkamer — Sinclair met UART-herstel (0.0.2-retry)

Afzonderlijke fork van gekkehenkie11/esphome_gree_ac, broncommit
`91f280231ff3fdc2eeb0f59857254aee8e24ad82`. De Tosot/Bora-repository blijft ongewijzigd.

## Herstel

- Eerste passieve statuspoging na twee seconden; zonder geldig antwoord opnieuw na twee seconden.
- Gebruik van de bestaande Sinclair no-change-markering; tijdens herstel geen temperatuur/modus uit oude of onbekende climate-state coderen.
- Na wegvallen van geldige status wordt een nog lopende bedieningsopdracht geannuleerd. Geen automatische replay na herstel.
- Alleen een gecontroleerd statusframe herstelt de verbinding. Korte frames, ongeldige checksum en andere typen geven geen bedieningsvrijgave.
- Onvolledige frames worden na 250 ms zonder ontvangen byte opgeruimd; onmogelijke lengtes en bufferoverloop herstarten de parser.
- Iedere 15 seconden een INFO `LINK`-regel, ook als er helemaal geen aircoverkeer is.

`rx_bytes=0` betekent geen ontvangen bytes sinds opstart. `rx_bytes` zonder `valid` betekent dat bytes binnenkomen maar nog geen bruikbaar statusframe. `invalid` telt afgekeurde complete frames; `partial_resets` telt parserherstel. `retries` telt antwoordtimeouts. `last_valid_age_ms` is tot de eerste geldige ontvangst de tijd sinds opstart (zie `valid=0`).

## Upload en controle

Gebruik bij voorkeur de vaste commit van deze wijziging als `external_components.source.ref` in de bestaande YAML. De voorbeeldconfig volgt main. UART-pinnen, inversie, snelheid en SHT31 blijven hetzelfde; API-/wifi-/OTA-secrets blijven lokaal.

Compileer en upload via je eigen ESPHome-installatie. Controleer vervolgens minimaal 30 seconden log op `0.0.2-retry`, `LINK`, `TX`, `RX` en `AC communication established`. Test daarna bewust ontvochtigen en uitschakelen en controleer de fysieke reactie. Controleer ook gezamenlijk spanningsloos maken en herstarten van airco en D1.

Dit herstel is nog niet op de fysieke badkamerunit gevalideerd. Het ontbreken van een retry was aantoonbaar; de oorzaak van het oorspronkelijke communicatieverlies is nog niet bewezen. De bestaande protocolmarkering voor no-change moet op deze unit ook tijdens herstel worden bevestigd.

## Tests

`ASAN_OPTIONS=detect_leaks=0 python3 tests/run.py`

Hosttest compileert de echte twee component-C++-bestanden tegen minimale ESPHome/UART-testdubbels, met AddressSanitizer en UndefinedBehaviorSanitizer. Test startup zonder antwoord, herhaalde retries, het ontvangen badkamerframe (19 graden / doel 25), dry-opdracht, verloren antwoord, geen replay, offline blokkering, corrupte/korte/onvolledige frames, synchronisatieherstel en millis-overloop.

Dit is geen volledige ESP8266-firmwarebuild en bewijst geen elektrische/protocolcompatibiliteit op de hardware.
