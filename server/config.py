import os
from dotenv import load_dotenv


class EnvironmentConfig:

    # Load configuration from file
    load_dotenv(
        os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", ".env")
        )
    )

    # Database connection
    POSTGRES_USER = os.getenv("POSTGRES_USER", None)
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", None)
    POSTGRES_ENDPOINT = os.getenv("POSTGRES_ENDPOINT", "postgresql")
    POSTGRES_DB = os.getenv("POSTGRES_DB", None)
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)

    REPORT_FILE_REPOSITORY_PATH = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "report_files_repository/")
    )
    GIT_SSH_SCRIPT = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "my_ssh_executable.sh")
    )

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}"
        + f":{POSTGRES_PASSWORD}"
        + f"@{POSTGRES_ENDPOINT}:"
        + f"{POSTGRES_PORT}"
        + f"/{POSTGRES_DB}"
    )

    SECRET_KEY = os.getenv("SECRET_KEY", "")

    # Some more definitions (not overridable)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
