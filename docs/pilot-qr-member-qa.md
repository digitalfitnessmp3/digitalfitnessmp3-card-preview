# Pilot QR reale — AlphaBeat World BASIC Card (QA, non pubblicato)

## Obiettivo
Testare la scansione QR **solo su uno dei quattro account di proprietà del titolare**, purché sia BASIC e non amministratore, senza esporre dati personali e senza modificare ruoli, abbonamenti o accessi. Il quinto account appartiene a una persona esterna sconosciuta e deve essere escluso da qualsiasi test nominativo senza consenso.

## Situazione verificata (17 novembre 2026)
- L'interfaccia pubblica del sito mostra una card BASIC e l'etichetta "QR IN ARRIVO".
- Nel progetto Supabase associato a DigitalFitnessMP3 Studio ci sono 5 record in `auth.users`. Il titolare ha chiarito che 4 account sono suoi e 1 appartiene a una persona esterna che non conosce. La corrispondenza tra i quattro account e i record tecnici non è ancora accertata.
- Nello schema `public` esaminato non è stata trovata una tabella specifica per i profili pubblici delle card.
- `qr-demo.html` contiene un QR di sola navigazione verso `https://digitalfitnessmp3.com/`; non è una tessera verificabile. La matrice del QR è stata confrontata con un generatore QR Code e corrisponde.

## Requisiti di sicurezza prima di collegare l'utente
1. Identificare un account BASIC **di proprietà del titolare** sul server, senza mai scegliere automaticamente la prima riga di `auth.users`. L'account esterno non è una risorsa QA.
2. Escludere in modo esplicito gli account admin/owner/QA sulla base di autorizzazioni **server-side**: mai fidarsi di claim modificabili dal cliente.
3. Per il pilot usare solo un account del titolare; un eventuale futuro test con l'utente esterno richiede consenso esplicito. Per il primo pilot utilizzare informazioni pubbliche minime: `BASIC`, `tessera valida`, nome pubblico scelto dall'utente solo se ha aderito.
4. Generare un identificatore QR casuale ad alta entropia, indipendente da UID, email, Stripe ID e token di sessione; conservare sul server solo un hash dell'identificatore se possibile. La verifica deve essere di sola lettura e revocabile.
5. Il QR non effettua login e non dà diritto a download, pagamenti o gestione abbonamento; ogni accesso riservato richiede sessione autenticata e controlli lato server.
6. Preferire un endpoint limitato e controllato per verifica `valid / revoked / not found`, con limitazione richieste, nessun dato sensibile e nessun provider key riservato nel frontend.
7. Abilitare RLS su nuove tabelle pubbliche e testare isolamenti tra membri; evitare `SECURITY DEFINER` non necessario.

## Sequenza collaudo
- **QA 0**: test demo QR con Nothing Phone, senza login.
- **QA 1**: confermare uno dei 4 account del titolare come BASIC non-admin (nessuna PII nel ticket/PR); NON usare il quinto account esterno.
- **QA 2**: generazione token per l'account QA del titolare tramite servizio lato server in staging.
- **QA 3**: scansione con smartphone non autenticato -> esito minimale di verifica, nessun accesso privilegiato.
- **QA 4**: scansione con account amministratore -> nessuna modifica, nessun accesso delegato.
- **QA 5**: revoca token -> la verifica non risulta valida; controllo URL inventati/non autorizzati.
- **QA 6**: nessuna modifica al sito live senza verifica QA, revisione sicurezza e approvazione al rilascio.

## Lavori successivi separati
1. Android APK: confermare la baseline reale `2.1.2`, package `com.digitalfitnessmp3.app`, prima di qualunque build; non tornare a versioni precedenti.
2. BPM: verificare differenza audio tra originale/remix e regolazione manuale senza alterare il motore Fitness 32 funzionante. Evitare batteria aggiunta.
3. Nessun deploy, costi, modifica account o backend effettuati da questo documento.
