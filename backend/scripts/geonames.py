import sys, pprint, argh
from pymongo import MongoClient


## argv[1] = file to parse
## argv[2] = network address of MongoDB instance to output to

class Record(object):
    def __init__(self, line):
        fields = [x.strip() for x in line.split('\t')]
        
        # Fields from http://download.geonames.org/export/dump/
        # Dropping many unnecessary country and region codes, as well as
        # population, elevation, and some other stuff.
        self.name = fields[1]
        self.asciiName = fields[2]
        self.alternateNames = fields[3].split(',')
        # Feature classes and codes available at:
        #   http://www.geonames.org/export/codes.html
        self.featureClass = fields[6]
        self.featureCode = fields[7]
        self.countryCode = fields[8] # 2-letter ISO 3166

class CountryTagData(object):
    def __init__(self, record):
        self.CountryName = record.name
        self.CountryCode = record.countryCode
        
        self.Terms = {}
        
    def addTerm(self, term):
        self.Terms[term.lower()] = True

    def getTerms(self):
        return self.Terms.keys()

        
def main(dumpPath='allCountries.txt', mongoUrl='127.0.0.1'):
    # Mapping of all countries by country code.
    countries = {}
    # Feature codes that should be kept; all others will be discarded.
    validCodesList = [ \
        'ADM1', #'ADM2',     # FeatureClass = A
                            # FeatureClass = H
                            # FeatureClass = L
#        'PPL', 'PPLC', 'PPLS', 'PPLG'       # FeatureClass = P
    ]
    validCodes = {key: None for key in validCodesList}
    
    ###
    ## First pass identifies all independent political entities (countries) and records them
    ## in the `countries` dictionary.
    ###
    with open(dumpPath) as fp:
        for line in fp:
            record = Record(line)

            if record.featureClass == 'A' and record.featureCode == 'PCLI':
                countries[record.countryCode] = CountryTagData(record)

    ###
    ## Second pass 
    ###
    with open(dumpPath) as fp:
        for line in fp:
            record = Record(line)
            
            if record.countryCode in countries and record.featureCode in validCodes:
                country = countries[record.countryCode]
                
                # Add the name of the entity
                try:
                    record.name.decode('ascii')
                    country.addTerm(record.name)
                except UnicodeDecodeError:
                    pass
                
                for term in record.alternateNames:
                    try:
                        term.decode('ascii')
                        country.addTerm(term)
                    except UnicodeDecodeError:
                        pass
                        
                # Add alternative names of the entity
#                map(lambda x: country.addTerm(x), record.alternateNames)

    
    ### 
    ## Initialize a database connection and update / insert country data.
    ###
    dbClient = MongoClient('mongodb://%s/' % mongoUrl)
    collection = dbClient.newsflash.country_data
    
    for _, country in countries.iteritems():
        collection.update_one(
            filter={'countrycode': country.CountryCode},
            update={'$set': {
                'countryname': country.CountryName,
                'countrycode': country.CountryCode,
                'terms': country.getTerms(),
            }},
            upsert=True,
        )
                            
argh.dispatch_command(main)