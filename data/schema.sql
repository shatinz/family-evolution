-- Scalable Family Evolution System Database Schema
-- Includes Informed Consent, Confidential Interpersonal Dynamics, and Monthly Longitudinal Evaluations.

CREATE TABLE IF NOT EXISTS family_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_name TEXT DEFAULT 'خانواده ما',
    overview TEXT,
    communication_rules_json TEXT,
    emergency_resources_json TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS family_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_type TEXT NOT NULL, -- 'short_term' or 'long_term'
    title TEXT NOT NULL,
    description TEXT,
    target_date TEXT,
    steps_json TEXT,
    status TEXT DEFAULT 'in_progress',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    name_fa TEXT NOT NULL,
    role TEXT NOT NULL,
    age INTEGER,
    conditions TEXT,
    medical_history TEXT,
    telegram_id INTEGER,
    consent_given INTEGER DEFAULT 0,
    consent_date TEXT,
    is_leader INTEGER DEFAULT 0,
    is_co_leader INTEGER DEFAULT 0,
    avatar TEXT DEFAULT '👤',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now'))
);

-- Monthly & Baseline Systemic Psychological Evaluations
CREATE TABLE IF NOT EXISTS family_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    evaluation_type TEXT NOT NULL, -- 'baseline' or 'monthly'
    date TEXT NOT NULL,
    psychological_safety_score INTEGER, -- 1 to 5
    respect_status_score INTEGER,       -- 1 to 5
    perceived_care_score INTEGER,       -- 1 to 5
    overall_family_climate_score INTEGER, -- 1 to 5
    confidential_narrative_vector TEXT, -- Vector embedding / encrypted narrative
    assessment_notes_json TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Confidential Interpersonal Dynamics (Pairwise Grievances & Appreciations)
CREATE TABLE IF NOT EXISTS interpersonal_dynamics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_member_id INTEGER NOT NULL,
    target_member_id INTEGER NOT NULL,
    hurt_points_encrypted TEXT,        -- Kept strictly confidential for AI analysis only
    appreciate_points_encrypted TEXT,   -- Kept strictly confidential for AI analysis only
    relationship_valence INTEGER DEFAULT 3, -- 1 (very strained) to 5 (very warm)
    date TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY(source_member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY(target_member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Dynamic Intervention Tuning & Adaptations
CREATE TABLE IF NOT EXISTS intervention_adaptations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    trigger_reason TEXT NOT NULL,
    changes_made_json TEXT NOT NULL,
    rationale TEXT,
    measured_impact_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    checkin_type TEXT DEFAULT 'morning',
    mood INTEGER,
    notes TEXT,
    anger_reported INTEGER DEFAULT 0,
    win_of_the_day TEXT,
    raw_data TEXT,
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_fa TEXT NOT NULL,
    title_en TEXT NOT NULL DEFAULT 'Chore',
    category TEXT NOT NULL DEFAULT 'cleaning',
    frequency TEXT NOT NULL DEFAULT 'daily',
    default_assignee_id INTEGER,
    difficulty TEXT DEFAULT 'medium',
    icon TEXT DEFAULT '📋',
    FOREIGN KEY(default_assignee_id) REFERENCES members(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS chore_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chore_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time_slot TEXT DEFAULT 'anytime',
    status TEXT DEFAULT 'pending',
    completed_at TEXT,
    notes TEXT,
    FOREIGN KEY(chore_id) REFERENCES chores(id) ON DELETE CASCADE,
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    title_fa TEXT NOT NULL,
    title_en TEXT NOT NULL DEFAULT 'Habit',
    category TEXT NOT NULL DEFAULT 'general',
    target_frequency TEXT DEFAULT 'daily',
    reminder_time TEXT,
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    status TEXT DEFAULT 'done',
    logged_at TEXT,
    FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conflicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    reported_by_id INTEGER,
    involved_members TEXT,
    trigger_reason TEXT,
    severity INTEGER DEFAULT 1,
    resolution_notes TEXT,
    FOREIGN KEY(reported_by_id) REFERENCES members(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    period_start TEXT,
    period_end TEXT,
    summary_fa TEXT,
    summary_en TEXT,
    recommendations_json TEXT,
    metrics_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    data_json TEXT
);
