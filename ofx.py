#!/usr/bin/python
#
# A hacked together script for generating OFX files.
# 
# Author: Brett Hutley <brett@hutley.net>
import os, sys
import ledger
import random

random.seed()

def convert_to_ofx_date(dat):
    
    return "%d%02d%02d120000" % (dat.year, dat.month, dat.day)

class Xact:
    def __init__(self, dat, desc, amount):
        self.date = dat
        self.desc = desc
        self.amount = amount
        self.type = 'CREDIT'
        if self.amount < 0.0:
            self.type = 'DEBIT'

class Ofx:
    def __init__(self, base_ccy, account_id):
        self.base_ccy = base_ccy
        self.account_id = account_id
        self.from_date = ''
        self.to_date = ''
        self.xacts_by_date = {}
        self.tran_key = "%06d" % random.randint(1, 999999)
        self.tran_id = 0

    def add_xact(self, dat, desc, amount):
        dt = convert_to_ofx_date(dat)
        xact = Xact(dt, desc, amount)
        if dt < self.from_date or self.from_date == '':
            self.from_date = dt
        if dt > self.to_date or self.to_date == '':
            self.to_date = dt
        if not self.xacts_by_date.has_key(dt):
            self.xacts_by_date[dt] = []
        self.xacts_by_date[dt].append(xact)
        
    def __str__(self):
        xml = self._get_header()
        dates = self.xacts_by_date.keys()
        dates.sort()
        for dat in dates:
            for xact in self.xacts_by_date[dat]:
                xml += self._get_transaction_xml(xact)
        xml += self._get_footer_xml()
        return xml

    def _get_header(self):
        if self.from_date == '':
            raise Exception("No transactions provided")

        return "OFXHEADER:100\nDATA:OFXSGML\nVERSION:102\nSECURITY:NONE\nENCODING:USASCII\nCHARSET:1252\nCOMPRESSION:NONE\nOLDFILEUID:NONE\nNEWFILEUID:NONE\n\n<OFX>\n<CREDITCARDMSGSRSV1>\n<CCSTMTTRNRS>\n<TRNUID>1</TRNUID>\n<STATUS>\n<CODE>0</CODE>\n<SEVERITY>INFO</SEVERITY>\n</STATUS>\n<CCSTMTRS>\n<CURDEF>%s</CURDEF>\n<CCACCTFROM>\n<ACCTID>%s</ACCTID>\n</CCACCTFROM>\n<BANKTRANLIST>\n<DTSTART>%s</DTSTART>\n<DTEND>%s</DTEND>\n" % (self.base_ccy, self.account_id, self.from_date, self.to_date)

    def _get_transaction_xml(self, xact):
        self.tran_id += 1
        trid = "%s%03d" % (self.tran_key, self.tran_id)
        return "<STMTTRN>\n<TRNTYPE>%s</TRNTYPE>\n<DTPOSTED>%s</DTPOSTED>\n<TRNAMT>%.2f</TRNAMT>\n<FITID>%s</FITID>\n<NAME>%s</NAME>\n</STMTTRN>\n" % (xact.type, xact.date, xact.amount, trid, xact.desc)

    def _get_footer_xml(self):
        return "</BANKTRANLIST>\n</CCSTMTRS>\n</CCSTMTTRNRS>\n</CREDITCARDMSGSRSV1>\n</OFX>\n"

