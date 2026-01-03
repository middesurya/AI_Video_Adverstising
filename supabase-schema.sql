-- ===========================
-- AI Video Advertising Platform
-- Database Schema for Supabase
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
  RAISE NOTICE '👉 Next: Install dependencies and start your servers!';
END $$;
