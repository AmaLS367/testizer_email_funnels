import logging

from config.settings import load_settings
from db.connection import database_connection_scope
from db.selectors import (
    get_language_test_candidates,
    get_non_language_test_candidates,
)
from logging_config.logger import configure_logging
from brevo.api_client import BrevoApiClient
from brevo.models import BrevoContact


def main() -> None:
    settings = load_settings()
    configure_logging(settings.application.log_level)

    logger = logging.getLogger("app.main")

    logger.info("Application environment: %s", settings.application.environment)
    logger.info("Dry run mode: %s", settings.application.dry_run)

    logger.info("Connecting to database")
    with database_connection_scope(settings.database) as connection:
        logger.info("Connected to database successfully")

        logger.info("Fetching language test candidates (placeholder)")
        language_candidates = get_language_test_candidates(connection, max_rows=10)
        logger.info("Language candidates count: %s", len(language_candidates))

        logger.info("Fetching non language test candidates (placeholder)")
        non_language_candidates = get_non_language_test_candidates(connection, max_rows=10)
        logger.info("Non language candidates count: %s", len(non_language_candidates))

        if language_candidates:
            logger.info("First language candidate row: %s", language_candidates[0])

        if non_language_candidates:
            logger.info("First non language candidate row: %s", non_language_candidates[0])

        brevo_client: BrevoApiClient | None = None

        if (
            settings.brevo.language_tests_list_id > 0
            or settings.brevo.non_language_tests_list_id > 0
        ):
            brevo_client = BrevoApiClient(
                api_key=settings.brevo.api_key or "",
                base_url=settings.brevo.base_url,
                dry_run=settings.application.dry_run,
            )
        else:
            logger.info(
                "Brevo list ids are not configured, skipping Brevo synchronization",
            )

        if brevo_client is not None:
            if (
                language_candidates
                and settings.brevo.language_tests_list_id > 0
            ):
                first_language_row = language_candidates[0]
                first_language_email = str(first_language_row[1])

                language_contact = BrevoContact(
                    email=first_language_email,
                    list_ids=[settings.brevo.language_tests_list_id],
                    attributes={"FUNNEL_TYPE": "language_test"},
                )

                logger.info(
                    "Sending sample language contact to Brevo: %s",
                    language_contact.email,
                )
                brevo_client.create_or_update_contact(language_contact)

            if (
                non_language_candidates
                and settings.brevo.non_language_tests_list_id > 0
            ):
                first_non_language_row = non_language_candidates[0]
                first_non_language_email = str(first_non_language_row[1])

                non_language_contact = BrevoContact(
                    email=first_non_language_email,
                    list_ids=[settings.brevo.non_language_tests_list_id],
                    attributes={"FUNNEL_TYPE": "non_language_test"},
                )

                logger.info(
                    "Sending sample non language contact to Brevo: %s",
                    non_language_contact.email,
                )
                brevo_client.create_or_update_contact(non_language_contact)

    logger.info("Job finished")


if __name__ == "__main__":
    main()
