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
    <GetDigits timeout="15" finishOnKey="#" callbackUrl="https://voice-ivr.herokuapp.com/hooks/get_digit_webhook/account/1">
        <Say>Welcome to ploar solar Self service portal, please enter your account number followed by the hash sign to proceed</Say>
    </GetDigits>
    <GetDigits timeout="15" finishOnKey="#" callbackUrl="https://voice-ivr.herokuapp.com/hooks/get_digit_webhook/account/1">
        <Say> please enter your account number followed by the hash sign to proceed</Say>
    </GetDigits>
    <Say>We did not get your account number. Good bye</Say>
</Response>
"""

GET_OPTION_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits timeout="15" finishOnKey="#" callbackUrl="https://voice-ivr.herokuapp.com/hooks/get_digit_webhook/option/{account}">
        <Say>To check your loan balance press 1 followed by hash sign.  To check your most recent token press 2 followed by hash sign</Say>
    </GetDigits>
    <GetDigits timeout="15" finishOnKey="#" callbackUrl="https://voice-ivr.herokuapp.com/hooks/get_digit_webhook/option/{account}">
        <Say> To check your loan balance press 1 followed by hash sign.  To check your most recent token press 2 followed by hash sign</Say>
    </GetDigits>
    <Say>We did not get your option. Good bye</Say>
</Response>
"""

GET_BALANCE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Your loan balance is {balance} kenyan shilings. I repeat your loan balance is {balance} kenyan shilings.</Say>
</Response>
"""


GET_TOKEN_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Your latest keycode token is {token}. I repeat your latest keycode token is {token}</Say>
</Response>
"""

WRONG_OPTION_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>The option you selected does not exist. Good bye</Say>
</Response>
"""