from lxml import etree as ET
from lxml import objectify
from datetime import date, datetime
import dateutil.parser as parsedate
import re
from parseDates import parseDates, createDateElement

ns = {'eac':'urn:isbn:1-931666-33-4',
        'xlink': 'http://www.w3.org/1999/xlink',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

parser = ET.XMLParser(remove_blank_text=True)
xmlFile = 'skinnyControl.xml'



class eacEntity():

    def __init__(self, recordID):
        self.tree = ET.parse(xmlFile, parser)
    	self.tree.find('.//{%s}recordID' % ns['eac']).text = recordID
        self.tree

    def createElement(self, tag, value = '', attrib = '', attribValue = False):
        element = ET.Element(tag)
        element.text = unicode(value)
        if attribValue:
            element.set(attrib, attribValue)
        return(element)


    def addMaintenanceEvent(self, eventType, agentType, agent, description):
        mHistory = self.tree.find('.//{%s}maintenanceHistory' % ns['eac'])
        mEvent = ET.SubElement(mHistory, 'maintenenanceEvent')
        mEvent.append(self.createElement('eventType', eventType))
        mEvent.append(self.createElement('eventDateTime', 'standardDate', date.today().strftime('%Y %B %d')))
        mEvent.append(self.createElement('agentType', agentType))
        mEvent.append(self.createElement('agent', agent))
        mEvent.append(self.createElement('eventDescription', description))

    	return("added " + eventType)

    def addType(self, entityType):
        self.find('./cpfDescription/identity/entityType').text = entityType

        return("added type")

    def addName(name, localType, authority = ''):
        names = self.find('./cpfDescription./identity')
    	nameEntry = ET.Element('nameEntry')
    	nameEntry.append(self.createElement('part', name, 'localType', localType))
    	if authority != '':
    		nameEntry.append(self.createElement('authorizedForm', authority))
    	return("added name")

    def addDescription(self, desc):
        self.find('./cpfDescription/description/biogHist').text = desc

    def addExistDates(self, startDate, endDate):
        self.find('./cpfDescription/description/existDates')

    def saveXML(directory):
        try:
            if directory[-1] == "/":
                self.write(directory + self.tree.find('.//{%s}recordID' % ns['eac']).text + '.xml',
                encoding = 'utf-8', method = 'xml', xml_declaration=True, pretty_print = True)
        except:
            return("damn it")
