import flask
import xmltodict
from flask.views import MethodView
from api.util import jsonify, dejsonify, sanitize_arguments
import logging

from api.blueprints import VOICE_CALLBACK__REJECT_TEMPLATE, GET_DIGIT_TEMPLATE, make_template_file

logger = logging.getLogger("voice")
logging.basicConfig(level=logging.DEBUG)

class Voice(MethodView):
    """user endpoint."""

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


class GetDigit(MethodView):
    """user endpoint."""

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

        xml = self.make_reject_payload()

        return self.emit_xml_response(xml)


    


def create_blueprint(at_prefix, **kwargs):
    """webhook blueprint"""
    blueprint = flask.Blueprint("webhook", __name__)
    blueprint.add_url_rule("/webhook", view_func=Voice.as_view("webhook"))
    blueprint.add_url_rule("/get_digit_webhook", view_func=GetDigit.as_view("get_digit_webhook"))

    return blueprint
