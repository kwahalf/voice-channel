from io import StringIO

def make_template_file(template_string):
    # type: (Text) -> Text
    _file = StringIO(template_string)
    template = _file.getvalue()
    _file.close()
    return template


VOICE_CALLBACK__REJECT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<response>
	<Reject/>
</response>
"""

GET_DIGIT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits timeout="30" finishOnKey="#" callbackUrl="https://voice-ivr.herokuapp.com/hooks/get_digit_webhook">
        <Say>Please enter your account number followed by the hash sign</Say>
    </GetDigits>
    <Say>We did not get your account number. Good bye</Say>
</Response>
"""
