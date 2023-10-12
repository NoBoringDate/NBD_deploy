from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "bot_config" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "bot_token" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "bug_reports" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL,
    "bug_text" VARCHAR(255) NOT NULL,
    "date_create" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fixed" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "contacts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "description" VARCHAR(255),
    "link" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "filter_questions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "question" VARCHAR(255),
    "answer" text[],
    "answer_to_answer" text[]
);
CREATE TABLE IF NOT EXISTS "global_send" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "send_name" TEXT,
    "tg_id" BIGINT,
    "button_id" INT
);
CREATE TABLE IF NOT EXISTS "id_images" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "images" int[],
    "id_post" VARCHAR(50)  UNIQUE
);
CREATE TABLE IF NOT EXISTS "main_questions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "order" INT  UNIQUE,
    "question" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "main_sessions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT,
    "curent_question" INT,
    "close_question" int[],
    "curent_filter_question" INT,
    "close_filter_question" int[],
    "curent_stat_question" INT,
    "close_stat_question" int[],
    "date_create" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_close" TIMESTAMPTZ,
    "intellect" DOUBLE PRECISION   DEFAULT 0,
    "filter_param" JSONB,
    "stat_answer" JSONB,
    "phys" DOUBLE PRECISION   DEFAULT 0,
    "skill" DOUBLE PRECISION   DEFAULT 0,
    "answers" text[],
    "close" BOOL NOT NULL  DEFAULT False,
    "tag" TEXT
);
CREATE TABLE IF NOT EXISTS "meet_questions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "order" INT  UNIQUE,
    "tag" VARCHAR(255),
    "question" VARCHAR(255),
    "recomended_answer" text[],
    "validation" VARCHAR(255),
    "answer_to_answer" text[]
);
CREATE TABLE IF NOT EXISTS "meet_sessions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT,
    "curent_question" INT,
    "close_question" int[],
    "date_create" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_close" TIMESTAMPTZ,
    "close" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "new_variable" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "answer" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "promoters" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(255),
    "distribution_chanell" VARCHAR(255),
    "ref_link" VARCHAR(255),
    "people_counter" INT   DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "question" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "question" TEXT
);
CREATE TABLE IF NOT EXISTS "ready_suggestions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT,
    "suggestions_1" int[],
    "suggestions_2" int[],
    "suggestions_3" int[],
    "ready_suggestions" int[],
    "sended_suggestion" INT,
    "view_suggestions" int[],
    "session_id" INT NOT NULL REFERENCES "main_sessions" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "ref_links" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "ref_link" TEXT,
    "sug_link" TEXT,
    "ref_counter" INT NOT NULL  DEFAULT 0,
    "sug_counter" INT NOT NULL  DEFAULT 0,
    "sug_title" TEXT
);
CREATE TABLE IF NOT EXISTS "ref_users" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "ref_link" TEXT,
    "user_id" BIGINT,
    "r_sug_id" INT,
    "relink" BOOL NOT NULL  DEFAULT False,
    "date_create" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "send_message" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "user" TEXT,
    "text_message" TEXT,
    "send_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "showed_phone_number" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sug_id" INT,
    "r_sug_id" INT,
    "tg_id" BIGINT,
    "date_click" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "statistic_questions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "question" VARCHAR(255),
    "answer" text[],
    "answer_to_answer" text[]
);
CREATE TABLE IF NOT EXISTS "texts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" VARCHAR(2047),
    "description" TEXT,
    "func" VARCHAR(255),
    "variable" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(255),
    "last_name" VARCHAR(255),
    "login" VARCHAR(255)  UNIQUE,
    "password" VARCHAR(255),
    "password_token" VARCHAR(255),
    "email" VARCHAR(255),
    "role" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "suggestions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" TEXT,
    "description" TEXT,
    "price" TEXT,
    "contact" TEXT,
    "address" TEXT,
    "intellect" DOUBLE PRECISION   DEFAULT 0,
    "phys" DOUBLE PRECISION   DEFAULT 0,
    "skill" DOUBLE PRECISION   DEFAULT 0,
    "tag" TEXT,
    "filter_param" JSONB,
    "cover" VARCHAR(512),
    "images" text[],
    "create_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_modified_time" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "view_counter" INT   DEFAULT 0,
    "real_view_counter" INT   DEFAULT 0,
    "deleted" BOOL NOT NULL  DEFAULT False,
    "deleted_time" TIMESTAMPTZ,
    "author_id" INT REFERENCES "users" ("id") ON DELETE CASCADE,
    "author_edit_id" INT REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_states" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "state" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "users_tg" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(255),
    "first_name" VARCHAR(255),
    "last_name" VARCHAR(255),
    "lang" VARCHAR(255),
    "gender" VARCHAR(255),
    "age" VARCHAR(255),
    "advert" VARCHAR(255),
    "date_create" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_enter" TIMESTAMPTZ,
    "curent_state_id" INT REFERENCES "user_states" ("id") ON DELETE CASCADE,
    "pref_state_id" INT REFERENCES "user_states" ("id") ON DELETE CASCADE,
    "ref_link_id" INT REFERENCES "promoters" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "variables" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "answer" VARCHAR(255),
    "answer_to_answer" VARCHAR(255),
    "intellect" DOUBLE PRECISION,
    "phys" DOUBLE PRECISION,
    "skill" DOUBLE PRECISION
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "main_questions_variables" (
    "main_questions_id" INT NOT NULL REFERENCES "main_questions" ("id") ON DELETE CASCADE,
    "variable_id" INT NOT NULL REFERENCES "variables" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "new_variable_question" (
    "new_variable_id" INT NOT NULL REFERENCES "new_variable" ("id") ON DELETE CASCADE,
    "question_id" BIGINT NOT NULL REFERENCES "question" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "question_new_variable" (
    "question_id" BIGINT NOT NULL REFERENCES "question" ("id") ON DELETE CASCADE,
    "new_variable_id" INT NOT NULL REFERENCES "new_variable" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
