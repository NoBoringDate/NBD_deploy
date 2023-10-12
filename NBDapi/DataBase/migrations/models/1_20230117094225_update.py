from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "send_message" ADD "status" TEXT;
        ALTER TABLE "users_tg" ADD "text_view" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users_tg" DROP COLUMN "text_view";
        ALTER TABLE "send_message" DROP COLUMN "status";"""
