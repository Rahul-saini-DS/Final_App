-- Add detailed question responses table
CREATE TABLE IF NOT EXISTS "question_responses" (
    "response_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "result_id" INTEGER NOT NULL REFERENCES "assessment_results"("result_id") ON DELETE CASCADE,
    "child_id" INTEGER NOT NULL REFERENCES "children"("child_id") ON DELETE CASCADE,
    "assessment_type" VARCHAR(20) NOT NULL CHECK (assessment_type IN ('intelligence', 'physical', 'linguistic')),
    "question_id" VARCHAR(50) NOT NULL,
    "question_text" TEXT NOT NULL,
    "child_answer" TEXT,
    "correct_answer" TEXT,
    "is_correct" BOOLEAN DEFAULT FALSE,
    "response_time_seconds" INTEGER,
    "difficulty_level" INTEGER DEFAULT 1,
    "attempts" INTEGER DEFAULT 1,
    "hints_used" INTEGER DEFAULT 0,
    "ai_confidence_score" FLOAT,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS "idx_question_responses_child_assessment" 
ON "question_responses" ("child_id", "assessment_type", "created_at");

CREATE INDEX IF NOT EXISTS "idx_question_responses_result" 
ON "question_responses" ("result_id");

-- Add detailed AI task responses table
CREATE TABLE IF NOT EXISTS "ai_task_responses" (
    "ai_response_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "result_id" INTEGER NOT NULL REFERENCES "assessment_results"("result_id") ON DELETE CASCADE,
    "child_id" INTEGER NOT NULL REFERENCES "children"("child_id") ON DELETE CASCADE,
    "task_type" VARCHAR(30) NOT NULL,
    "task_name" VARCHAR(100) NOT NULL,
    "success_count" INTEGER DEFAULT 0,
    "total_attempts" INTEGER DEFAULT 0,
    "completion_time_seconds" INTEGER,
    "success_rate" FLOAT,
    "ai_feedback" TEXT,
    "was_completed" BOOLEAN DEFAULT FALSE,
    "was_skipped" BOOLEAN DEFAULT FALSE,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for AI task responses
CREATE INDEX IF NOT EXISTS "idx_ai_task_responses_child_task" 
ON "ai_task_responses" ("child_id", "task_type", "created_at");
