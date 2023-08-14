"""Utility functions for working with carrier services."""

import logging
from src.utils.std_carrier_lib.helpers import CarrierInformation

logger = logging.getLogger(__name__)
carrier_information = CarrierInformation()


def get_service_name(
    service_id: str, project_reference: str, phone_number: str = None
) -> str:
    """
    Returns a service name for a given service, project reference, and phone number (optional).

    :param service_id: str - The unique identifier for the service.
    :param project_reference: str - A unique reference for the project.
    :param phone_number: str, optional - A phone number to use for getting the country and carrier name.

    :return: str - The generated service name in the format of "{project_reference}_{country_dialing_code}_{operator_code}".
    """
    try:
        if service_id.lower() == "sms":
            country_dialing_code = carrier_information.get_country_code(
                phone_number=phone_number
            )
            operator_code = carrier_information.get_operator_code(MSISDN=phone_number)
            service_name = f"{project_reference}_{country_dialing_code}_{operator_code}"

            logger.info("Successfully generated service name")

            return service_name

        return None

    except Exception as error:
        logger.error("Failed to generate service name for service_id '%s'", service_id)
        raise error
