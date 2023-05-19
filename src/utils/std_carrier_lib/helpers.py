#!/usr/bin/env python3

import phonenumbers
from phonenumbers import geocoder, carrier

from src.utils.std_carrier_lib import MCCMNC

INVALID_COUNTRY_CODE_EXCEPTION = "INVALID_COUNTRY_CODE"


class InvalidPhoneNUmber(Exception):
    def __init__(self, message="INVALID PHONE NUMBER"):
        self.message = message
        super().__init__(self.message)


class InvalidCountryCode(Exception):
    def __init__(self, message="INVALID COUNTRY CODE"):
        self.message = message
        super().__init__(self.message)


class MissingCountryCode(Exception):
    def __init__(self, message="MISSING COUNTRY CODE"):
        self.message = message
        super().__init__(self.message)


class NotE164Number(Exception):
    def __init__(self, number, message=None):
        self.number = number
        self.message = message or "Not an E164 Number"
        super().__init__(self.message)


class NoMatchOperator(Exception):
    def __init__(self, number, message=None):
        self.number = number
        self.message = message or "no match operator"
        super().__init__(self.message)


class InvalidNumber(Exception):
    def __init__(self, number, message=None):
        self.number = number
        self.message = message or "invalid number"
        super().__init__(self.message)


class BadFormNumber(Exception):
    def __init__(self, number, message=None):
        self.number = number
        self.message = message or "badly formed number"
        super().__init__(self.message)


class NoAvailableModem(Exception):
    def __init__(self, message=None):
        self.message = message or "no available modem"
        super().__init__(self.message)


class CarrierInformation:
    def get_operator_name(
        self, operator_code: str = None, phone_number: str = None
    ) -> str:
        """requires the first 3 digits"""
        if operator_code:
            cm_op_code = (int(operator_code[0:3]), int(operator_code[-1]))
            if cm_op_code in MCCMNC.MNC_dict:
                operator_details = MCCMNC.MNC_dict[cm_op_code]

                if operator_details[0] == int(operator_code):
                    operator_name = str(operator_details[1])
                    # logging.debug("%s", operator_name)

                    return operator_name

            return ""
        else:
            try:
                return self.__get_phonenumber_carrier_name__(MSISDN=phone_number)
            except Exception as error:
                raise error

    def __get_phonenumber_carrier_name__(self, MSISDN: str) -> str:
        """Returns the country of MSISDN.
        Args:
            MSISDN (str):
                The phone number for which country is required.
        Returns:
            (str): country name
        Exceptions:
            INVALID_PHONE_NUMBER_EXCEPTION
            INVALID_COUNTRY_CODE_EXCEPTION
            MISSING_COUNTRY_CODE_EXCEPTION
        """

        try:
            _number = phonenumbers.parse(MSISDN, "en")

            if not phonenumbers.is_valid_number(_number):
                raise InvalidPhoneNUmber()

            return phonenumbers.carrier.name_for_number(_number, "en")

        except phonenumbers.NumberParseException as error:
            if (
                error.error_type
                == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE
            ):
                if MSISDN[0] == "+" or MSISDN[0] == "0":
                    raise InvalidCountryCode() from error
                else:
                    raise MissingCountryCode() from error
            else:
                raise error

        except Exception as error:
            raise error

    def get_country(self, operator_code: str = None, phone_number: str = None) -> str:
        """ """
        if operator_code:
            try:
                """requires the first 3 digits"""
                cm_op_code = int(operator_code[0:3])

                if cm_op_code in MCCMNC.MCC_dict:
                    operator_details = MCCMNC.MCC_dict[cm_op_code]

                    return str(operator_details[0])

            except Exception as error:
                raise error
        else:
            try:
                return self.__get_phonenumber_country__(MSISDN=phone_number)
            except Exception as error:
                raise error

    def __get_phonenumber_country__(self, MSISDN: str) -> str:
        """Returns the country of MSISDN.
        Args:
            MSISDN (str):
                The phone number for which country is required.
        Returns:
            (str): country name
        Exceptions:
            INVALID_PHONE_NUMBER_EXCEPTION
            INVALID_COUNTRY_CODE_EXCEPTION
            MISSING_COUNTRY_CODE_EXCEPTION
        """

        try:
            _number = phonenumbers.parse(MSISDN, "en")

            if not phonenumbers.is_valid_number(_number):
                raise InvalidPhoneNUmber()

            # return phonenumbers.carrier.name_for_number(_number, "en")
            return geocoder.description_for_number(_number, "en")

        except phonenumbers.NumberParseException as error:
            if (
                error.error_type
                == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE
            ):
                if MSISDN[0] == "+" or MSISDN[0] == "0":
                    raise InvalidCountryCode() from error
                else:
                    raise MissingCountryCode() from error
            else:
                raise error

        except Exception as error:
            raise error

    def is_e164(self, MSISDN: str) -> str:
        import re

        """
        https://www.twilio.com/docs/glossary/what-e164
        """

        _rex = re.compile("^\+[1-9]\d{1,14}$")

        return _rex.fullmatch(MSISDN)

    def is_valid_number(self, MSISDN: str) -> bool:
        """ """
        try:
            if self.is_e164(MSISDN):
                _number = phonenumbers.parse(MSISDN, "en")

                if not phonenumbers.is_valid_number(_number):
                    raise InvalidNumber(MSISDN)
            else:
                raise NotE164Number(MSISDN)

        except phonenumbers.NumberParseException as error:
            raise error

        except Exception as error:
            raise error

    def get_operator_code(self, MSISDN: str) -> str:
        """ """
        MSISDN_country = self.__get_phonenumber_country__(MSISDN=MSISDN)
        operator_name = self.__get_phonenumber_carrier_name__(MSISDN=MSISDN)

        operator_id = None
        for IMSI, values in MCCMNC.MCC_dict.items():
            if MSISDN_country == values[0]:
                for key, values in MCCMNC.MNC_dict.items():
                    if IMSI == key[0] and operator_name == values[1]:
                        operator_id = values[0]
                        return str(operator_id)

    def get_country_code(self, operator_code: str) -> str:
        """requires the first 3 digits"""
        cm_op_code = int(operator_code[0:3])

        if cm_op_code in MCCMNC.MCC_dict:
            operator_details = MCCMNC.MCC_dict[cm_op_code]

            return str(operator_details[1])

        return ""

    def validate_MSISDN(self, MSISDN: str) -> bool:
        try:
            _number = phonenumbers.parse(MSISDN, "en")

            if not phonenumbers.is_valid_number(_number):
                raise InvalidNumber(MSISDN)

            return phonenumbers.geocoder.description_for_number(
                _number, "en"
            ), phonenumbers.carrier.name_for_number(_number, "en")

        except phonenumbers.NumberParseException as error:
            if (
                error.error_type
                == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE
            ):
                if MSISDN[0] == "+" or MSISDN[0] == "0":
                    raise BadFormNumber(MSISDN, "INVALID_COUNTRY_CODE") from error
                else:
                    raise BadFormNumber(MSISDN, "MISSING_COUNTRY_CODE") from error

            else:
                raise error

        except Exception as error:
            raise error
