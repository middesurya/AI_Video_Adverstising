# SaaS Implementation Plan - Complete Guide

## 🎯 Your Requirements
- ✅ Public deployment
- ✅ Prevent API abuse
- ✅ Track per-user costs/limits
- ✅ Users save/load projects
- ✅ Build as SaaS product

---

## 🚀 Recommended Stack

### **Backend:**
- FastAPI (current) ✅
- **Supabase** - Auth + Database + Storage
- **Redis** - Caching + rate limiting
- **Celery** - Background jobs
- **Stripe** - Payments

### **Frontend:**
- Next.js (current) ✅
- **NextAuth.js** - Authentication
- **Supabase Client** - Database access
- **SWR** - Data fetching

### **Infrastructure:**
- **Docker** (current) ✅
- **Vercel** - Frontend hosting (free tier)
- **Railway/Render** - Backend hosting ($5-10/month)
- **Supabase** - Database + Auth (free tier)
- **Cloudflare R2** - Video storage ($0.015/GB)

**Total Monthly Cost:** ~$15-30 for starter plan

---

## 📅 Implementation Timeline: 3-4 Weeks

### **Week 1: Authentication & Database**
- Days 1-2: Supabase setup + schema
- Days 3-4: Authentication implementation
- Day 5: Testing & debugging

### **Week 2: Core Features**
- Days 1-2: Project CRUD operations
- Days 3-4: Usage tracking + cost calculation
- Day 5: Rate limiting per user

### **Week 3: Payments & Polish**
- Days 1-3: Stripe integration
- Days 4-5: UI/UX improvements

### **Week 4: Testing & Launch**
- Days 1-2: Security audit
- Days 3-4: Load testing
- Day 5: Deploy to production

---

## 🔐 Step 1: Supabase Setup (START HERE)

### 1.1 Create Supabase Project

```bash
# 1. Go to https://supabase.com
# 2. Sign up (free)
# 3. Create new project
# 4. Copy your credentials:
#    - API URL
#    - anon/public key
#    - service_role key (secret!)
```

### 1.2 Database Schema

Run this SQL in Supabase SQL Editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (Supabase Auth handles this, but we can extend it)
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

-- Projects table
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

-- API usage tracking
CREATE TABLE api_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

  service TEXT NOT NULL, -- 'runway_ml', 'stability_ai', 'elevenlabs'
  operation TEXT NOT NULL, -- 'video_generation', 'audio_generation'

  -- Usage metrics
  units_consumed DECIMAL(10, 2), -- seconds, characters, etc.
  cost_usd DECIMAL(10, 4),

  -- Metadata
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Subscription plans
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  plan_name TEXT NOT NULL, -- 'free', 'pro', 'business'
  status TEXT NOT NULL, -- 'active', 'canceled', 'expired'

  -- Stripe data
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

-- Rate limiting (optional, can use Redis instead)
CREATE TABLE rate_limits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  endpoint TEXT NOT NULL,
  request_count INT DEFAULT 0,
  window_start TIMESTAMP DEFAULT NOW(),

  UNIQUE(user_id, endpoint)
);

-- Indexes for performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);

-- Row Level Security (RLS) Policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON user_profiles FOR UPDATE
  USING (auth.uid() = id);

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

