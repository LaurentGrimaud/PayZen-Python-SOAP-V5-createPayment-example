# PayZen-Python-SOAP-V5-createPayment-example
Example of Python code using [PayZen](https://payzen.eu/) SOAP V5 webservices - createPayment request


## Introduction
The code presented here is a demonstration of the implementation of the SOAP v5 PayZen webservices, aimed to ease its use and learning.

This code only supports the `createPayment` request, but shows how a PayZen request and its answer can be handled.

The SOAP backend used here is SUDS, you may need to install it into your system. Please consult https://fedorahosted.org/suds/ for detailled install instructions


## Contents
This code is divided in two parts:
* payzen.soap-v5.createPayment.example.py, the main file, entry point of the process
* PayZenSOAPV5ToolBox.py, the core file, defining an utility class encapsulating all the PayZen logics


## The first use
1. Place the files on the same directory
2. In `payzen.soap-v5.createPayment.example.py`, replace the occurences of `[***CHANGE-ME***]` by the actual values of your PayZen account
3. Execute:
> python payzen.soap-v5.createPayment.example.py
to perform the createPayment request, in "TEST" mode.


## The next steps
You can follow the on-file documentation in `payzen.soap-v5.createPayment.example.php` to change the properties of the payment you want to initiate, like the amount or the informations of the customer payment card.

You can also change the `TEST` parameter to `PRODUCTION` to switch to _real_ payment mode, with *all* the caution this decision expects.


## Note
* The documentation used to write this code was [Guide technique d’implémentation des Web services V5, v1.4](https://payzen.eu/wp-content/uploads/2015/09/Guide_technique_d_implementation_Webservice_V5_v1.4_Payzen.pdf) (FRENCH)





