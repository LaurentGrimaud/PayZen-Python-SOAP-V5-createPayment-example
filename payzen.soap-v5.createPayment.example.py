#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" PayZen SOAP V5 Python2 payment example """

from PayZenSOAPV5ToolBox import PayZenSOAPV5ToolBox
import logging


# Here we define the logger we wanna use
# Adapt this to reflect your needs
logging.basicConfig(filename="payment_soap.log", level=logging.INFO)
logger = logging.getLogger()

# Payment data
amount           = 1000                # payment amount, in cents
currency         = 978                 # 'EURO' currency code
cardNumber       = '4970100000000003'  # debit/credit card number
expiryMonth      = '11'                # debit/credit card month expiry (2 digits)
expiryYear       = '2016'              # debit/credit card year expiry (4 digits)
cardSecurityCode = '235'               # debit/credit card security code
scheme           = 'VISA'              # debit/credit card scheme

# Order data
orderId          = '12345678'          # 'your' order id

# Account data
shopId   = '[***CHANGE-ME***]'         # PayZen shop id
certTest = '[***CHANGE-ME***]'         # PayZen certificate for TEST mode
certProd = '[***CHANGE-ME***]'         # PayZen certificate for PRODUCTION mode
mode     = 'TEST'                      # the mode you wanna the payment to be in


# Initialisation of the PayZen Tool-Box
payzenTB = PayZenSOAPV5ToolBox(shopId, certTest, certProd, mode, logger)

# 'createPayent' request
try:
    result = payzenTB.createPayment(amount, currency, cardNumber, expiryMonth, expiryYear, cardSecurityCode, scheme, orderId)
    logger.info("Payzen response code was: " + str(result.commonResponse.responseCode))

    # Use the result
    if result.commonResponse.responseCode == 0:
        ### Here is the code for an accepted payment
        print 'Payment is done !'
        logger.info('Payment of order {} is done !'.format(orderId))
    else:
        ### Here is the code for a not accepted payment
        print "Payment is not authorised"
        logger.error("Payment not authorised for order " + orderId)
        print "PayZen responded with code " + str(result.commonResponse.responseCode)
        if result.commonResponse.responseCodeDetail:
            print "The additionnal given detail was: " + result.commonResponse.responseCodeDetail
            logger.info("The additionnal given detail was: " + result.commonResponse.responseCodeDetail)

except Exception as e:
    ### Here is the code for a error during process management
    msg = 'Something was wrong during payment process - An exception raised: ' + str(e)
    logger.error(msg)
    print msg
