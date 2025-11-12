-- Migration: Create admin_users table for management
-- Description: Table to store admin users for secure authentication and management
-- Date: 2025-11-12

-- Create admin_users table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_by UUID, -- Self-reference for audit
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    updated_by UUID -- Self-reference for audit
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_active ON admin_users(is_active);

-- Enable RLS (Row Level Security)
ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for admin users
-- Only authenticated admins can read all admin users
CREATE POLICY "Admin users can read all admin users" ON admin_users
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM admin_users 
            WHERE username = auth.jwt() ->> 'sub' 
            AND is_active = true
        )
    );

-- Only super admins can insert new admin users
CREATE POLICY "Super admins can insert admin users" ON admin_users
    FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM admin_users 
            WHERE username = auth.jwt() ->> 'sub' 
            AND is_active = true
            AND role = 'super_admin'
        )
    );

-- Only super admins can update admin users
CREATE POLICY "Super admins can update admin users" ON admin_users
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM admin_users 
            WHERE username = auth.jwt() ->> 'sub' 
            AND is_active = true
            AND role = 'super_admin'
        )
    );

-- Only super admins can delete admin users (soft delete)
CREATE POLICY "Super admins can delete admin users" ON admin_users
    FOR DELETE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM admin_users 
            WHERE username = auth.jwt() ->> 'sub' 
            AND is_active = true
            AND role = 'super_admin'
        )
    );

-- Function to handle password hashing
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(password, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to verify password
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (crypt(password, hash) = hash);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_admin_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER update_admin_users_updated_at
    BEFORE UPDATE ON admin_users
    FOR EACH ROW
    EXECUTE FUNCTION update_admin_users_updated_at();

-- Insert default super admin user
-- Password: admin123 (hashed)
INSERT INTO admin_users (
    username,
    email,
    password_hash,
    first_name,
    last_name,
    role,
    is_active,
    created_at
) VALUES (
    'admin',
    'admin@shortlistai.com',
    crypt('admin123', gen_salt('bf', 12)),
    'Default',
    'Administrator',
    'super_admin',
    true,
    now()
) ON CONFLICT (username) DO NOTHING;

-- Grant permissions to authenticated role
GRANT SELECT, INSERT, UPDATE, DELETE ON admin_users TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Comments for documentation
COMMENT ON TABLE admin_users IS 'Admin users table for managing platform administrators';
COMMENT ON COLUMN admin_users.id IS 'Unique identifier for admin user';
COMMENT ON COLUMN admin_users.username IS 'Unique username for login';
COMMENT ON COLUMN admin_users.email IS 'Unique email for login and notifications';
COMMENT ON COLUMN admin_users.password_hash IS 'Bcrypt hashed password';
COMMENT ON COLUMN admin_users.first_name IS 'Admin first name';
COMMENT ON COLUMN admin_users.last_name IS 'Admin last name';
COMMENT ON COLUMN admin_users.role IS 'Admin role: admin, super_admin';
COMMENT ON COLUMN admin_users.is_active IS 'Whether admin account is active';
COMMENT ON COLUMN admin_users.last_login_at IS 'Last successful login timestamp';
COMMENT ON COLUMN admin_users.failed_login_attempts IS 'Number of failed login attempts';
COMMENT ON COLUMN admin_users.locked_until IS 'Account lock expiration timestamp';
COMMENT ON COLUMN admin_users.created_at IS 'Account creation timestamp';
COMMENT ON COLUMN admin_users.updated_at IS 'Last account update timestamp';
COMMENT ON COLUMN admin_users.created_by IS 'Admin who created this account';
COMMENT ON COLUMN admin_users.updated_by IS 'Admin who last updated this account';

-- Security note
COMMENT ON FUNCTION hash_password(TEXT) IS 'Hash password using bcrypt with salt';
COMMENT ON FUNCTION verify_password(TEXT, TEXT) IS 'Verify password against hash';
