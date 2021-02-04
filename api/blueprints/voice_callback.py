import os
import flask
import requests
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
    NO_TOKEN_TEMPLATE,
    NO_ACCOUNT_TEMPLATE,
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

    def make_get_no_account_payload(self):
        return make_template_file(
            NO_ACCOUNT_TEMPLATE
        )

    def make_get_no_token_payload(self):
        return make_template_file(
            NO_TOKEN_TEMPLATE
        )

    def construct_connects_url(self):
        domain = os.environ.get("CONNECTS_DOMAIN")
        url = f"https://{domain}/data"
        return url

    def get_requests_auth(self):
        return (os.environ.get("CONNECTS_USERNAME"), os.environ.get("CONNECTS_PASSWORD"))

    def find_account(self, account_number):
        endpoint = f"/accounts_by_number/" \
                   f"{account_number}" \

        url = self.construct_connects_url() + endpoint
        response = requests.get(url, auth=self.get_requests_auth())

        if response.status_code != 200:
            # Handle a bad query
            return None

        account = response.json()

        if not account:
            return None
        # if not data["_embedded"]["item"]:
        #     # Handle no results found
        #     return None

        # account = data["_embedded"]["item"][0]

        return account

    def get_from_embed_link(self, link):
        response = requests.get(link, auth=self.get_requests_auth())
        if response.status_code != 200:
            # Handle a bad query
            return None

        data = response.json()

        if not data["_embedded"]["item"]:
            # Handle no results found
            return None

        embed = data["_embedded"]["item"][0]

        return embed




    def get_loan_balance(self, account_number):
        account = self.find_account(account_number)
        if not account:
            return None
        return float(account["full_price"]) - float(account["total_paid"])


    def get_recent_keycode(self, account_number):
        account = self.find_account(account_number)
        if not account:
            return None

        activation = self.get_from_embed_link(account["_links"]["za:activations"]["href"])

        if not activation:
            return None



        return activation["keycode"]

    def format_keycode(self, keycode):
        return keycode.replace(' ', '').replace('', ' . ').lstrip(' . ')



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

        phone_number = flask.request.form.get("callerNumber", "")


        if not phone_number.startswith("+254"):
            xml = self.make_reject_payload()
            return self.emit_xml_response(xml)

        if status == "Completed":
            xml = self.make_reject_payload()
            return self.emit_xml_response(xml)


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
                xml = self.make_get_no_account_payload()
                balance = self.get_loan_balance(value)
                logger.info(f"balance is {balance}")
                if balance is not None:
                    logger.info("updating xml")
                    xml = self.make_get_balance_payload(balance)
                return self.emit_xml_response(xml)
            if digits == "2":
                xml = self.make_get_no_token_payload()
                keycode = self.get_recent_keycode(value)
                if keycode is not None:
                    formated_keycode = self.format_keycode(keycode)
                    xml = self.make_get_token_payload(formated_keycode)

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
