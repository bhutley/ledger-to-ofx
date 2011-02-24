#!/usr/bin/python
#
# A hacked together script for reading ledger files and generating OFX
# files.
# 
# Author: Brett Hutley <brett@hutley.net>
import os, sys, datetime
import ledger
import ofx

def parse_date(dt):
    fields = dt.split('-')
    if len(fields) != 3 or len(fields[0]) != 4 or len(fields[1]) != 2 or len(fields[2]) != 2:
        raise(Exception("Date must be specified in the format YYYY-MM-DD"))

    return datetime.date(int(fields[0]), int(fields[1]), int(fields[2]))

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: %s <ledger.txt> <account_name> <account_id> <base_ccy> <from_date> [<to_date>]" % sys.argv[0])
        exit(0)

    filename = sys.argv[1]
    account_name = sys.argv[2]
    account_id = sys.argv[3]
    base_ccy = sys.argv[4]
    from_date = parse_date(sys.argv[5])

    to_date = None
    if len(sys.argv) > 6:
        to_date = parse_date(sys.argv[6])

    xacts = ledger.load_ledger_file(filename)
    ofx = ofx.Ofx(base_ccy, account_id)

    for xact in xacts:
        if xact.date >= from_date:
            if to_date is not None and to_date < xact.date:
                continue
            if xact.is_account_in_xact(account_name):
                split = xact.split_for_account(account_name)
                ofx.add_xact(xact.date, xact.desc, split.amount)

    print str(ofx)
