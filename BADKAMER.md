# Badkamer — Sinclair-proef

Afzonderlijke fork van gekkehenkie11/esphome_gree_ac, broncommit `91f280231ff3fdc2eeb0f59857254aee8e24ad82`. De componentcode is ongewijzigd. De bestaande Tosot/Bora-repository is niet gewijzigd.

Gebruik `examples/badkamer-airco.yaml`. UART, D1 mini en SHT31 volgen de aangeleverde badkamerconfiguratie. Het interne climate-id `tosot_badkamer` blijft behouden; de platformnaam wordt `sinclair_ac`.

Het voorbeeld verwacht naast bestaande wifi-/OTA-secrets ook `badkamer_airco_api_key` en `badkamer_airco_fallback_password`. Zet daar lokaal de huidige waarden in. Publiceer secrets.yaml niet. Je kunt ook uitsluitend external_components en climate in je bestaande YAML vervangen.

## Eerste controle

Compileer in je eigen ESPHome-installatie en upload daarna zelf. Deze fork is nog niet gecompileerd of op de badkamerunit getest. Bewaar de huidige YAML als terugval.

Controleer na upload de opstartlog, ontvangen frames, publicatie van klimaatstatus en temperatuur van de binnenunit. Vergelijk met de afstandsbediening. De SHT31-metingen alleen bewijzen geen aircocommunicatie. De eerdere `0x30/0x31`-frames zijn aanleiding voor deze proef, geen bewijs dat alle Sinclair-velden op deze unit kloppen. Oude Tosot-tellers hoeven niet in deze component voor te komen.

Bij een compileerfout: bewaar de eerste fout plus ESPHome-versie. Bij communicatieproblemen: bewaar de opstartlog en minstens 30 seconden VERBOSE-log. Geen firmware of fysieke bediening is vanuit deze sessie uitgevoerd.
