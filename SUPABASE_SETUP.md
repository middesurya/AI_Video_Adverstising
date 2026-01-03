# Supabase Setup Guide - AI Video Advertising Platform

Complete guide to set up authentication, database, and SaaS features using Supabase.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Create Supabase Project](#step-1-create-supabase-project)
3. [Run Database Migrations](#step-2-run-database-migrations)
4. [Configure Environment Variables](#step-3-configure-environment-variables)
5. [Install Dependencies](#step-4-install-dependencies)
6. [Test Authentication](#step-5-test-authentication)
7. [Verify Database](#step-6-verify-database)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Supabase Account** - Sign up at [https://supabase.com](https://supabase.com) (free tier available)
- **Backend** - Python 3.11+ with pip
- **Frontend** - Node.js 18+ with npm

---

## Step 1: Create Supabase Project

### 1.1 Sign Up and Create Project

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Sign up or log in
3. Click **"New Project"**
4. Fill in project details:
   - **Name**: `ai-video-advertising` (or your preferred name)
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier is sufficient to start

5. Click **"Create new project"**
6. Wait 2-3 minutes for project to initialize

### 1.2 Get Your API Credentials

Once your project is ready:

1. Go to **Settings** → **API**
2. Copy the following values:

```
Project URL: https://xxxxxxxxxxxxx.supabase.co
anon/public key: eyJhbGc...
service_role key: eyJhbGc... (keep this secret!)
```

3. Go to **Settings** → **API** → **JWT Settings**
4. Copy the **JWT Secret**

---

## Step 2: Run Database Migrations

### 2.1 Open SQL Editor

1. In your Supabase dashboard, go to **SQL Editor**
2. Click **"New Query"**
3. Copy and paste the following SQL:

```sql
-- ===========================
-- AI Video Advertising Platform
-- Database Schema
-- ===========================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===== USER PROFILES TABLE =====
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  company TEXT,
  subscription_tier TEXT DEFAULT 'free',
  credits_remaining INT DEFAULT 2,
  total_videos_generated INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===== PROJECTS TABLE =====
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  status TEXT DEFAULT 'draft', -- draft, generating, complete, failed

  -- Ad brief data
  product_name TEXT NOT NULL,
  description TEXT NOT NULL,
  mood INT DEFAULT 50,
  energy INT DEFAULT 50,
  style TEXT DEFAULT 'cinematic',
  archetype TEXT DEFAULT 'hero-journey',
  target_audience TEXT,
  call_to_action TEXT,

  -- Generated content
  script TEXT,
  scenes JSONB,
  video_url TEXT,
  video_duration_seconds INT,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- ===== API USAGE TRACKING TABLE =====
CREATE TABLE api_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

  service TEXT NOT NULL, -- 'runway_ml', 'stability_ai', 'elevenlabs', 'mock'
  operation TEXT NOT NULL, -- 'video_generation', 'audio_generation'

  -- Usage metrics
  units_consumed DECIMAL(10, 2), -- seconds, characters, etc.
  cost_usd DECIMAL(10, 4),

  -- Metadata
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ===== SUBSCRIPTIONS TABLE =====
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  plan_name TEXT NOT NULL, -- 'free', 'pro', 'business'
  status TEXT NOT NULL, -- 'active', 'canceled', 'expired'

  -- Stripe data (for future use)
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,

  -- Limits
  monthly_video_limit INT,
  current_month_usage INT DEFAULT 0,

  -- Dates
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ===== INDEXES FOR PERFORMANCE =====
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);

-- ===== ROW LEVEL SECURITY (RLS) =====
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own profile
CREATE POLICY "Users can view own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = id);

-- Users can only see their own projects
CREATE POLICY "Users can view own projects"
  ON projects FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own projects"
  ON projects FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects"
  ON projects FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects"
  ON projects FOR DELETE
  USING (auth.uid() = user_id);

-- Users can only see their own usage
CREATE POLICY "Users can view own usage"
  ON api_usage FOR SELECT
  USING (auth.uid() = user_id);

-- Users can only see their own subscription
CREATE POLICY "Users can view own subscription"
  ON subscriptions FOR SELECT
  USING (auth.uid() = user_id);

-- ===== TRIGGERS =====

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===== AUTO-CREATE USER PROFILE ON SIGNUP =====

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Create user profile
  INSERT INTO public.user_profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name'
  );

  -- Create free subscription
  INSERT INTO public.subscriptions (
    user_id,
    plan_name,
    status,
    monthly_video_limit,
    current_month_usage,
    current_period_start,
    current_period_end
  )
  VALUES (
    NEW.id,
    'free',
    'active',
    2, -- 2 free videos per month
    0,
    NOW(),
    NOW() + INTERVAL '1 month'
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile and subscription on signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ===== SUCCESS MESSAGE =====
DO $$
BEGIN
  RAISE NOTICE '✅ Database schema created successfully!';
  RAISE NOTICE '✅ Row Level Security enabled';
  RAISE NOTICE '✅ Auto-signup triggers configured';
  RAISE NOTICE '👉 Next: Configure your environment variables';
END $$;
```

4. Click **"Run"** (or press Ctrl/Cmd + Enter)
5. Verify you see success messages at the bottom

### 2.2 Verify Tables Created

1. Go to **Table Editor** in the sidebar
2. You should see 4 tables:
   - `user_profiles`
   - `projects`
   - `api_usage`
   - `subscriptions`

---

## Step 3: Configure Environment Variables

### 3.1 Backend Configuration

1. Navigate to `backend/` directory
2. Copy the example file:
   ```bash
   cp .env.example .env
   ```

3. Edit `backend/.env` and fill in your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Video Generation (optional for now)
USE_MOCK_VIDEO=true

# Other settings
ENV=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3.2 Frontend Configuration

1. Navigate to `frontend/` directory
2. Copy the example file:
   ```bash
   cp .env.local.example .env.local
   ```

3. Edit `frontend/.env.local` and fill in:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-public-key-here

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8002
```

**IMPORTANT**: Use the **anon** key in the frontend, NOT the service role key!

---

## Step 4: Install Dependencies

### 4.1 Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `supabase` - Supabase Python client
- `python-jose[cryptography]` - JWT token verification
- `passlib[bcrypt]` - Password hashing

### 4.2 Frontend Dependencies

```bash
cd frontend
npm install
```

This will install:
- `@supabase/supabase-js` - Supabase JavaScript client
- `@supabase/auth-helpers-nextjs` - Next.js auth helpers

---

## Step 5: Test Authentication

### 5.1 Start the Servers

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8002
```

You should see:
```
✅ Supabase client initialized
✅ Authentication enabled
🚀 AI Ad Video Generator API started successfully
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5.2 Test Signup Flow

1. Open [http://localhost:3000/auth/signup](http://localhost:3000/auth/signup)
2. Fill in the signup form:
   - Full Name: `Test User`
   - Email: `test@example.com`
   - Password: `password123`
3. Click **"Sign Up"**
4. Check your email for confirmation link (if email confirmation is enabled)
5. Click the confirmation link

### 5.3 Test Login

1. Go to [http://localhost:3000/auth/login](http://localhost:3000/auth/login)
2. Enter your credentials
3. Click **"Sign In"**
4. You should be redirected to the home page

### 5.4 Verify User Created

1. Go to Supabase Dashboard → **Authentication** → **Users**
2. You should see your test user listed
3. Go to **Table Editor** → `user_profiles`
4. You should see a profile created automatically
5. Check `subscriptions` table - you should see a free subscription created

---

## Step 6: Verify Database

### 6.1 Test Protected Endpoints

Use the browser console or curl:

```bash
# Get auth token from browser (check Application → Local Storage → supabase.auth.token)
TOKEN="your-access-token-here"

# Test protected endpoint
curl -X GET http://localhost:8002/api/projects \
  -H "Authorization: Bearer $TOKEN"

# Should return: {"projects": []}
```

### 6.2 Test Project Creation

1. Log in to the frontend
2. Create a new ad brief
3. Generate a script
4. Go to Supabase → **Table Editor** → `projects`
5. You should see your project listed

---

## Troubleshooting

### Error: "Authentication not configured"

**Cause:** Supabase environment variables not set correctly

**Solution:**
1. Check `backend/.env` has all three Supabase variables
2. Restart the backend server
3. Verify you see "✅ Supabase client initialized" on startup

### Error: "Invalid authentication credentials"

**Cause:** JWT token is invalid or expired

**Solution:**
1. Log out and log back in
2. Check that `SUPABASE_JWT_SECRET` matches your Supabase project
3. Verify you're using the correct JWT secret from Supabase dashboard

### Error: "No active subscription found"

**Cause:** User doesn't have a subscription record

**Solution:**
1. Check `subscriptions` table in Supabase
2. Manually create a subscription:
   ```sql
   INSERT INTO subscriptions (user_id, plan_name, status, monthly_video_limit)
   VALUES ('user-uuid-here', 'free', 'active', 2);
   ```

### Error: "Row Level Security" policy violation

**Cause:** RLS policies are blocking access

**Solution:**
1. Verify user is authenticated
2. Check that `auth.uid()` matches the `user_id` in the table
3. Review RLS policies in Supabase → **Database** → **Policies**

### Tables not visible in Supabase

**Cause:** SQL script didn't run successfully

**Solution:**
1. Go to **SQL Editor** → **History**
2. Check for error messages
3. Re-run the schema creation script
4. Check **Logs** for detailed error messages

---

## Next Steps

✅ **You're all set!** Your authentication system is configured.

### Optional Enhancements:

1. **Email Templates** - Customize in Supabase → **Authentication** → **Email Templates**
2. **Social Login** - Enable Google/GitHub in **Authentication** → **Providers**
3. **Password Requirements** - Configure in **Authentication** → **Policies**
4. **Rate Limiting** - Add Redis integration (see `SAAS_IMPLEMENTATION_PLAN.md`)
5. **Stripe Payments** - See payment integration guide (coming soon)

---

## API Endpoints Reference

### Public Endpoints (No Auth Required)
- `POST /api/generate-script` - Generate script (unprotected)
- `POST /api/generate-video` - Generate video (unprotected)
- `GET /api/archetypes` - Get story archetypes
- `GET /api/styles` - Get visual styles

### Protected Endpoints (Require Auth)
- `POST /api/generate-script-protected` - Generate script with usage tracking
- `POST /api/generate-video-protected` - Generate video with cost tracking
- `GET /api/projects` - Get user's projects
- `GET /api/projects/{id}` - Get specific project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `GET /api/usage` - Get usage statistics
- `GET /api/subscription` - Get subscription details

---

## Support

- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Supabase Discord**: [https://discord.supabase.com](https://discord.supabase.com)
- **Project Issues**: Check `CLAUDE.md` and `SAAS_IMPLEMENTATION_PLAN.md`

---

**Last Updated:** 2026-01-03
**Status:** Production Ready ✅
