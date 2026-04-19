# Supabase Module

Database, storage, authentication, and edge functions for the Exegia API.

## Overview

Supabase provides the backend infrastructure:

- **Database**: PostgreSQL with Row Level Security (RLS)
- **Storage**: Object storage for dataset files
- **Auth**: User authentication and authorization
- **Edge Functions**: Serverless functions for Git fetching and processing

## Architecture

```
Desktop Client
    ↓
Supabase Edge Functions (Optional)
    ↓
┌─────────────────────────────┐
│  Supabase (Cloud Backend)   │
│  ┌─────────────────────┐    │
│  │ PostgreSQL Database │    │
│  │ • users             │    │
│  │ • notes             │    │
│  │ • favorites         │    │
│  │ • user_datasets     │    │
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │ Storage Buckets     │    │
│  │ • bibles/           │    │
│  │ • lexicons/         │    │
│  │ • dictionaries/     │    │
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │ Auth                │    │
│  │ • JWT tokens        │    │
│  │ • RLS policies      │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
```

## Files Structure

```
supabase/
├── migrations/              # Database migrations
│   ├── 20240101000000_initial_schema.sql
│   ├── 20240102000000_add_notes.sql
│   └── ...
├── functions/               # Edge functions
│   ├── fetch-tf-dataset/    # Git repository fetching
│   └── process-upload/      # Dataset processing
├── seed.sql                 # Seed data for development
└── config.toml              # Supabase configuration
```

## Database Schema

### Tables

See [../app/models/CLAUDE.md](../app/models/CLAUDE.md) for detailed schema documentation.

**Core Tables:**

- `profiles` - User profiles (extends auth.users)
- `notes` - User notes on passages
- `favorites` - User favorite passages
- `user_datasets` - Downloaded datasets tracking

### Row Level Security (RLS)

All tables use RLS to ensure data isolation:

```sql
-- Enable RLS on table
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own notes
CREATE POLICY "Users manage own notes"
    ON notes FOR ALL
    USING (auth.uid() = user_id);
```

### Migrations

#### Create Migration

```bash
# Using Supabase CLI
bunx supabase migration new add_tags_to_notes

# Edit the generated file in supabase/migrations/
```

#### Run Migrations

```bash
# Local development
bunx supabase db reset

# Production
bunx supabase db push
```

#### Example Migration

```sql
-- supabase/migrations/20240115000000_add_tags_to_notes.sql

-- Add tags column to notes
ALTER TABLE notes ADD COLUMN tags TEXT[];

-- Create index for tag searches
CREATE INDEX idx_notes_tags ON notes USING GIN(tags);

-- Update RLS policies (if needed)
```

## Storage Buckets

### Bucket Organization

```
storage/
├── bibles/              # Public read, auth write
│   ├── BHSA.zip
│   ├── KJV.zip
│   └── ...
├── lexicons/            # Public read, auth write
├── dictionaries/        # Public read, auth write
└── books/               # Public read, auth write
```

### Bucket Policies

```sql
-- Create bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('bibles', 'bibles', true);

-- Policy: Anyone can read
CREATE POLICY "Public read access"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'bibles');

-- Policy: Authenticated users can upload
CREATE POLICY "Authenticated upload"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'bibles' AND
        auth.role() = 'authenticated'
    );

-- Policy: Only admins can delete
CREATE POLICY "Admin delete"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'bibles' AND
        auth.jwt() ->> 'role' = 'admin'
    );
```

### Storage Operations

```python
from supabase import create_client

supabase = create_client(url, key)

# List files
files = supabase.storage.from_('bibles').list()

# Upload
supabase.storage.from_('bibles').upload('dataset.zip', file_bytes)

# Download
data = supabase.storage.from_('bibles').download('dataset.zip')

# Delete
supabase.storage.from_('bibles').remove(['old.zip'])

# Get public URL
url = supabase.storage.from_('bibles').get_public_url('dataset.zip')
```

## Authentication

### User Registration

```python
# Sign up
response = supabase.auth.sign_up({
    "email": "user@example.com",
    "password": "securepassword"
})

# Creates user in auth.users
# Triggers profile creation in profiles table
```

### User Login

```python
# Sign in
response = supabase.auth.sign_in_with_password({
    "email": "user@example.com",
    "password": "securepassword"
})

# Returns JWT token
access_token = response.session.access_token
```

### Token Usage

```python
# Set auth token
supabase.auth.set_session(access_token, refresh_token)

# All subsequent queries use this user's context
# RLS policies automatically filter data
notes = supabase.table('notes').select('*').execute()
```

