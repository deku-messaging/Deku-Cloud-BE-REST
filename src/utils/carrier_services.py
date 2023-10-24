"""
Utility functions for working with carrier services.
"""

import logging

from werkzeug.exceptions import BadRequest

from src.utils.std_carrier_lib.helpers import CarrierInformation

logger = logging.getLogger(__name__)
carrier_information = CarrierInformation()


def get_service_name(
    service_id: str,
    project_reference: str,
    phone_number: str = None,
    country_dialing_code: str = None,
    operator_code: str = None,
) -> str:
    """
    Returns a service name for a given service, project reference,
    and phone number (optional). If both country_dialing_code and
    operator_code are not provided, it generates them from the phone_number.

    :param service_id: str - The unique identifier for the service.
    :param project_reference: str - A unique reference for the project.
    :param phone_number: str, optional - A phone number to use for getting
    the country and carrier name.
    :param country_dialing_code: str, optional - The country dialing code.
    :param operator_code: str, optional - The operator code.

    :return: str - The generated service name in the format of
    "{project_reference}_{country_dialing_code}_{operator_code}".
    """
    try:
        if service_id.lower() == "sms":
            if not country_dialing_code or not operator_code:
                if not phone_number:
                    raise BadRequest(
                        "phone_number is required to generate \
                        country_dialing_code and operator_code"
                    )
                country_dialing_code = carrier_information.get_country_code(
                    phone_number=phone_number
                )
                operator_code = carrier_information.get_operator_code(
                    MSISDN=phone_number
                )

                logger.info(
                    "Generating country_dialing_code '%s' and operator_code '%s' from phone_number",
                    country_dialing_code,
                    operator_code,
                )

            service_name = f"{project_reference}_{country_dialing_code}_{operator_code}"

            logger.info("Successfully generated service name")

            return service_name

        return None

    except Exception as error:
        logger.error("Failed to generate service name for service_id '%s'", service_id)
        raise error
