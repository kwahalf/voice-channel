import flask
import xmltodict
from flask.views import MethodView
from api.util import jsonify, dejsonify, sanitize_arguments
import logging

from api.blueprints import (
    VOICE_CALLBACK__REJECT_TEMPLATE,
    GET_DIGIT_TEMPLATE,
    GET_OPTION_TEMPLATE,
    GET_BALANCE_TEMPLATE,
    GET_TOKEN_TEMPLATE,
    WRONG_OPTION_TEMPLATE,
    make_template_file

    )


logger = logging.getLogger("voice")
logging.basicConfig(level=logging.DEBUG)


class WebhookBase(MethodView):
    def emit_success_message(self):
        message = {"status": "SUCCESS"}
        jsonified_message = jsonify(dict(message=message))
        response = flask.Response(jsonified_message, mimetype="application/json")
        return response

    def emit_xml_response(self, xml):
        response = flask.Response(xml, mimetype="text/xml")
        return response

    def make_reject_payload(self):
        return make_template_file(
            VOICE_CALLBACK__REJECT_TEMPLATE
        )

    def make_get_digit_payload(self):
        return make_template_file(
            GET_DIGIT_TEMPLATE
        )

    def make_get_option_payload(self, account):
        return make_template_file(
            GET_OPTION_TEMPLATE.format(account=account)
        )

    def make_get_balance_payload(self, balance):
        return make_template_file(
            GET_BALANCE_TEMPLATE.format(balance=balance)
        )

    def make_get_token_payload(self, token):
        return make_template_file(
            GET_TOKEN_TEMPLATE.format(token=token)
        )

    def make_get_wrong_option_payload(self):
        return make_template_file(
            WRONG_OPTION_TEMPLATE
        )



class Voice(WebhookBase):
    def get(self):
        # Webhook verification
        return self.emit_success_message()

    def post(self):
        logger.info(
            "received notification %s",
                flask.request.values
        )

        raw_data = flask.request.data

        # parsed_data = xmltodict.parse(raw_data, process_namespaces=False)

        # logger.info(
        #     "paseed data is %s",
        #         parsed_data
        # )

        status = flask.request.form.get("callSessionState", None)

        if status == "Completed":
            xml = self.make_reject_payload()
            self.emit_xml_response(xml)


        xml = self.make_get_digit_payload()

        return self.emit_xml_response(xml)


class GetDigit(WebhookBase):
    def get(self):
        # Webhook verification
        return self.emit_success_message()

    def post(self, digit_type, value):
        logger.info(
            "received notification %s",
                flask.request.values
        )

        raw_data = flask.request.data

        digits =  flask.request.form.get("dtmfDigits", None)

        # parsed_data = xmltodict.parse(raw_data, process_namespaces=False)

        # logger.info(
        #     "paseed data is %s",
        #         parsed_data
        # )

        if digit_type == "account":
            xml = self.make_get_option_payload(digits)
            return self.emit_xml_response(xml)

        if digit_type == "option":
            if digits == "1":
                xml = self.make_get_balance_payload(300)
                return self.emit_xml_response(xml)
            if digits == "2":
                xml = self.make_get_token_payload("*. 1 . 2 . 4 . 6 . 9 . 0 . 7 . 9 . #.")
                return self.emit_xml_response(xml)
            xml = self.make_get_wrong_option_payload()
            return self.emit_xml_response(xml)




        xml = self.make_reject_payload()

        return self.emit_xml_response(xml)


    


def create_blueprint(at_prefix, **kwargs):
    """webhook blueprint"""
    blueprint = flask.Blueprint("webhook", __name__)
    blueprint.add_url_rule("/webhook", view_func=Voice.as_view("webhook"))
    blueprint.add_url_rule("/get_digit_webhook/<digit_type>/<value>", view_func=GetDigit.as_view("get_digit_webhook"))

    return blueprint
