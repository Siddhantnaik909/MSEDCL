"""Initialize and migrate the configured database before starting Gunicorn."""

from config.settings import settings
from init_db import init_db
from migrate_db import run_migrations


def main():
    init_db(settings.database_path)
    run_migrations(settings.database_path)


if __name__ == "__main__":
    main()
