# AlphaBeat World Card — Fase 3: integrazione account

**Stato:** specifica tecnica. Nessuna integrazione attiva, nessuna modifica a Supabase, Stripe o produzione.

## Identità e profilo
- Unica identità: UUID Supabase `auth.users.id`, non indirizzo email.
- Tessera BASIC gratuita solo per account autenticato con email verificata.
- Il nome sulla tessera è personalizzabile, validato e visualizzato in sicurezza.
- La demo GitHub Pages rimane pubblica, con dati fittizi e senza token personali.
- L'accesso fra domini diversi richiede un flusso SSO progettato e testato: non presumere condivisione automatica delle sessioni.

## Abbonamenti
- Leggere lo stato del piano da una fonte server-side autorevole, da identificare nell'attuale sistema Stripe/Redis.
- Non assegnare piani da parametri browser, metadata utente modificabili o valori non verificati.
- Stato incerto: mostrare «Verifica in corso» senza attribuire vantaggi PRO.
- Non modificare checkout, portale clienti, webhook o abbonamenti esistenti.

## Sicurezza
- Non esporre service_role Supabase, chiavi Stripe o dati personali nei file statici.
- Se servirà una nuova tabella esposta, attivare RLS e policy con controllo proprietario `(select auth.uid()) = user_id`.
- Verificare prima la corrispondenza fra UUID Supabase e Stripe customer ID.
- Tenere separati autenticazione, profilo e autorizzazione agli abbonamenti.

## Test prima del rilascio
1. Ospite non vede profili personali.
2. Utente A non può leggere dati dell'utente B.
3. Email non verificata: nessuna tessera personale attiva.
4. Utente verificato senza piano: BASIC.
5. Abbonamento attivo/scaduto/cancellato: livello corretto.
6. Webhook duplicato, ritardato o fuori ordine: nessuna promozione indebita.
7. Logout e sessione cross-domain: nessuna fuga di dati.
8. Grafica BASIC approvata e servizi esistenti invariati.

## Sequenza
Audit in sola lettura → contratto API e test → preview isolata → autorizzazione esplicita prima di qualunque modifica alla produzione.
