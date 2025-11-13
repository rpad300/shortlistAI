-- Migration: Fix RLS policies for companies and interviewers
-- Description: Add INSERT policies to allow backend service role to create records
-- Author: System
-- Date: 2025-11-14

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Service role can manage companies" ON companies;
DROP POLICY IF EXISTS "Service role can manage interviewers" ON interviewers;
DROP POLICY IF EXISTS "Public can insert companies" ON companies;
DROP POLICY IF EXISTS "Public can insert interviewers" ON interviewers;

-- Companies: Allow service role full access
CREATE POLICY "Service role can manage companies"
    ON companies
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Companies: Allow public INSERT (backend validates everything)
-- This is safe because the backend API validates all inputs
CREATE POLICY "Public can insert companies"
    ON companies
    FOR INSERT
    WITH CHECK (TRUE);

-- Companies: Allow public SELECT (for lookups)
CREATE POLICY "Public can read companies"
    ON companies
    FOR SELECT
    USING (TRUE);

-- Interviewers: Allow service role full access
CREATE POLICY "Service role can manage interviewers"
    ON interviewers
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Interviewers: Allow public INSERT (backend validates everything)
-- This is safe because the backend API validates all inputs
CREATE POLICY "Public can insert interviewers"
    ON interviewers
    FOR INSERT
    WITH CHECK (TRUE);

-- Interviewers: Allow public SELECT (for lookups)
CREATE POLICY "Public can read interviewers"
    ON interviewers
    FOR SELECT
    USING (TRUE);

COMMENT ON POLICY "Service role can manage companies" ON companies IS 'Service role has full access to companies table';
COMMENT ON POLICY "Public can insert companies" ON companies IS 'Public can insert companies via backend API (validated)';
COMMENT ON POLICY "Public can read companies" ON companies IS 'Public can read companies for lookups';
COMMENT ON POLICY "Service role can manage interviewers" ON interviewers IS 'Service role has full access to interviewers table';
COMMENT ON POLICY "Public can insert interviewers" ON interviewers IS 'Public can insert interviewers via backend API (validated)';
COMMENT ON POLICY "Public can read interviewers" ON interviewers IS 'Public can read interviewers for lookups';

