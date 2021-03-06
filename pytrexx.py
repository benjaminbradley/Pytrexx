#!/usr/bin/env python3
__author__ = 'Dennis.Gyor'

from bittrex import Bittrex
import datetime
import click
from forex_python.bitcoin import BtcConverter
from tabulate import tabulate
import logging
from configparser import ConfigParser
from termcolor import colored, cprint

#Datetimestamp
dts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#parser object for creating the config file
config = ConfigParser()

#Read in config file entries and create vars
config.read('APIkey.ini')
key = config.get('API keys', 'key')
secret = config.get('API keys', 'secret')

#Bittrex API key object
# my_bittrex = Bittrex(secret, 'few') <-- for testing invalid API calls
my_bittrex = Bittrex(key, secret)

#create the command line group
@click.group()
@click.version_option('1.0.0')
@click.pass_context

#The top level cli command
def cli(self):
    """******************Pytrexx******************\n
\n
    Bittrex account and trading bot command line utility.\n

    Features:\n
      Fiat to BTC Converter\n
      Bittrex markets (Execute manual trades)\n
      Bittrex account (Query account information)\n
      Bittrex public (Retrieve exchange information)\n
      COMING SOON: Bittrex trading bot (automated trading)\n
    """

#convert command code block START
@cli.command('convert', help='<currency> type and <amount> to convert.')
#arguments for convert
@click.argument('currency', nargs=1, type=str)
@click.argument('amount', nargs=1, type=float)

#converter command method
def convert(currency, amount):

  # create a new converter object with standardized date
  b = BtcConverter()
  x = b.get_latest_price(currency)

  cprint('Powered by Coindesk | https://www.coindesk.com/price/', 'green')
  print("[" + str(dts) + "]" + "  " + currency.upper() + " for 1.0 Bitcoin (BTC) is " + str(x))

  # convert to BTC
  conversion_amount = b.convert_to_btc(amount, currency.upper())
  print("[{}]  Converting {} to BTC: {} {} is currently worth {} BTC!".format(str(dts), currency.upper(), "%0.2f" %(amount), currency.upper(), conversion_amount))
#convert command code block END

###ACCOUNT API CALLS###

#accountbalances command code block START
@cli.command('accountbalances', help='Get a balance of all of your coins on Bittrex')

#Used to retrieve the balance from your account for all currencies.
def accountbalances():
  try:
    t = my_bittrex.get_balances()
    table = tabulate(t['result'], headers="keys", tablefmt="grid", floatfmt=".8f")
    print(table)
  except TypeError as e:
    if t['message'] ==  'INVALID_SIGNATURE':
      print("Invalid Credentials. Check your API keys.")
    elif t['message'] ==  'INVALID_CURRENCY':
      print("Invalid Currency specified. Check your symbol.")
    else:
      print("Unknown error.")
  except:
    print(e)
#accountbalances command code block END

#accountbalance command code block START
@cli.command('accountbalance', help='Check your Bittrex account balance')
@click.argument('cryptocurrency', nargs=1, type=str)

#Used to retrieve the balance from your account for a specific currency.
def accountbalance(cryptocurrency):
  # print(type(my_bittrex)) <-- for debugging
  try:
    t = my_bittrex.get_balance(cryptocurrency)
    table = tabulate([t['result']], headers="keys", tablefmt="grid", floatfmt=".8f")
    print(table)
  except TypeError as e:
    if t['message'] ==  'INVALID_SIGNATURE':
      print("Invalid Credentials. Check your API keys.")
    elif t['message'] ==  'INVALID_CURRENCY':
      print("Invalid Currency specified. Check your symbol.")
    else:
      print("Unknown error.")
  except:
    print(e)

#accountbalance command code block END

#order command code block START
@cli.command('order', help='Check a Bittrex order')
@click.argument('id')

def order(id):
  # import pdb;pdb.set_trace()
  print(my_bittrex.get_order(id))
#order command code block END

#orderhistory command code block START
@cli.command('orders', help='Check your Bittrex order history')
@click.option('--cp')

def orders(cp):
  # import pdb;pdb.set_trace()
  t = my_bittrex.get_order_history(cp)
  table = tabulate(t['result'], headers="keys", tablefmt="grid", floatfmt=".8f")
  print(table)
#orderhistory command code block END

#deposit history command code block START
@cli.command('deposits', help='Check your Bittrex deposit history Options: currency, number of deposits ')
@click.option("--c")
@click.option("--n", type=int)

def deposits(c, n):
  if n != None:
    print(tabulate(my_bittrex.get_deposit_history(c)["result"][:n], headers="keys", tablefmt="grid"))
  else:
    print(tabulate(my_bittrex.get_deposit_history(c)["result"], headers="keys", tablefmt="grid"))
#deposit history command code block END

#withdrawal history command code block START
@cli.command('withdrawals', help='Check your Bittrex withdrawal history')
@click.option("--c")

def withdrawals(c):
  print(tabulate([my_bittrex.get_withdrawal_history(c)["result"]], headers="keys", tablefmt="grid"))
#withdrawal history command code block END

###MARKET API CALLS###

#buy command code block START
@cli.command('buy', help='Set buy limit order <currency pair> <quantity> <rate>')
@click.argument('cp', type=str)
@click.argument('quantity', type=float)
@click.argument('rate', type=float)

#Limit buy method
def buy(cp, quantity, rate):
  if click.confirm('Are you sure you want to make this buy limit order?', abort=True):
    print(my_bittrex.buy_limit(cp, quantity, rate))
#buy command code block END

#sell command code block START
@cli.command('sell', help='Set buy limit order <currency pair> <quantity> <rate>')
@click.argument('cp', type=str)
@click.argument('quantity', type=float)
@click.argument('rate', type=float)

#Limit sell method
def sell(cp, quantity, rate):
  if click.confirm('Are you sure you want to make this sell limit order?', abort=True):
    print(my_bittrex.sell_limit(cp, quantity, rate))
#sell command code block END

#cancel command code block START
@cli.command('cancel', help='Cancel an existing buy/sell limit order')
@click.argument('id', type=str)

def cancel(cp, quantity, rate):
  print(my_bittrex.cancel(id))
#cancel command code block END

###PUBLIC API CALLS###

#currencies command code block START
@cli.command('currencies', help='List all supported currencies on Bittrex')

#GET a list of all currencies supported on the Bittrex platform
def currencies():
  print(tabulate(my_bittrex.get_currencies()['result'], headers="keys", tablefmt="grid"))
#currencies command code block END

if __name__ == '__main__':
    cli()
