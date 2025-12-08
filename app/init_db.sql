-- Database initialization script for AWS Certifications Coach
-- This script creates the initial database schema for Snowflake

CREATE DATABASE AWS_CERTIFICATIONS;

-- Use the database
USE DATABASE AWS_CERTIFICATIONS;
USE SCHEMA PUBLIC;

-- Create logged_users table
CREATE OR REPLACE TABLE logged_users (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    target_certification VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create chat_history table
CREATE OR REPLACE TABLE chat_history (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES logged_users(id)
);

-- Create user_progress table
CREATE  OR REPLACE TABLE user_progress (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    study_time_minutes INTEGER DEFAULT 0,
    practice_tests_taken INTEGER DEFAULT 0,
    average_score INTEGER DEFAULT 0,
    storage_topic_progress INTEGER DEFAULT 0,
    compute_topic_progress INTEGER DEFAULT 0,
    networking_topic_progress INTEGER DEFAULT 0,
    security_topic_progress INTEGER DEFAULT 0,
    database_topic_progress INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    total_questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    accuracy_percentage INTEGER DEFAULT 0,
    services_studied INTEGER DEFAULT 0,
    weak_areas VARCHAR,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES logged_users(id)
);


-- Activity log table
CREATE  OR REPLACE TABLE activity_log (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    user_id INTEGER,
    activity VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES logged_users(id)
);

-- Exam sessions table for practice exam tracking
CREATE OR REPLACE TABLE exam_sessions (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    certification VARCHAR(255) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    incorrect_answers INTEGER NOT NULL,
    percentage FLOAT NOT NULL,
    passed BOOLEAN NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER NOT NULL,
    answer_breakdown VARIANT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES logged_users(id)
);
