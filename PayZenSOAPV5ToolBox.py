from suds.client import Client
from suds.sax.element import Element


import uuid
import hmac
import base64
from datetime import datetime
from hashlib import sha256 


class PayZenSOAPV5ToolBox:
  # PayZen platform data
  platform = {
            'wsdl'           : 'https://secure.payzen.eu/vads-ws/v5?wsdl',
	    'ns'             : 'http://v5.ws.vads.lyra.com/',
	    'hns'            : 'http://v5.ws.vads.lyra.com/Header',
  }
  UUIDBase = '1546058f-5a25-4334-85ae-e68f2a44bbaf'

  # PayZen account data
  def __init__(self, shopId, certTest, certProd, mode = 'TEST'):
    self.account = {
     'shopId': shopId,
     'cert': {
      'TEST': certTest,
      'PRODUCTION': certProd
     },
     'mode': mode
    } 

  #Header construct
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


  def authToken(self, requestId, timestamp, format = 'request'):
    certificate = self.account['cert'][self.account['mode']]
    data = str(requestId) + timestamp if format == 'request' else timestamp + str(requestId)
    return base64.b64encode(hmac.new(certificate, data, sha256).digest())


  def validate(self, answer):
    try:
     headers = answer.getChild("soap:Envelope").getChild("soap:Header")
     requestId = headers.getChild('requestId').getText()
     timestamp = headers.getChild('timestamp').getText()
     authToken = headers.getChild('authToken').getText()
    except:
     raise Exception('Incorrect SOPA header in response - Payment is not confirmed')
    if authToken != self.authToken(requestId, timestamp, 'response'):
      raise Exception('Received authToken incorrect - Payment is not confirmed')


  def createPayment(self, amount, currency, cardNumber, expiryMonth, expiryYear, cardSecurityCode, scheme, orderId):
  # Create a service proxy from the WSDL.
   client = Client(url = self.platform['wsdl'])
 #  print client

   timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

   headers = self.headers(timestamp)
   client.set_options(soapheaders = headers)

   # Build the payload
   ## commonRequest
   commonRequest = {'submissionDate': timestamp}

   ## paymentRequest
   paymentRequest = {'amount': amount, 'currency': currency}

   ## orderRequest
   orderRequest = {'orderId': orderId}

   ## cardRequest
   cardRequest = {
       'number'           : cardNumber
     , 'expiryMonth'      : expiryMonth 
     , 'expiryYear'       : expiryYear
     , 'cardSecurityCode' : cardSecurityCode 
     , 'scheme'           : scheme
   }

   # Perform the query.
   answer = client.service.createPayment(
     commonRequest  = commonRequest,
     paymentRequest = paymentRequest,
     cardRequest    = cardRequest,
     orderRequest   = orderRequest
     )

   # Validate the answer
   self.validate(client.last_received())

   #returns the answer
   return answer
