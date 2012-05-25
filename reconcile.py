#!/usr/bin/env python
# coding=utf-8
#
# reconcile an ofx file against pending payments
#

import ofxparse, sys
from flaskext.script import Command, Manager, Option
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.mail import Mail

from decimal import Decimal

from main import app
from models import User

#app = Flask(__name__)
#app.config.from_envvar('SETTINGS_FILE')
db = SQLAlchemy(app)
mail = Mail(app)

manager = Manager(app)

class Reconcile(Command):
  """
    Reconcile transactions in a .ofx file against the emfcamp db
  """
  option_list = (Option('-f', '--file', dest='filename', help="The .ofx file to load"),
                 Option('-d', '--doit', action='store_true', help="set this to actually change the db"),
                 Option('-q', '--quiet', action='store_true', help="don't be verbose"),
                )

  def run(self, filename, doit, quiet):
    self.doit = doit
    self.quiet = quiet
    data = ofxparse.OfxParser.parse(file(filename))
    for t in data.account.statement.transactions:
      # field mappings:
      # 
      # NAME 		: payee  <-- the ref we want
      # TRNTYPE 	: type   <-- other (?)
      # MEMO		: memo   <-- ?
      # FITID		: id     <-- also ?
      # TRNAMT		: amount <-- this is important...
      # DTPOSTED	: date   
      self.reconcile(t.payee, Decimal(t.amount), t)

  def reconcile(self, ref, amount, t):
    if t.type == 'other':
      user = User.query.filter_by(bankref=ref).all()
      if len(user) == 1:
        user = user[0]
        print u"user %s paid £%d with ref %s" % (user.name, amount, ref)
        #
        # so now we have the ref and an amount
        #
        unpaid = user.tickets.filter_by(paid=False).all()
        total = Decimal(0)
        for t in unpaid:
          total += Decimal(str(t.type.cost_pence / 100.0))

        if total == 0:
          # nothing owed, so an old payment...
          return
          
        if total != amount:
          print "tried to reconcile payment %s for %s, but amount paid (%d) didn't match amount owed (%d)" % (ref, user.name, amount, total)
        else:
          # all paid up.
          if self.doit:
            if not self.quiet:
              print "user %s paid for %d tickets" % (user.name, len(unpaid))
            # not sure why we have to do this, or why the object is already in a session.
            s = db.object_session(unpaid[0])            
            for t in unpaid:
              t.paid = True
            s.commit()

      elif len(user) == 0:
        if not self.quiet:
          print "unmatched ref %s paid %d" % (ref, amount)
      else:
        print "too many users"
    else:
      if not self.quiet:
        print t, t.type, t.payee

if __name__ == "__main__":
  manager.add_command('reconcile', Reconcile())
  manager.run()
