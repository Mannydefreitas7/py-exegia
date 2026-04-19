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

## Database Schema

### Tables

See @src/models/CLAUDE.md for detailed schema documentation.

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

## Local Development

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

## Production Deployment

### Push Migrations

```bash
supabase db push
```

### Deploy Functions

```bash
supabase functions deploy
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
supabase db reset --seed
```

## Security Best Practices

1. **Always use RLS**: Never disable Row Level Security
2. **Validate JWT tokens**: Verify tokens in edge functions
3. **Use service role key carefully**: Only for admin operations
4. **Encrypt sensitive data**: Use pgcrypto for sensitive fields
5. **Rate limit**: Implement rate limiting on edge functions
6. **Schedule backup**: Enable automatic backups
