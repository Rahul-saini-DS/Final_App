-- Create sequences
CREATE SEQUENCE IF NOT EXISTS users_id_seq;
CREATE SEQUENCE IF NOT EXISTS children_id_seq;
CREATE SEQUENCE IF NOT EXISTS assessment_results_id_seq;
CREATE SEQUENCE IF NOT EXISTS age_groups_id_seq;

-- Users table
CREATE TABLE "users" (
    "user_id" INTEGER PRIMARY KEY DEFAULT nextval('users_id_seq'),
    "parent_name" VARCHAR(100) NOT NULL,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "phone_number" VARCHAR(20),
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Age groups table
CREATE TABLE "age_groups" (
    "age_group_id" INTEGER PRIMARY KEY DEFAULT nextval('age_groups_id_seq'),
    "age_range" VARCHAR(20) NOT NULL UNIQUE,
    "min_age" INTEGER NOT NULL,
    "max_age" INTEGER NOT NULL,
    "display_name" VARCHAR(100) NOT NULL
);

-- Children table
CREATE TABLE "children" (
    "child_id" INTEGER PRIMARY KEY DEFAULT nextval('children_id_seq'),
    "user_id" INTEGER NOT NULL REFERENCES "users"("user_id") ON DELETE CASCADE,
    "child_name" VARCHAR(100) NOT NULL,
    "sex" VARCHAR(10) CHECK (sex IN ('Boy', 'Girl', 'Other')),
    "birth_date" DATE NOT NULL,
    "age_group_id" INTEGER REFERENCES "age_groups"("age_group_id"),
    "city" VARCHAR(100),
    "state" VARCHAR(100),
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assessment results table
CREATE TABLE "assessment_results" (
    "result_id" INTEGER PRIMARY KEY DEFAULT nextval('assessment_results_id_seq'),
    "child_id" INTEGER NOT NULL REFERENCES "children"("child_id") ON DELETE CASCADE,
    "age_group_id" INTEGER REFERENCES "age_groups"("age_group_id"),
    "assessment_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "answers" JSON,
    "scores" JSON,
    "total_score" INTEGER
);

-- Insert age groups with display names
INSERT INTO "age_groups" (age_range, min_age, max_age, display_name) VALUES
('0-1', 0, 12, 'Baby Genius (0–1 yrs) 👶'),
('1-2', 12, 24, 'Toddler Genius (1–2 yrs) 🚼'),
('2-3', 24, 36, 'Little Explorer (2–3 yrs) 🧸'),
('3-4', 36, 48, 'Creative Kid (3–4 yrs) 🎨'),
('4-5', 48, 60, 'Smart Scholar (4–5 yrs) 📚'),
('5-6', 60, 72, 'Young Genius (5–6 yrs) 🌟');
