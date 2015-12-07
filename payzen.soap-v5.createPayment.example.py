from PayZenSOAPV5ToolBox import PayZenSOAPV5ToolBox
import logging


logging.basicConfig(level=logging.INFO)

#Payment data
amount           = 1000
currency         = 978
cardNumber       = '4970100000000003'
expiryMonth      = '11'
expiryYear       = '2016'
cardSecurityCode = '235'
scheme           = 'VISA'

#Order data
orderId  = '[***CHANGE-ME***]'

#Account data
shopId   = '[***CHANGE-ME***]'
certTest = '[***CHANGE-ME***]'
certProd = '[***CHANGE-ME***]'
mode     = 'TEST'

payzen = PayZenSOAPV5ToolBox(shopId, certTest, certProd, mode)

result = payzen.createPayment(amount, currency, cardNumber, expiryMonth, expiryYear, cardSecurityCode, scheme, orderId)
   

# Output the result.
if result.commonResponse.responseCode == 0:
  print 'Payment is done !'
else:
  print "Something was wrong during payment"
  print "PayZen responded with the code " + result.commonResponse.responseCode
  if result.commonResponse.responseCodeDetail:
    print "The additionnal given detail was: " + result.commonResponse.responseCodeDetail