CREATE POLICY "Users can view own usage"
  ON api_usage FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can view own subscription"
  ON subscriptions FOR SELECT
  USING (auth.uid() = user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
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

-- Function to create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name'
  );

  -- Create free subscription
  INSERT INTO public.subscriptions (user_id, plan_name, status, monthly_video_limit, current_month_usage)
  VALUES (
    NEW.id,
    'free',
    'active',
    2, -- 2 free videos per month
    0
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();
```

---

## 🔑 Step 2: Backend Authentication

### 2.1 Install Dependencies

```bash
cd backend
pip install supabase python-jose[cryptography] passlib[bcrypt]
```

### 2.2 Create Auth Service

Create `backend/auth.py`:

```python
"""
Authentication service using Supabase
"""
from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt, JWTError
import os

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """
    Verify JWT token and return current user

    Usage in endpoints:
        @app.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": user["sub"]}
    """
    token = credentials.credentials

    try:
        # Verify JWT token
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


class SubscriptionChecker:
    """Check user subscription and limits"""

    @staticmethod
    async def check_video_generation_allowed(user_id: str) -> bool:
        """Check if user can generate videos"""
        # Get user subscription
        result = supabase.table("subscriptions") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("status", "active") \
            .single() \
            .execute()

        if not result.data:
            raise HTTPException(
                status_code=403,
                detail="No active subscription found"
            )

        subscription = result.data

        # Check limits
        if subscription["current_month_usage"] >= subscription["monthly_video_limit"]:
            raise HTTPException(
                status_code=403,
                detail=f"Monthly limit reached ({subscription['monthly_video_limit']} videos). Upgrade your plan."
            )

        return True

    @staticmethod
    async def increment_usage(user_id: str):
        """Increment user's video generation count"""
        # Increment usage
        supabase.rpc(
            "increment_video_usage",
            {"user_id_param": user_id}
        ).execute()


# Database helper functions
class Database:
    """Database operations"""

    @staticmethod
    async def create_project(user_id: str, project_data: dict):
        """Create a new project"""
        result = supabase.table("projects").insert({
            "user_id": user_id,
            **project_data
        }).execute()

        return result.data[0]

    @staticmethod
    async def get_user_projects(user_id: str):
        """Get all projects for a user"""
        result = supabase.table("projects") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()

        return result.data

    @staticmethod
    async def get_project(project_id: str, user_id: str):
        """Get a specific project"""
        result = supabase.table("projects") \
            .select("*") \
            .eq("id", project_id) \
            .eq("user_id", user_id) \
            .single() \
            .execute()

        return result.data

    @staticmethod
    async def update_project(project_id: str, user_id: str, updates: dict):
        """Update a project"""
        result = supabase.table("projects") \
            .update(updates) \
            .eq("id", project_id) \
            .eq("user_id", user_id) \
            .execute()

        return result.data[0] if result.data else None

    @staticmethod
    async def delete_project(project_id: str, user_id: str):
        """Delete a project"""
        supabase.table("projects") \
            .delete() \
            .eq("id", project_id) \
            .eq("user_id", user_id) \
            .execute()

    @staticmethod
    async def track_api_usage(user_id: str, project_id: str, service: str,
                              operation: str, units: float, cost: float, metadata: dict = None):
        """Track API usage"""
        supabase.table("api_usage").insert({
            "user_id": user_id,
            "project_id": project_id,
            "service": service,
            "operation": operation,
            "units_consumed": units,
            "cost_usd": cost,
            "metadata": metadata or {}
        }).execute()
```

### 2.3 Update main.py with Protected Routes

Add to `backend/main.py`:

```python
from auth import get_current_user, SubscriptionChecker, Database
from fastapi import Depends

# Protected endpoint example
@app.post("/api/generate-script-protected", response_model=ScriptResponse)
async def generate_script_protected(
    brief: AdBrief,
    user = Depends(get_current_user)
):
    """Generate script (requires authentication)"""
    user_id = user["sub"]

    try:
        # Check subscription limits
        await SubscriptionChecker.check_video_generation_allowed(user_id)

        # Generate script
        script, scenes = generate_mock_script(brief)

        # Save project to database
        project = await Database.create_project(user_id, {
            "name": f"{brief.productName} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "product_name": brief.productName,
            "description": brief.description,
            "mood": brief.mood,
            "energy": brief.energy,
            "style": brief.style,
            "archetype": brief.archetype,
            "target_audience": brief.targetAudience or "",
            "call_to_action": brief.callToAction or "",
            "script": script,
            "scenes": [scene.dict() for scene in scenes],
            "status": "draft"
        })

        return ScriptResponse(
            success=True,
            script=script,
            scenes=scenes,
            project_id=project["id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Script generation error: {e}")
        return ScriptResponse(
            success=False,
            error=str(e)
        )


# Projects CRUD
@app.get("/api/projects")
async def get_projects(user = Depends(get_current_user)):
    """Get all user projects"""
    user_id = user["sub"]
    projects = await Database.get_user_projects(user_id)
    return {"projects": projects}


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str, user = Depends(get_current_user)):
    """Get specific project"""
    user_id = user["sub"]
    project = await Database.get_project(project_id, user_id)
    return {"project": project}


@app.put("/api/projects/{project_id}")
async def update_project(
    project_id: str,
    updates: dict,
    user = Depends(get_current_user)
):
    """Update project"""
    user_id = user["sub"]
    project = await Database.update_project(project_id, user_id, updates)
    return {"project": project}


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, user = Depends(get_current_user)):
    """Delete project"""
    user_id = user["sub"]
    await Database.delete_project(project_id, user_id)
    return {"message": "Project deleted"}


