import logging
import re
from datetime import datetime
from spiffworkflow_connector_command.command_interface import CommandResultDictV1
from spiffworkflow_connector_command.command_interface import ConnectorCommand
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


def _extract_value(value):
    """Extract actual value from Config objects or return as-is if string."""
    if hasattr(value, 'value'):
        return str(value.value)
    return str(value)


class SendSMSCommand(ConnectorCommand):
    """
    Command to send an SMS using Twilio.
    """

    def __init__(self, account_sid: str, auth_token: str, from_phone_number: str):
        # Extract actual values from Config objects or convert to string
        self.account_sid = _extract_value(account_sid)
        self.auth_token = _extract_value(auth_token)
        self.from_phone_number = self._validate_phone_number(_extract_value(from_phone_number))
        try:
            self.client = Client(self.account_sid, self.auth_token)
            # Validate credentials by fetching account info
            self.client.api.accounts(self.account_sid).fetch()
            logger.info("Twilio client initialized successfully")
        except TwilioRestException as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            raise ValueError(f"Invalid Twilio credentials: {e}")

    @staticmethod
    def _validate_phone_number(phone_number: str) -> str:
        """
        Validate phone number format (basic E.164 validation).

        Args:
            phone_number (str): Phone number to validate.

        Returns:
            str: Validated phone number.

        Raises:
            ValueError: If phone number format is invalid.
        """
        # E.164 format: +[country code][number] (max 15 digits)
        pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(pattern, phone_number):
            raise ValueError(f"Invalid phone number format: {phone_number}. Expected E.164 format (e.g., +1234567890)")
        return phone_number if phone_number.startswith('+') else f'+{phone_number}'

    def execute(
        self,
        to_phone_number: str,
        message_body: str,
    ) -> CommandResultDictV1:
        """
        Send an SMS message.

        Args:
            to_phone_number (str): The recipient's phone number.
            message_body (str): The body of the SMS message.

        Returns:
            CommandResultDictV1: Result of the command execution.
        """
        try:
            # Extract actual values from Config objects or convert to string
            to_phone_number = _extract_value(to_phone_number)
            message_body = _extract_value(message_body)

            # Validate recipient phone number
            validated_to = self._validate_phone_number(to_phone_number)

            logger.info(f"Sending SMS to {validated_to}")
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_phone_number,
                to=validated_to
            )

            logger.info(f"SMS sent successfully. SID: {message.sid}")
            return {
                "response": {
                    "message_sid": message.sid,
                    "to": validated_to,
                    "from": self.from_phone_number,
                    "status_code": message.status,
                    "timestamp": datetime.utcnow().isoformat(),
                    "details": f"Message sent to {validated_to}"
                },
                "status": 200,
                "mimetype": "application/json"
            }
        except TwilioRestException as e:
            logger.error(f"Twilio API error: {e.code} - {e.msg}")
            return {
                "response": {
                    "error_type": "TwilioRestException",
                    "error_code": e.code,
                    "error_message": e.msg,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "status": 400,
                "mimetype": "application/json"
            }
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                "response": {
                    "error_type": "ValueError",
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                },
                "status": 400,
                "mimetype": "application/json"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "response": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                },
                "status": 500,
                "mimetype": "application/json"
            }