### Auth in FastAPI

```python
from app.auth import get_current_user

@router.get("/notes")
async def get_notes(user = Depends(get_current_user)):
    # user is authenticated
    # RLS ensures they only see their notes
    pass
```

## Edge Functions

Serverless functions running on Deno Deploy.

### Fetch TF Dataset Function

```typescript
// supabase/functions/fetch-tf-dataset/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
  const { repo_url, dataset_id, version } = await req.json();

  // 1. Clone Git repository
  const repo = await Deno.run({
    cmd: ["git", "clone", repo_url, "/tmp/repo"],
  });

  // 2. Extract .tf files
  const tfFiles = await extractTfFiles("/tmp/repo");

  // 3. Create ZIP
  const zip = await createZip(tfFiles);

  // 4. Upload to Storage
  await uploadToStorage(zip, dataset_id);

  return new Response(JSON.stringify({ success: true }), {
    headers: { "Content-Type": "application/json" },
  });
});
```

### Deploy Function

```bash
bunx supabase functions deploy fetch-tf-dataset
```

### Invoke Function

```python
# From Python
response = supabase.functions.invoke("fetch-tf-dataset", {
    "body": {
        "repo_url": "https://github.com/ETCBC/bhsa",
        "dataset_id": "BHSA",
        "version": "2021"
    }
})
```

## Configuration (`config.toml`)

```toml
[project]
id = "your-project-ref"
name = "Exegia"

[database]
port = 54322

[api]
port = 54321

[auth]
site_url = "http://localhost:3000"
additional_redirect_urls = ["http://localhost:8000"]

[storage]
file_size_limit = "50MB"

[functions.fetch-tf-dataset]
verify_jwt = true
```

## Local Development

### Start Supabase

```bash
# Start all services
bunx supabase start

# Output includes:
# - API URL: http://localhost:54321
# - DB URL: postgresql://postgres:postgres@localhost:54322/postgres
# - Studio URL: http://localhost:54323
```

### Access Studio

Supabase Studio (local dashboard): **http://localhost:54323**

Features:

- Table editor
- SQL editor
- Storage browser
- Auth users
- Database migrations

### Stop Supabase

```bash
bunx supabase stop
```

## Environment Variables

Required in `.env`:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database (for direct connection)
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
```

## Production Deployment

### Link Project

```bash
bunx supabase link --project-ref your-project-ref
```

### Push Migrations

```bash
bunx supabase db push
```

### Deploy Functions

```bash
bunx supabase functions deploy
```

## Testing

### Seed Data

```sql
-- supabase/seed.sql

-- Create test user (via Supabase dashboard or Auth API)

-- Insert test notes
INSERT INTO notes (user_id, dataset_id, reference, content)
VALUES
  ('user-uuid', 'BHSA', 'Genesis 1:1', 'Test note 1'),
  ('user-uuid', 'KJV', 'John 3:16', 'Test note 2');

-- Insert test favorites
INSERT INTO favorites (user_id, dataset_id, reference)
VALUES
  ('user-uuid', 'BHSA', 'Psalm 23:1');
```

### Run Seeds

```bash
bunx supabase db reset --seed
```

## Monitoring

### Database Logs

```bash
bunx supabase db logs
```

### Storage Logs

```bash
bunx supabase storage logs
```

### Function Logs

```bash
bunx supabase functions logs fetch-tf-dataset
```

## Security Best Practices

1. **Always use RLS**: Never disable Row Level Security
2. **Validate JWT tokens**: Verify tokens in edge functions
3. **Use service role key carefully**: Only for admin operations
4. **Encrypt sensitive data**: Use pgcrypto for sensitive fields
5. **Rate limit**: Implement rate limiting on edge functions
6. **Backup regularly**: Enable automatic backups

## Related Documentation

- [Database Models](../app/models/CLAUDE.md) - Schema and models
- [Storage Service](../app/storage/CLAUDE.md) - Storage operations
- [GraphQL API](../app/graphql/CLAUDE.md) - API using Supabase
- [Supabase Docs](https://supabase.com/docs)

## Useful Commands

```bash
# Initialize Supabase
bunx supabase init

# Start local Supabase
bunx supabase start

# Create migration
bunx supabase migration new migration_name

# Reset database
bunx supabase db reset

# Push to production
bunx supabase db push

# Deploy functions
bunx supabase functions deploy

# View logs
bunx supabase db logs
```
