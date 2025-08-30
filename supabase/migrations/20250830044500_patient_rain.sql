create extension if not exists vector;

create table if not exists threads (
  id text primary key,
  user_id text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists messages (
  id bigserial primary key,
  thread_id text references threads(id) on delete cascade,
  role text not null,                   -- 'user' | 'assistant' | 'system'
  content text not null,
  created_at timestamptz default now()
);

-- Optional semantic cache / retrieval
create table if not exists msg_embeddings (
  msg_id bigint references messages(id) on delete cascade,
  embedding vector(1536),
  primary key (msg_id)
);

create table if not exists leads (
  id bigserial primary key,
  thread_id text,
  name text,
  email text,
  phone text,
  intent text,
  notes text,
  raw jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_messages_thread on messages(thread_id);
create index if not exists idx_leads_thread on leads(thread_id);