-- REVIEW ONLY. DO NOT APPLY TO THE LIVE DATABASE WITHOUT APPROVAL.
-- Isolated QR QA token storage. No personal details exposed to public clients.
create table if not exists public.card_qr_qa_tokens (
  user_id uuid not null references auth.users(id) on delete cascade,
  token_digest text not null primary key check (token_digest ~ '^[a-f0-9]{64}$'),
  issued_at timestamptz not null default now(),
  expires_at timestamptz not null,
  revoked_at timestamptz,
  constraint card_qr_qa_tokens_member_unique unique (user_id)
);
alter table public.card_qr_qa_tokens enable row level security;
revoke all on table public.card_qr_qa_tokens from public, anon, authenticated;
grant select, insert, update, delete on table public.card_qr_qa_tokens to service_role;
-- NO RLS policies for anon/authenticated: deny all direct client access.
-- Only backend QA endpoints may use service_role; never ship it to a client.