# Usage stats
@app.get("/api/usage")
async def get_usage(user = Depends(get_current_user)):
    """Get user's usage statistics"""
    user_id = user["sub"]

    # Get subscription info
    subscription = supabase.table("subscriptions") \
        .select("*") \
        .eq("user_id", user_id) \
        .single() \
        .execute()

    # Get usage this month
    usage = supabase.table("api_usage") \
        .select("*") \
        .eq("user_id", user_id) \
        .gte("created_at", datetime.now().replace(day=1).isoformat()) \
        .execute()

    total_cost = sum(float(u["cost_usd"]) for u in usage.data)

    return {
        "subscription": subscription.data,
        "monthly_usage": {
            "videos_generated": len([u for u in usage.data if u["operation"] == "video_generation"]),
            "total_cost_usd": total_cost
        }
    }
```

---

## 🎨 Step 3: Frontend Authentication

### 3.1 Install Dependencies

```bash
cd frontend
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs
```

### 3.2 Create Supabase Client

Create `frontend/lib/supabase.js`:

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 3.3 Create Auth Context

Create `frontend/contexts/AuthContext.js`:

```javascript
import { createContext, useContext, useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check active sessions
    const session = supabase.auth.getSession()
    setUser(session?.user ?? null)
    setLoading(false)

    // Listen for auth changes
    const { data: listener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => {
      listener.subscription.unsubscribe()
    }
  }, [])

  const value = {
    user,
    loading,
    signIn: (email, password) => supabase.auth.signInWithPassword({ email, password }),
    signUp: (email, password, metadata) => supabase.auth.signUp({
      email,
      password,
      options: { data: metadata }
    }),
    signOut: () => supabase.auth.signOut(),
    resetPassword: (email) => supabase.auth.resetPasswordForEmail(email)
  }

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
```

### 3.4 Create Login/Signup Pages

Create `frontend/pages/auth/login.js`:

```javascript
import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useRouter } from 'next/router'
import styles from '../../styles/Auth.module.css'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const { signIn } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const { error } = await signIn(email, password)
      if (error) throw error
      router.push('/')
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.authContainer}>
      <div className={styles.authCard}>
        <h1>Sign In</h1>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p>
          Don't have an account? <a href="/auth/signup">Sign up</a>
        </p>
      </div>
    </div>
  )
}
```

Similar file for `signup.js`...

---

## 💳 Step 4: Stripe Integration (Optional for now)

I can provide the complete Stripe setup if you want to start charging users.

---

## 📦 Environment Variables Needed

### Backend (.env)
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Video APIs (existing)
RUNWAY_API_KEY=your-runway-key
STABILITY_API_KEY=your-stability-key
ELEVENLABS_API_KEY=your-elevenlabs-key
USE_MOCK_VIDEO=false

# Stripe (optional for now)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8002
```

---

## ✅ Next Steps

Would you like me to:

1. **Implement the full authentication system?**
   - Create all the auth files
   - Add protected routes
   - Add project CRUD

2. **Set up the database schema in Supabase?**
   - Run the SQL migrations
   - Set up RLS policies

3. **Add Stripe integration?**
   - Subscription plans
   - Payment processing
   - Webhook handling

4. **Create the pricing page?**
   - Plan comparison
   - Checkout flow

Let me know and I'll implement it! 🚀
