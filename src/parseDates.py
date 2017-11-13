import datetime
import dateutil.parser as parser
from lxml import etree as ET
import re

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)

parser.parser.parse = parse


def parseDates(dateString):
	if re.search(r'and', dateString):
		dateString = dateString.replace('and', '-')

	if re.search(r',|;', dateString):
		dates = re.split(r',|;', dateString)
		dateElement = ET.Element('dateSet')
		for date in dates:
			dateElement.append(parseDates(date.strip()))
	elif re.search(r'-', dateString):
		dateElement = convertDateRange(dateString.strip())
	else:
		dateElement = createDateElement('date', dateString.strip())


	return(dateElement)



def createDateElement(tag, dateString):
	dateElement = ET.Element(tag)

	if re.search(r'\d{4}s', dateString):
		decade = dateString[:-1]
		dateElement.set('notBefore', decade)
		dateElement.set('notAfter', decade[:-1] + "9")

	convertedDateString = convertDateString(dateString)

	value = convertedDateString[0]
	dateElement.text = value
	dateElement.set('standardDate', convertedDateString[1])

	if convertedDateString[2] == 'before':
		dateElement.set('notAfter', convertedDateString[1])
	elif convertedDateString[2] == 'after':
		dateElement.set('notBefore', convertedDateString[1])

	return(dateElement)


def convertDateString(dateString):
	testedDateString = testApproxValue(dateString)
	date = unicode(testedDateString[1])


	ddd = parser.parser().parse(date, None, fuzzy = True)

	if ddd.day:
		dstr = str(ddd.year)+'-'+str("%02d" % ddd.month)+'-'+str("%02d" % ddd.day)
	elif ddd.month:
		dstr =  str(ddd.year)+'-'+str("%02d" % ddd.month)
	elif ddd.year:
		dstr = str(ddd.year)
	else:
		print 'Unreadable date: ' + date
		newDateString = raw_input('Enter a new date as (before, after, etc) dd Month yyyy e.g. (after 01 January 2000):\n')
		print dateString, date, newDateString
		return(convertDateString(unicode(newDateString)))

	testedDateString[1] = dstr

	return(testedDateString)


def testApproxValue(dateString):
	justDateString = dateString
	approxString = ''

	approxStrings = re.search(r'(.*)(before|after|\?|s$)(.*)', dateString)

	if approxStrings:
		approxString = approxStrings.group(2)
		if approxStrings.group(1) != '':
			justDateString = approxStrings.group(1)
		else:
			justDateString = approxStrings.group(3)

	return([dateString, justDateString, approxString])


def convertDateRange(dateRange):
	rangeMatch = re.search(r'^(.*)-(.*)$', dateRange)

	dateElement = ET.Element('dateRange')

	fromDate = None

	if rangeMatch.group(1):
		fromDate = rangeMatch.group(1).strip()
		dateElement.append(createDateElement('fromDate', rangeMatch.group(1)))
	if rangeMatch.group(2):
		toDate = rangeMatch.group(2).strip()
		if toDate != '' and not re.match(r'\d', toDate) and fromDate:
			toDate = fromDate[0:4] + ' ' + toDate
			print toDate
		dateElement.append(createDateElement('toDate', toDate))

	return(dateElement)
