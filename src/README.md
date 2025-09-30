# Connector Twilio

A SpiffWorkflow connector proxy for sending SMS messages via Twilio. This connector allows you to send SMS notifications after user tasks are completed in your SpiffWorkflow engine.

## Features

- Send SMS messages using Twilio API
- Phone number validation (E.164 format)
- Comprehensive error handling with detailed error messages
- Logging for debugging and auditing
- Credential validation on initialization

## Installation

```bash
cd src
poetry install
```

## Configuration

You'll need the following Twilio credentials:
- Account SID
- Auth Token
- From Phone Number (Twilio number)

## Usage

```python
from connector_twilio.commands.send_sms import SendSMSCommand

# Initialize the command with your Twilio credentials
sms_command = SendSMSCommand(
    account_sid="your_account_sid",
    auth_token="your_auth_token",
    from_phone_number="+1234567890"
)

# Send an SMS
result = sms_command.execute(
    to_phone_number="+0987654321",
    message_body="Hello from SpiffWorkflow!"
)

# Check the result
if result["status"] == "success":
    print(f"Message sent! SID: {result['message_sid']}")
else:
    print(f"Error: {result['error_message']}")
```

## Response Format

### Success Response
```python
{
    "status": "success",
    "message_sid": "SM...",
    "to": "+1234567890",
    "from": "+0987654321",
    "status_code": "queued",
    "timestamp": "2025-09-30T22:30:00.000000",
    "details": "Message sent to +1234567890"
}
```

### Error Response
```python
{
    "status": "error",
    "error_type": "TwilioRestException",
    "error_code": 21211,
    "error_message": "Invalid 'To' Phone Number",
    "timestamp": "2025-09-30T22:30:00.000000"
}
```

## Phone Number Format

Phone numbers must be in E.164 format:
- Start with `+` followed by country code
- Maximum 15 digits
- Example: `+1234567890`

## Requirements

- Python ^3.11
- Twilio account with active phone number
- SpiffWorkflow Connector Command

## Dependencies

- `spiffworkflow-connector-command`
- `twilio ^9.8.3`
- `fastapi ^0.118.0`

## License

See LICENSE file for details.

## Author

buhariabubakar <buharikwmbo@yahoo.com>
