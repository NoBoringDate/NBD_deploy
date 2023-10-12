from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
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
    "date_create" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
