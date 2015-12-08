##
 # PayZen SOAP V5 Tool Box
 # Uses SUDS as SOAP backend
 #
 # @depend SUDS
 # @link https://fedorahosted.org/suds/
 #
 # @version 0.2
 # 
 ##

from suds.client import Client
from suds.sax.element import Element


import uuid
import hmac
import base64
from datetime import datetime
from hashlib import sha256 
import logging


class PayZenSOAPV5ToolBox:
  # PayZen platform data
  platform = {
            'wsdl'           : 'https://secure.payzen.eu/vads-ws/v5?wsdl', # URL of the PayZen SOAP V5 WSDL
	    'ns'             : 'http://v5.ws.vads.lyra.com/',              # Namespace of the service
	    'hns'            : 'http://v5.ws.vads.lyra.com/Header',        # Namespace ot the service header
  }

  # UUID V5 needs a valid UUID as reference
  UUIDBase = '1546058f-5a25-4334-85ae-e68f2a44bbaf'

  # Constructor, stores the PayZen user's account informations
  # 
  # @param shopId string, the account shop id as provided by Payzen
  # @param certTest string, certificate, test-version, as provided by PayZen
  # @param certProd string, certificate, production-version, as provided by PayZen
  # @param mode string ("TEST" or "PRODUCTION"), the PayZen mode to operate
  # @param logger logging.logger object, the logger to use. Will be created if not provided
  #
  def __init__(self, shopId, certTest, certProd, mode = 'TEST', logger = None):
    self.logger = logger or logging.getLogger()
    self.account = {
     'shopId': shopId,
     'cert': {
      'TEST': certTest,
      'PRODUCTION': certProd
     },
     'mode': mode
    } 

  # Utility method, build the SOAP headers
  #
  # @param timestamp string, the SOAP header timestamp
  #
  # @return dict of SUDS.Element defining the headers
  #
  def headers(self, timestamp):
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

  # Utility method, builds the authToken matching the
  # given requestId and timestamp
  #
  # @param requestId string, the request UUID
  # @param timestamp string, the request timestamp
  # @param format string, the format to use: 'request'
  # or 'response'
  #
  # @return dict of SUDS.SAX.Element defining the headers
  #
  def authToken(self, requestId, timestamp, format = 'request'):
    certificate = self.account['cert'][self.account['mode']]
    data = str(requestId) + timestamp if format == 'request' else timestamp + str(requestId)
    return base64.b64encode(hmac.new(certificate, data, sha256).digest())


  # Utility method, validates the response from PayZen
  #
  # @param answer SUDS answer
  #
  # @throw Exception if response is invalid
  #
  def validate(self, answer):
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


  # Main method, performs a createRequest payment
  #
  # @param amount string, the payment amount
  # @param currency string, the currency code (978 is for Euro)
  # @param cardNumber string, the credit card number
  # @param expiryMonth string, the month (MM) of the credit card expiry
  # @param expiryMonth string, the year (YYYY) of the credit card expiry
  # @param cardSecurityCode string, the security code of the credit card 
  # @param cardSecurityCode string, the scheme of the credit card (ie 'VISA')
  # @param orderId string, the identifier of the order related to the requested payment
  #
  # @return SUDS answer
  #
  def createPayment(self, amount, currency, cardNumber, expiryMonth, expiryYear, cardSecurityCode, scheme, orderId):
   self.logger.info("'createPayment' requested for order id {} (amount: {}, currency: {})".format(orderId, amount, currency))
   # Create a SUDS client of the PayZen platform
   client = Client(url = self.platform['wsdl'])

   # Each request needs a timestamp
   timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

   # SOAP headers construction and definition
   headers = self.headers(timestamp)
   client.set_options(soapheaders = headers)

   # Builds the payload
   ## commonRequest part
   commonRequest = {'submissionDate': timestamp}

   ## paymentRequest part
   paymentRequest = {'amount': amount, 'currency': currency}

   ## orderRequest part
   orderRequest = {'orderId': orderId}

   ## cardRequest part
   cardRequest = {
       'number'           : cardNumber
     , 'expiryMonth'      : expiryMonth 
     , 'expiryYear'       : expiryYear
     , 'cardSecurityCode' : cardSecurityCode 
     , 'scheme'           : scheme
   }

   # Performs the query
   answer = client.service.createPayment(
     commonRequest  = commonRequest,
     paymentRequest = paymentRequest,
     cardRequest    = cardRequest,
     orderRequest   = orderRequest
     )

   # Validates the answer
   self.validate(client.last_received())
   self.logger.info("'createPayment' response for order id {} is valid".format(orderId))

   # Returns the answer
   return answer
