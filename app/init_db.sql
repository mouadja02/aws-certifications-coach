-- Database initialization script for AWS Certifications Coach
-- This script creates the initial database schema

-- Create logged_users table
CREATE TABLE IF NOT EXISTS logged_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    target_certification VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat_history table
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES logged_users(id) ON DELETE CASCADE
);

-- Create user_progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    study_time_minutes INTEGER DEFAULT 0,
    practice_tests_taken INTEGER DEFAULT 0,
    average_score INTEGER DEFAULT 0,
    progress_percentage INTEGER DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES logged_users(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_logged_users_email ON logged_users(email);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history(created_at);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating updated_at
DROP TRIGGER IF EXISTS update_logged_users_updated_at ON logged_users;
CREATE TRIGGER update_logged_users_updated_at
    BEFORE UPDATE ON logged_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_progress_updated_at ON user_progress;
CREATE TRIGGER update_user_progress_updated_at
    BEFORE UPDATE ON user_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional - for testing)
-- Password is 'password123' (in production, this should be hashed)
-- INSERT INTO logged_users (name, email, password, target_certification, age) 
-- VALUES ('Demo User', 'demo@awscoach.com', 'password123', 'AWS Certified Solutions Architect - Associate', 25)
-- ON CONFLICT (email) DO NOTHING;

-- Grant necessary permissions (if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO awscoach;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO awscoach;

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
END $$;

