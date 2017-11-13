from lxml import etree as ET
import xlrd
from datetime import date, datetime
import dateutil.parser as parsedate
import re
import eacEntity

defaultMap = ['status', 'recordId', 'name', 'authority', 'authorityUri', 'occupation',
 'birth', 'death', 'staff', 'trustee', 'amnh-other', 'dept', 'rel-id', 'years', 'exped']

def extractRecords(wkbkPath, sheetName, type):
	xlData = xlrd.open_workbook(wkbkPath)
	xlSkinnies = xlData.sheet_by_name(sheetName)

	totalRows = xlSkinnies.nrows - 1
	recordsWritten = 0

	for i in range(1, 10):
		skinnyRow = xlSkinnies.row(i)
		#print skinnyRow
		if skinnyRow[0].value == 0:
			values = parseRow(entityTypeskinnyRow)
			createSkinnyXML(values)
			recordsWritten = recordsWritten + 1

	print recordsWritten

def parseRow(entityType, row, valueMap = defaultMap):
	values['type'] = entityType
	for i in valueMap:
		values[values[i]] = row[i]

	['type', 'name', 'desc', 'exist']

	if values['staff'] != '':
		values['desc'].append('AMNH staff member')
		values['rel'].append('American Museum of Natural History')
	if values['trustee'] != '':
		values['desc'].append('AMNH trustee')
	if values['dept'] != '':
		values['desc'].append(values['dept'] + 'member')
	values['desc'] = v

		if values[5].value != '':
			biogHist.append(createElement('p', values[5].value))

		if values[8].value == True:
			biog = 'This person was employed by the American Museum of Natural History'
			relations.append(createRelation('American Museum of Natural History', 'Employed by AMNH', 'employedBy', values[13].value))

		if values[11].value != '':
			if biog:
				biog = biog[0:-1] + 'in ' + values[11].value + '.'
			else:
				biog = 'This person was employed by the American Museum of Natural History in ' + values[11].value + '.'
			relations.append(createRelation(values[11].value, 'Employed by AMNH in ' + values[11].value, 'employedBy', values[13].value))

		if values[9].value == True:
			if biog:
				biog = biog + 'This person also served as a trustee.'
			else:
				biog = 'This person also served as a trustee for the American Museum of Natural History.'
			relations.append(createRelation('American Museum of Natural History', 'Trustee of AMNH', '', values[13].value))

		if biog:
			biogHist.append(createElement('p', 'biog'))

		if values[10].value != '':
			biogHist.append(createElement('p', values[10].value))

	return(values)


def createSkinnyXML(values):
	skinnyXML = eacEntity(values[1])
	skinnyXML.addMaintenanceEvent('creation', 'machine', 'EAC-machine', 'Migrated from excel to xml')
	skinnyXML.addType(values['type'])
	skinnyXML.addName(values['name'])
	skinnyXML.addDescription(values['desc'])
	skinnyXML.addDates(values['exist'])




	if values[2].value != '' & values[3].value == 'lcnaf':
		names.append(createNameEntry(values[2].value, '100a', 'lcnaf'))
	elif values[2].value != '':
		names.append(createNameEntry(values[2].value, '100a'))

	#create control section with custom information
	base = createBaseXML(values[1].value)
	print values[1].value
	print values
	print base

	for value in values:
		if isinstance(value.value, float):
			value.value = str(int(value.value))
		if isinstance(value.value, basestring):
			value.value = value.value.strip(' .,')

	root = base.getroot()

	if type == 'corporate':
		root.append(createCDescription(values, type).getroot())
	elif type == 'person':
		root.append(createPDescription(values, type).getroot())
	else:
		print 'Require "corporate" or "person" as second argument'

	context = etree.iterwalk(root)
	for action, elem in context:
	    parent = elem.getparent()
	    if recursively_empty(elem):
	        parent.remove(elem)

	base.write('new/' + values[1].value + '.xml', encoding = 'utf-8', method = 'xml', xml_declaration=True, pretty_print = True)

def recursively_empty(xml_element):
   if xml_element.text:
       return False
   return all((recursively_empty(xe) for xe in xml_element.iterchildren()))
