import datetime as dt
import requests as req
import json
import numpy as np
import pandas as pd
from datetime import datetime
from config import *

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float

import sqlite3

from flask import Flask, jsonify

#################################################
# Reformat date from 6/30/2017 12:00 AM to 2017-06-30
#################################################

def reformat_date(str_date):
	return datetime.strptime(str_date, '%m/%d/%Y %I:%M %p').strftime('%Y-%m-%d')


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///sec13f.sqlite")
db = sqlite3.connect("sec13f.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the invoices and invoice_items tables
SecuritiesEx = Base.classes.securitiesex
ProcessedPositions = Base.classes.processed_positions
LatestPositions = Base.classes.latest_positions

# Create our session (link) from Python to the DB
session = Session(engine)

# Create a connection to the engine called conn
conn = engine.connect()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
	"""List all available api routes."""
	return (
		f"Avalable Routes:<br/>"
		f"/api/v1.0/dates - List available dates<br/>"

		f"/api/v1.0/positions/<date>"
		f"- List of holdings on file date<br/>"

		f"/api/v1.0/srr/<start_date>/<end_date>"
		f"- List of holdings on end_date with a simple rate of return<br/>"
	)

#################################################
@app.route("/api/v1.0/dates")
def getDates():
	"""Return a list of available dates"""
	# Query all countries from the Invoices table
	results1 = session.query(LatestPositions.currentreportdate).\
		group_by(LatestPositions.currentreportdate).all()

	results2 = session.query(ProcessedPositions.file_date).\
		group_by(ProcessedPositions.file_date).all()

	# Convert list of tuples into normal list
	dates_list = list(np.ravel(results1)) + list(np.ravel(results2))
	dates_list.sort()
	return jsonify(dates_list)

#################################################
# SELECT file_date, name, ticker, mval, cmval, shares, cshares,                  
#   case when pprice == 0 then 0                                                 
#        when shares == 0 then 0                                                 
#        else ((price-pprice)/(pprice*1.0))*100 end as srr, price, pprice
# FROM (                                                                         
#   SELECT file_date, name, ticker, SUM(mval) as mval, SUM(cmval) as cmval,      
#     SUM(shares) as shares, SUM(cshares) as cshares, MIN(price) as price,       
#     MIN(pprice) as pprice                                                      
#   FROM (                                                                       
#     SELECT p.file_date, p.name, s.ticker, CAST(p.mval AS NUMERIC) as mval,     
#       CAST(p.cmval AS NUMERIC) as cmval, CAST(p.shares AS NUMERIC) as shares,  
#       CAST(p.cshares AS NUMERIC) as cshares, CAST(p.price AS NUMERIC) as price,
#       CAST(p.prior_price AS NUMERIC) as pprice                                 
#     FROM processed_positions p                                                 
#     LEFT JOIN securitiesex s ON p.cusip = s.cusip                              
#     WHERE '2016-09-30' <= p.file_date AND p.file_date <= '2017-06-30'
#   ) x                                                                         
#   GROUP BY file_date, name, ticker                                             
#   UNION ALL                                                                    
                                                                               
#   SELECT lp.currentreportdate, lp.companyname, lp.ticker,                      
#     CAST(lp.marketvalue AS NUMERIC), CAST(lp.marketvaluechange AS NUMERIC),    
#     CAST(lp.sharesheld AS NUMERIC), CAST(lp.sharesheldchange AS NUMERIC),       
#     CAST(lp.price AS NUMERIC), 0
#   FROM latest_positions lp                                                     
#   WHERE '2016-09-30' <= lp.currentreportdate AND lp.currentreportdate <= '2017-06-30'
#   );

@app.route("/api/v1.0/srr/<start_date>/<end_date>")
def getSRR(start_date, end_date):
	## List of holdings on end_date with a simple rate of return
	sql = ('SELECT file_date, name, ticker, mval, cmval, shares, cshares,                   ' +
		'  case when pprice == 0 then 0                                                     ' +
		'       when shares == 0 then 0                                                     ' +
		'       else ((price-pprice)/(pprice*1.0))*100 end as srr, price, pprice            ' +
		'FROM (                                                                             ' +
		'  SELECT file_date, name, ticker, SUM(mval) as mval, SUM(cmval) as cmval,          ' +
		'    SUM(shares) as shares, SUM(cshares) as cshares, MIN(price) as price,           ' +
		'    MIN(pprice) as pprice                                                          ' +
		'  FROM (                                                                           ' +
		'    SELECT p.file_date, p.name, s.ticker, CAST(p.mval AS NUMERIC) as mval,         ' +
		'      CAST(p.cmval AS NUMERIC) as cmval, CAST(p.shares AS NUMERIC) as shares,      ' +
		'      CAST(p.cshares AS NUMERIC) as cshares, CAST(p.price AS NUMERIC) as price,    ' +
		'      CAST(p.prior_price AS NUMERIC) as pprice                                     ' +
		'    FROM processed_positions p                                                     ' +
		'    LEFT JOIN securitiesex s ON p.cusip = s.cusip                                  ' +
		'    WHERE "' + start_date + '" <= p.file_date AND p.file_date <= "' + end_date       +
		'  ") x                                                                             ' +
		'  GROUP BY file_date, name, ticker                                                 ' +
		'  UNION ALL                                                                        ' +
		'                                                                                   ' +
		'  SELECT lp.currentreportdate, lp.companyname, lp.ticker,                          ' +
		'    CAST(lp.marketvalue AS NUMERIC), CAST(lp.marketvaluechange AS NUMERIC),        ' +
		'    CAST(lp.sharesheld AS NUMERIC), CAST(lp.sharesheldchange AS NUMERIC),          ' +
		'    CAST(lp.price AS NUMERIC), 0                     ' +
		'  FROM latest_positions lp                                                         ' +
		'  WHERE ' + start_date + ' <= lp.currentreportdate AND lp.currentreportdate <=     ' + 
		end_date + ');')

	cursor = db.cursor()
	cursor.execute(sql)
	response = cursor.fetchall()
	positions = []
	for record in response:
		positions.append({
			"name": record[1],
			"ticker": record[2],
			"mval": record[3],
			"cmval": record[4],
			"shares": record[5],
			"cshares": record[6],
			"srr": record[7],
			"price": record[8],
			"pprice": record[9],
		})

	return jsonify(positions)


#################################################
@app.route("/api/v1.0/positions/<date>")
def getHoldings(date):
	## Get current holdings

	# Use `declarative_base` from SQLAlchemy to connect your class to your sqlite database
	Base2 = declarative_base()

	class Lastest_Positions(Base2):
		__tablename__ = 'latest_positions'
		id = Column(Integer, primary_key=True)
		querydate = Column(Text)
		filerid = Column(Text)
		cik = Column(Text)
		currentreportdate = Column(Text)
		priorreportdate = Column(Text)
		ownername = Column(Text)
		issueid = Column(Text)
		ticker = Column(Text)
		companyname = Column(Text)
		issuetitle = Column(Text)
		exchangeid = Column(Text)
		street1 = Column(Text)
		city = Column(Text)
		state = Column(Text)
		zipcode = Column(Text)
		country = Column(Text)
		phonecountrycode = Column(Text)
		phoneareacode = Column(Text)
		phonenumber = Column(Text)
		sharesout = Column(Text)
		sharesoutdate = Column(Text)
		price = Column(Text)
		pricedate = Column(Text)
		sharesheld = Column(Text)
		sharesheldchange = Column(Text)
		sharesheldpercentchange = Column(Text)
		marketvalue = Column(Text)
		marketvaluechange = Column(Text)
		portfoliopercent = Column(Text)
		sharesoutpercent = Column(Text)
		marketoperator = Column(Text)
		marketoperatorid = Column(Text)
		markettier = Column(Text)
		markettierid = Column(Text)

		def __repr__(self):
			return f"companyname={self.companyname}, ticker={self.ticker}, marketvalue={self.marketvalue}, sharesheld={self.sharesheld}"


	# Use `create_all` to create the latest_positions table in the database
	Base2.metadata.create_all(engine)

	# Use MetaData from SQLAlchemy to reflect the tables\n",
	metadata = MetaData(bind=engine)
	metadata.reflect()

	# Save the reference to the `latest_positions` table as a variable called `table`
	table = sqlalchemy.Table('latest_positions', metadata, autoload=True)

	query_url = "http://edgaronline.api.mashery.com/v2/ownerships/currentownerholdings?ciks=%s&appkey=%s" % (config["sec13f_brkcik"], config["sec13f_appkey"])
	sec_data = req.get(query_url).json()


	file_date = None
	securities = []
	for row in sec_data["result"]["rows"]:
		querydate = None
		filerid = None
		cik = None
		currentreportdate = None
		priorreportdate = None
		ownername = None
		issueid = None
		ticker = None
		companyname = None
		issuetitle = None
		exchangeid = None
		street1 = None
		city = None
		state = None
		zipcode = None
		country = None
		phonecountrycode = None
		phoneareacode = None
		phonenumber = None
		sharesout = None
		sharesoutdate = None
		price = None
		pricedate = None
		sharesheld = None
		sharesheldchange = None
		sharesheldpercentchange = None
		marketvalue = None
		marketvaluechange = None
		portfoliopercent = None
		sharesoutpercent = None
		marketoperator = None
		marketoperatorid = None
		markettier = None
		markettierid = None
		for value in row["values"]:
			if not(file_date) and value["field"] == "currentreportdate":
				file_date = reformat_date(value["value"])
			if value["field"] == "querydate":
				querydate = reformat_date(value["value"])
			if value["field"] == "filerid":
				filerid = value["value"]
			if value["field"] == "cik":
				cik = value["value"]
			if value["field"] == "currentreportdate":
				currentreportdate = reformat_date(value["value"])
			if value["field"] == "priorreportdate":
				 priorreportdate = reformat_date(value["value"])
			if value["field"] == "owername":
				ownername = value["value"]
			if value["field"] == "issueid":
				issueid = value["value"]
			if value["field"] == "ticker":
				ticker = value["value"]
			if value["field"] == "companyname":
				companyname = value["value"]
			if value["field"] == "issuetitle":
				issuetitle = value["value"]
			if value["field"] == "exchangeid":
				exchangeid = value["value"]
			if value["field"] == "street1":
				street1 = value["value"]
			if value["field"] == "city":
				city = value["value"]
			if value["field"] == "state":
				state = value["value"]
			if value["field"] == "zip":
				zipcode = value["value"]
			if value["field"] == "country":
				country = value["value"]
			if value["field"] == "phonecountrycode":
				phonecountrycode = value["value"]
			if value["field"] == "phoneareacode":
				phoneareacode = value["value"]
			if value["field"] == "phonenumber":
				phonenumber = value["value"]
			if value["field"] == "sharesout":
				sharesout = value["value"]
			if value["field"] == "sharesoutdate":
				sharesoutdate = value["value"]
			if value["field"] == "price":
				price = value["value"]
			if value["field"] == "pricedate":
				pricedate = reformat_date(value["value"])
			if value["field"] == "sharesheld":
				sharesheld = value["value"]
			if value["field"] == "sharesheldchange":
				sharesheldchange = value["value"]
			if value["field"] == "sharesheldpercentchange":
				sharesheldpercentchange = value["value"]
			if value["field"] == "marketvalue":
				marketvalue = value["value"]
			if value["field"] == "marketvaluechange":
				marketvaluechange = value["value"]
			if value["field"] == "portfoliopercent":
				portfoliopercent = value["value"]
			if value["field"] == "sharesoutpercent":
				sharesoutpercent = value["value"]
			if value["field"] == "marketoperator":
				marketoperator = value["value"]
			if value["field"] == "marketoperatorid":
				marketoperatorid = value["value"]
			if value["field"] == "markettier":
				markettier = value["value"]
			if value["field"] == "markettierid":
				markettierid = value["value"]
		securities.append({
			 "querydate" :               querydate
			,"filerid" :                 filerid
			,"cik" :                     cik
			,"currentreportdate" :       currentreportdate
			,"priorreportdate" :         priorreportdate
			,"ownername" :               ownername
			,"issueid" :                 issueid
			,"ticker" :                  ticker
			,"companyname" :             companyname
			,"issuetitle" :              issuetitle
			,"exchangeid" :              exchangeid
			,"street1" :                 street1
			,"city" :                    city
			,"state" :                   state
			,"zipcode" :                 zipcode
			,"country" :                 country
			,"phonecountrycode" :        phonecountrycode
			,"phoneareacode" :           phoneareacode
			,"phonenumber" :             phonenumber
			,"sharesout" :               sharesout
			,"sharesoutdate" :           sharesoutdate
			,"price" :                   price
			,"pricedate" :               pricedate
			,"sharesheld" :              sharesheld
			,"sharesheldchange" :        sharesheldchange
			,"sharesheldpercentchange" : sharesheldpercentchange
			,"marketvalue" :             marketvalue
			,"marketvaluechange" :       marketvaluechange
			,"portfoliopercent" :        portfoliopercent
			,"sharesoutpercent" :        sharesoutpercent
			,"marketoperator" :          marketoperator
			,"marketoperatorid" :        marketoperatorid
			,"markettier" :              markettier
			,"markettierid" :            markettierid
		})
	
	# check if holdings for the date exist
	results = session.query(
			LatestPositions.companyname,\
			LatestPositions.ticker,\
			sqlalchemy.sql.expression.literal_column("''").label("cusip"),\
			LatestPositions.marketvalue,\
			LatestPositions.marketvaluechange,\
			LatestPositions.sharesheld,\
			LatestPositions.sharesheldchange)\
		.group_by(LatestPositions.ticker)\
		.filter(LatestPositions.currentreportdate == file_date).all()

	if (len(results) == 0):

		# delete existing file date data from table
		sql = f"DELETE FROM latest_positions WHERE currentreportdate = '{file_date}'"
		conn.execute(sql)

		sql = f"DELETE FROM processed_positions WHERE file_date = '{file_date}'"
		conn.execute(sql)


		conn.execute(table.insert(), securities)

	if (file_date != date or len(results) == 0):
		results = session.query(
				ProcessedPositions.name,\
				sqlalchemy.sql.expression.literal_column("''").label("ticker"),\
				ProcessedPositions.cusip,\
				ProcessedPositions.mval,\
				ProcessedPositions.cmval,\
				ProcessedPositions.shares,\
				ProcessedPositions.cshares)\
			.group_by(ProcessedPositions.cusip)\
			.filter(ProcessedPositions.file_date == date).all()

	# Create a dictionary from the row data and append to a list of all_passengers
	positions = []
	for result in results:
		positions.append(result)

	return jsonify(positions)

#################################################
if __name__ == '__main__':
    app.run()
