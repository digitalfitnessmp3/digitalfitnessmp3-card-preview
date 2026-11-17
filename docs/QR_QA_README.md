# AlphaBeat World Card — QR verificabile, solo QA

**Non è una funzione live.** La PR resta draft. L'implementazione viene deliberatamente rifiutata salvo `CARD_QA_ENABLED=true` e configurazione corretta.

## Stato e flusso

- La card BASIC rosa/arancione e `qr-demo.html` della PR #1 rimangono una demo pubblica: il QR fisso porta solo alla homepage.
- `POST /api/card/issue` richiede un Bearer JWT Supabase verificato sul server, account `CARD_QA_USER_ID` esplicitamente confermato BASIC non-admin e consenso a un pilot del titolare. Gira un nuovo token casuale al momento dell'emissione; ritorna un URL di verifica con token nel frammento `#code=...`, non nel percorso/query trasmesso al server. Non associare utenti per ordine record. **Non integrare in una tessera reale senza il renderer di QR dinamico**.
- `POST /api/card/verify` with JSON `{code}` restituisce solo `valid BASIC`, `expired`, `revoked` o `invalid`, senza identificativi personali.
- `POST /api/card/revoke` richiede lo stesso login QA per revocare il token.
- `card-verifica.html` mostra l'esito minimo, rimuove il codice dall'indirizzo visibile e non include analytics.
- I token sono casuali a 256 bit, archiviati solo come SHA-256. Non sono password, credenziali, login, attestazioni di pagamento o autorizzazioni per download.

## Configurazione QA (mai nei file pubblici)

- `CARD_QA_ENABLED` default `false` (attivare solo nel branch QA o staging controllato)
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` **segreti soltanto sul server**
- `CARD_PUBLIC_ORIGIN` URL HTTPS esatto del dominio di prova
- `CARD_QA_USER_ID` UUID di uno degli account del titolare, confermato tramite backend come BASIC e non admin
- `CARD_QA_ACCOUNT_CLASS=basic_non_admin_verified` solo dopo verifica backend dell'account selezionato
- `CARD_ADMIN_USER_IDS` elenco UID owner/admin esclusi, separati da virgole, server-side

Non usare mai l'account amministratore, né il quinto account esterno privo di consenso.

## Passaggi restanti prima del rilascio

1. Verificare UID tecnico di un account BASIC di proprietà del titolare e lista admin reale, senza esporre dati personali nei PR.
2. Revisione SQL prima di creare la tabella `card_qr_qa_tokens`; oggi non è presente. Nessuno schema è stato modificato da questa PR.
3. Attivare i flag solo nell'ambiente QA controllato, proteggere gli endpoint con rate limiting WAF/Cloudflare e verificare il modello RLS.
4. Integrare un renderer QR offline/dinamico che codifichi l'`verification_url` restituita da `issue` (non la semplice homepage).
5. Verificare scansione con un secondo dispositivo, status `valid`, revoca, scadenza, link inventato e richiesta non autorizzata. Gli utenti reali rimangono esclusi.
6. Solo dopo collaudo, revisione sicurezza e autorizzazione di rilascio, integrare nella Card in «Il mio profilo»; niente modifiche a OS/admin, pagamenti o abbonamenti.

## Note di sicurezza

- Non registrare token, query di verifica o bearer negli analytics, log applicativi, crash report, referrer o servizi di terze parti.
- Impostare no-store/no-referrer per le pagine e API, e un controllo su log del gateway/CDN; i parametri URL trasmessi ai server possono finire nei log: il token qui viaggia nel solo frammento, poi nel corpo POST della richiesta di verifica.
- Ruoli e permessi verificati server-side, mai da etichette o `user_metadata` modificabile.
- Il pilot QA non concede privilegi: ogni accesso riservato è autenticato separatamente.
- Questa PR non crea servizi, non avvia deploy, non interroga account esterni e non genera costi.

## Avanzamento 17 novembre 2026 — collegamento profilo (codice QA)

La tabella `public.card_qr_qa_tokens` è stata creata nel progetto Supabase esistente e verificata: RLS attiva, nessun permesso diretto di SELECT per `anon` o `authenticated`, zero codici emessi al momento della verifica. **La tabella è reale; la funzione QR non è attiva sul sito.**

- `GET /api/card/me`: verifica lo stato della tessera del SOLO account pilot, senza restituire token, email o identificativi.
- `POST /api/card/issue`: emette e sostituisce un codice, lo restituisce solo nella risposta di quel momento; il backend conserva solo il digest SHA-256.
- `POST /api/card/revoke`: revoca il codice. `POST /api/card/verify`: verifica senza login e non permette accessi riservati.
- `card-qa.html`: interfaccia mobile BASIC che legge la sessione esistente `DFMP3AdminAuth` soltanto se montata sullo stesso origin, mai su un dominio che non condivide l'autenticazione.
- `vendor/qrcode.min.js`: generatore MIT incluso localmente; nessun token è inviato a servizi di terze parti.
- `qa-tests/card-status.test.mjs` e `qa-tests/card-qa-ui.test.mjs`: nuovi contratti QA. Eseguire `npm test` localmente prima di ogni pubblicazione.

### **Blocchi per rilascio e prova con l'account**

1. Non basta l'email confermata per l'autorizzazione. Verificare e registrare un singolo UID pilot BASIC non-admin, controllando anche la lista completa degli amministratori in `CARD_ADMIN_USER_IDS`. Le protezioni rifiutano richieste se quest'ultima manca.
2. Configurare segreti e variabili esclusivamente lato server, su un servizio QA isolato con **stesso origin** della pagina e protezione antiabuso; non aggiungere privilegi al database, account o abbonamenti.
3. Collegare la pagina al profilo dell'ambiente QA. La UI di questo repo non può funzionare da sola su GitHub perché non contiene il sistema di login.
4. Testare con secondo dispositivo: emissione, scansione, stato attivo, rigenerazione, revoca, logout, account admin, URL inventati e sessione scaduta.
5. Non attivare o pubblicare alcuna tessera sul sito live prima del collaudo end-to-end e della verifica del metodo di deploy. Non effettuare merge automatico della PR.
6. Il QR emesso non è recuperabile dal database in chiaro: dopo un refresh, l'utente può visualizzare lo stato della card, ma deve rigenerare il QR. Questa è una limitazione intenzionale del **pilot**; per una card stabile servirà un archivio cifrato server-side o una diversa architettura.
