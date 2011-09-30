#!/usr/bin/python
#
# A hacked together script for parsing jwiegley's Ledger files
# 
# Author: Brett Hutley <brett@hutley.net>
import sys
import datetime

class Split:
    def __init__(self, account, amount):
        self.account = account
        self.amount = amount

    def __str__(self):
        return "\t%s\t%.2f\n" % (self.account, self.amount)

class Xact:
    def __init__(self, date, desc):
        self.date = date
        self.desc = desc
        self.splits = []
        self.account_splits = {}

    def add_split(self, split):
        if self.account_splits.has_key(split.account):
            raise Exception("Can't have multiple splits with the same account ('%s') in the same transaction" % (split.account, ))

        self.splits.append(split)
        self.account_splits[split.account] = split

    def is_account_in_xact(self, account):
        return self.account_splits.has_key(account)

    def split_for_account(self, account):
        return self.account_splits[account]

    def __str__(self):
        str = "%d-%02d-%02d\t%s\n" % (self.date.year, self.date.month, self.date.day, self.desc)
        for split in self.splits:
            str += split.__str__()
        return str

def parse_xact(line):
    dt = line[0:10]
    desc = line[10:len(line)].strip()

    year, mon, day = dt.split('-')
    date = datetime.date(int(year), int(mon), int(day))
    return Xact(date, desc)

def load_ledger_file(filename):
    file = open(filename, 'r')

    WAITING_FOR_XACT = 0
    IN_XACT = 1

    state = WAITING_FOR_XACT

    xacts = []

    curr_xact = None

    linenum = 0
    for line in file:
        linenum += 1

        if line.startswith(';'):
            continue
        line = line.rstrip()

        if state == WAITING_FOR_XACT:
            if len(line) > 10:
                state = IN_XACT

                curr_xact = parse_xact(line)
                xacts.append(curr_xact)
        else:
            # in XACT
            if len(line) > 10:
                fields = line.split("\t")
                if len(fields) != 3:
                    print("Error in split at line: %s" % line)
                    exit(0)
                split = Split(fields[1], float(fields[2]))
                try:
                    curr_xact.add_split(split)
                except:
                    print("Caught exception adding split at line number %d" % (linenum, ))
                    exit(0)
            else:
                state = WAITING_FOR_XACT
    file.close()


    return xacts

