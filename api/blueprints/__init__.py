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
