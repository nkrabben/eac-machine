from lxml import etree as ET
import xlrd
from datetime import date, datetime
import dateutil.parser as parsedate
import re
from parseDates import parseDates, createDateElement


namespaces = {'ns':'isbn:1-931666-33-4', 'xlink': 'http://www.w3.org/1999/xlink',  'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
eacNS = '{urn:isbn:1-931666-33-4}'
xlink = '{http://www.w3.org/1999/xlink}'
parser = ET.XMLParser(remove_blank_text=True)

def parse(self, timestr, default=None,
          ignoretz=False, tzinfos=None,
          **kwargs):
    return self._parse(timestr, **kwargs)

parsedate.parser.parse = parse


def extractRecords(wkbkPath, sheetName, type):
	xlData = xlrd.open_workbook(wkbkPath)
	xlSkinnies = xlData.sheet_by_name(sheetName)

	totalRows = xlSkinnies.nrows - 1
	recordsWritten = 0

	for i in range(1, totalRows):
		#print i
		skinnyRow = xlSkinnies.row(i)
		#print skinnyRow
		createSkinnyXML(skinnyRow, type)
		recordsWritten = recordsWritten + 1

	print recordsWritten

def createSkinnyXML(values, type):
	#create control section with custom information
	base = createBaseXML(values[1].value)
	print values[1].value

	for value in values:
		if isinstance(value.value, float):
			value.value = str(int(value.value))
		if isinstance(value.value, basestring):
			value.value = value.value.strip(' .,')

	root = base.getroot()

	'''
	if values[4] != '':
		entry = None
		if values[3].value == 'lcnaf':
			entry = "Library of Congress Name Authority File"
		elif values[3].value == 'viaf':
			entry = "Virtual International Authority File"
		if entry:
			control = root.find('./' + eacNS + 'control')
			sources = ET.Element('sources')
			source = ET.SubElement(sources, 'source')
			source.set(xlink + 'href', values[4].value)
			source.append(createElement("sourceEntry", entry))
			control.append(sources)



	if values[14].value != '':
		sources = root.find('.//' + eacNS + 'sources')
		print sources
		sourceEntries = values[14].value.split(';')
		if not sourceEntries:
			sourceEntries = [values[14].value]
		for sourceEntry in sourceEntries:
			source = ET.Element('source')
			source.append(createElement("sourceEntry", sourceEntry))
			sources.append(source)

	if values[15].value != '':
		sources = root.find('.//' + eacNS + 'sources')
		print sources
		sourceEntries = values[15].value.split(';')
		if not sourceEntries:
			sourceEntries = [values[15].value]
		for sourceEntry in sourceEntries:
			source = ET.Element('source')
			source.append(createElement("sourceEntry", sourceEntry))
			sources.append(source)
	'''



	if type == 'corporateBody':
		root.append(createCDescription(values, type).getroot())
	elif type == 'person':
		root.append(createPDescription(values, type).getroot())
	else:
		print 'Require "corporate" or "person" as second argument'

	context = ET.iterwalk(root)
	for action, elem in context:
	    parent = elem.getparent()
	    if recursively_empty(elem):
	        parent.remove(elem)

	base.write('new/' + values[1].value + '.xml', encoding = 'utf-8', method = 'xml', xml_declaration=True, pretty_print = True)


def recursively_empty(xml_element):
   if xml_element.text:
       return False
   return all((recursively_empty(xe) for xe in xml_element.iterchildren()))


def createBaseXML(recordID):
	base = ET.parse('templates/skinnyControl.xml', parser)

	#add recordID. identify element via xpath?
	base.find('.//' + eacNS + 'recordId').text = recordID

	#maintenanceHistory = base.find('maintenanceHistory')
	maintenanceEventTime = base.find('.//' + eacNS + 'maintenanceHistory//' + eacNS + 'eventDateTime')
	maintenanceEventTime.text = date.today().strftime('%Y %B %d')
	maintenanceEventTime.set('standardDateTime', date.today().isoformat())

	maintenanceEventTime = base.find('.//' + eacNS + 'maintenanceHistory//' + eacNS + 'agent')
	maintenanceEventTime.text = 'Python'

	maintenanceEventTime = base.find('.//' + eacNS + 'maintenanceHistory//' + eacNS + 'agentType')
	maintenanceEventTime.text = 'machine'

	return(base)


def createMaintenanceEvent(agent, event):
	#create base element
	maintenance = ET.Element('maintenanceEvent')

	#add custom event description
	ET.SubElement(maintenance, 'event').text = event

	#add date and standard date
	time = ET.SubElement(maintenance, 'eventDateTime')
	time.text = date.today().strftime('%Y %B %d')
	time.set('standardDate', date.today().isoformat())

	#add agents
	ET.SubElement(maintenance, 'agentType').text = 'computer'
	ET.SubElement(maintenance, 'agent').text = agent

   	return(maintenance)


def createCDescription(values, type):
	cpfDescription = ET.parse('templates/skinnyDescription.xml', parser)

	#identity
	cpfDescription.find('./identity/entityType').text = type
	names = cpfDescription.find('./identity')

	if values[2].value != '':
		names.append(createCNameEntry(values[2].value))

	if values[3].value != '':
		names.append(createCNameEntry(values[3].value, 'amnhopac'))

	#description
	description = cpfDescription.find('./description')

	#dates
	existDates = description.find('./existDates')

	if values[7].value != '' and re.match(r'\d', values[7].value[0]):
		date = values[6].value + '-' + values[7].value
	elif values[7].value != '' and re.match(r'[A-Za-z]', values[7].value[0]):
		date = values[6].value + ' ' + values[7].value
	else:
		date = values[6].value + values[7].value

	if date != '':
		existDates.append(parseDates(date))

	if values[8].value:
		existDates.append(createElement('descriptiveNote', values[8].value))

	if values[9].value:
		placeEntries = values[9].value.split(';')

		if len(placeEntries) == 1:
			place = ET.Element('place')
			place.append(createElement("placeEntry", values[9].value))
			existDates.addnext(place)

		else:
			places = ET.Element('places')
			for placeEntry in placeEntries:
				place = ET.Element('place')
				place.append(createElement("placeEntry", placeEntry))
				places.append(place)
			existDates.addnext(places)

	biogHist = description.find('.//biogHist')

	if values[10].value:
		biogHist.append(createElement('abstract', values[10].value))

	if values[11].value:
		biogHist.append(createElement('p', 'Personnel: ' + values[11].value))

	if values[12].value:
		biogHist.append(createElement('p', 'Department: ' + values[12].value))

	if values[13].value:
		biogHist.append(createElement('p', 'Sponsors: ' + values[13].value))

	if values[14].value:
		biogHist.append(createElement('p', 'Other: ' + values[14].value))

	if values[16].value:
		biogHist.append(createElement('p', 'Sources: ' + values[16].value))

	return(cpfDescription)


def createPDescription(values, type):
	cpfDescription = ET.parse('templates/skinnyDescription.xml', parser)

	#identity
	cpfDescription.find('./identity/entityType').text = type
	names = cpfDescription.find('./identity')

	if values[2].value != '':
	 	name = values[2].value
		if values[3].value != u'' or values[3].value != "FALSE":
			authorizedForm = values[3].value
		else:
			authorizedForm = None
		'''
		if authorizedForm and values[4].value != u'':
			uri = values[4].value
		else:
			uri = None
		'''

		names.append(createNameEntry(name, authorizedForm))


	#description
	description = cpfDescription.find('./description')

	#dates
	existDates = description.find('./existDates/dateRange')
	#print(existDates)
	if values[6].value and values[7].value:
		existDates.append(createDateElement('fromDate', values[6].value))
		existDates.append(createDateElement('toDate', values[7].value))

	#bioghist
	biogHist = description.find('.//biogHist')
	relations = cpfDescription.find('./relations')

	biog = None

	if values[5].value != '':
		biogHist.append(createElement('p', values[5].value))

	staff_biog = None

	if values[10].value != '':
		biogHist.append(createElement('p', values[10].value))
		relations.append(createRelation('American Museum of Natural History', 'amnhc_0000001', values[13].value))

	if values[8].value == True:
		staff_biog = 'Worked at the American Museum of Natural History.'

	if values[11].value != '':
		staff_biog = 'Worked at the American Museum of Natural History in ' + values[11].value + '.'
		if values[12].value != '':
			xlink = values[12].value
		else:
			xlink = ''
		relations.append(createRelation(values[11].value, xlink, values[13].value))

	if staff_biog:
		biogHist.append(createElement('p', staff_biog))

	if values[9].value == True:
		trustee_biog = 'Trustee, American Museum of Natural History.'
		relations.append(createRelation('American Museum of Natural History', 'amnhc_0000001', values[13].value))
		biogHist.append(createElement('p', trustee_biog))

	return(cpfDescription)


def createElement(tag, value = '', attrib = '', attribValue = False):
	element = ET.Element(tag)
	element.text = unicode(value)
	if attribValue:
		element.set(attrib, attribValue)
	return(element)


def createNameEntry(name, authority = None):
	nameEntry = ET.Element('nameEntry')
	name_parts = re.search(r'(\w+),\s([\w\s\.]+)(\([\w\s\.]+\))?(,\s([-\d\?]+))?', name)
	if name_parts:
		if name_parts.group(1):
			nameEntry.append(createElement('part', name_parts.group(1), 'localType', 'surname'))
		if name_parts.group(2):
			nameEntry.append(createElement('part', name_parts.group(2).strip(' '), 'localType', 'forename'))
		if name_parts.group(3):
			nameEntry.append(createElement('part', name_parts.group(3), 'localType', 'nameExpansion'))
		if name_parts.group(5):
			nameEntry.append(createElement('part', name_parts.group(5), 'localType', 'date'))
	else:
		nameEntry.append(createElement('part', name, 'localType', 'name'))
	if authority:
		nameEntry.append(createElement('authorizedForm', authority))

	return(nameEntry)

def createCNameEntry(name, authority = None):
	nameEntry = ET.Element('nameEntry')
	nameEntry.append(createElement('part', name, 'localType', 'corporateName'))
	if authority:
		nameEntry.append(createElement('authorizedForm', authority))

	return(nameEntry)


def createRelation(entity, xlink_value = '', date = '', desc = ''):
	relation = ET.Element('cpfRelation')
	relation.set('cpfRelationType', 'identity')

	if xlink_value != '':
		relation.set(xlink + 'href', xlink_value)

	ET.SubElement(relation, 'relationEntry').text = entity
	if date != '':
		relation.append(parseDates(date))

	return(relation)

#TODO unicode
#TODO relationship URIs
