import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.infrastructure.database import metadata
from app.infrastructure.config import settings

config = context.config
# ConfigParser trata "%" como interpolação, e a senha codificada na URL gera "%21", "%23"...
config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL", settings.DATABASE_URL).replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

conexao = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
with conexao.connect() as connection:
    context.configure(connection=connection, target_metadata=metadata)
    with context.begin_transaction():
        context.run_migrations()
