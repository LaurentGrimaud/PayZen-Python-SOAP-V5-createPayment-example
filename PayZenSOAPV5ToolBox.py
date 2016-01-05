#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PayZen SOAP V5 Python2 Tool Box

Depends:
SUDS 0.4 https://fedorahosted.org/suds/
"""

from suds.client import Client
from suds.sax.element import Element

import uuid
import hmac
import base64
from datetime import datetime
from hashlib import sha256
import logging


class PayZenSOAPV5ToolBox:
    """ PayZen SOAP V5 Python2 toolbox class """

    # PayZen platform data
    platform = {
        'wsdl': 'https://secure.payzen.eu/vads-ws/v5?wsdl',  # URL of the PayZen SOAP V5 WSDL
        'ns': 'http://v5.ws.vads.lyra.com/',  # Namespace of the service
        'hns': 'http://v5.ws.vads.lyra.com/Header',  # Namespace ot the service header
    }

    # UUID V5 needs a valid UUID as reference
    UUIDBase = '1546058f-5a25-4334-85ae-e68f2a44bbaf'

    def __init__(self, shopId, certTest, certProd, mode='TEST', logger=None):
        """ Constructor, stores the PayZen user's account informations.

        Keyword arguments:
        shopId -- the account shop id as provided by Payzen
        certTest -- certificate, test-version, as provided by PayZen
        certProd -- certificate, production-version, as provided by PayZen
        mode -- ("TEST" or "PRODUCTION"), the PayZen mode to operate
        logger -- logging.logger object, the logger to use. Will be created if not provided
        """
        self.logger = logger or logging.getLogger()
        self.account = {
            'shopId': shopId,
            'cert': {
                'TEST': certTest,
                'PRODUCTION': certProd
            },
            'mode': mode
        }


    def headers(self, timestamp):
        """ Utility method, build the SOAP headers

        Keyword arguments:
        timestamp ---, the SOAP header timestamp

        Returns:
        dict of SUDS.Element defining the headers
        """
        # Mandatory header data
        requestId = str(uuid.uuid5(uuid.UUID(self.UUIDBase), timestamp))
        authToken = self.authToken(requestId, timestamp, 'request')

        hns = ('hns', self.platform['hns'])
        headers = (
            Element('shopId', ns=hns).setText(self.account['shopId']),
            Element('mode', ns=hns).setText(self.account['mode']),
            Element('requestId', ns=hns).setText(requestId),
            Element('timestamp', ns=hns).setText(timestamp),
            Element('authToken', ns=hns).setText(authToken)
        )
        return headers


    def authToken(self, requestId, timestamp, format='request'):
        """ Utility method, builds the authToken matching the given requestId and timestamp

        Keyword arguments:
        requestId -- the request UUID
        timestamp -- the request timestamp
        format -- the format to use: 'request' or 'response'

        Returns
        dict of SUDS.SAX.Element defining the headers
        """
        certificate = self.account['cert'][self.account['mode']]
        data = str(requestId) + timestamp if format == 'request' else timestamp + str(requestId)
        return base64.b64encode(hmac.new(certificate, data, sha256).digest())


    def validate(self, answer):
        """ Utility method, validates the response from PayZen

        Keyword arguments:
        answer -- SUDS answer

        Throws:
        Exception if response is invalid
        """
        try:
            headers = answer.getChild("soap:Envelope").getChild("soap:Header")
            requestId = headers.getChild('requestId').getText()
            timestamp = headers.getChild('timestamp').getText()
            authToken = headers.getChild('authToken').getText()
        except:
            raise Exception('Incorrect SOAP header in response - Payment is not confirmed')
        if authToken != self.authToken(requestId, timestamp, 'response'):
            raise Exception('Received authToken incorrect - Payment is not confirmed')
        self.logger.debug('auth token {} for request id {} is valid'.format(authToken, requestId))



    def createPayment(self, amount, currency, cardNumber, expiryMonth, expiryYear, cardSecurityCode, scheme, orderId):
        """ Main method, performs a createRequest payment

        Keyword arguments:
        amount -- the payment amount
        currency -- the currency code (978 is for Euro)
        cardNumber -- the credit card number
        expiryMonth -- the month (MM) of the credit card expiry
        expiryYear -- the year (YYYY) of the credit card expiry
        cardSecurityCode -- the security code of the credit card
        scheme -- the scheme of the credit card (ie 'VISA')
        orderId -- the identifier of the order related to the requested payment

        Returns:
        SUDS answer
        """
        self.logger.info("'createPayment' requested for order id {} (amount: {}, currency: {})".format(orderId, amount, currency))
        # Create a SUDS client of the PayZen platform
        client = Client(url=self.platform['wsdl'])

        # Each request needs a timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # SOAP headers construction and definition
        headers = self.headers(timestamp)
        client.set_options(soapheaders=headers)

        # Builds the payload
        ## commonRequest part
        commonRequest = {'submissionDate': timestamp}

        ## paymentRequest part
        paymentRequest = {'amount': amount, 'currency': currency}

        ## orderRequest part
        orderRequest = {'orderId': orderId}

        ## cardRequest part
        cardRequest = {
            'number': cardNumber
            , 'expiryMonth': expiryMonth
            , 'expiryYear': expiryYear
            , 'cardSecurityCode': cardSecurityCode
           , 'scheme': scheme
        }

        # Performs the query
        answer = client.service.createPayment(
            commonRequest=commonRequest,
            paymentRequest=paymentRequest,
            cardRequest=cardRequest,
            orderRequest=orderRequest
        )

        # Validates the answer
        self.validate(client.last_received())
        self.logger.info("'createPayment' response for order id {} is valid".format(orderId))

        # Returns the answer
        return answer
