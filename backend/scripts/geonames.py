import sys, pprint

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

        
def main():
    # Mapping of all countries by country code.
    countries = {}
    validCodes = [ \
        'ADM1', 'ADM2', 'PCL', 'TERR', \    # FeatureClass = A
        'BNK', 'HBR', 'LKS',                # FeatureClass = H
        # FeatureClass = L
        'PPL', 'PPLC', 'PPLS', 'PPLG'       # FeatureClass = P
    ]
    
    ###
    ## First pass identifies all independent political entities (countries) and records them
    ## in the `countries` dictionary.
    ###
    with open(sys.argv[1]) as fp:
        for line in fp:
            record = Record(line)

            if record.featureClass == 'A' and record.featureCode == 'PCLI':
                countries[record.countryCode] = CountryTagData(record)

    ###
    ## Second pass 
    ###
    with open(sys.argv[1]) as fp:
        for line in fp:
            record = Record(line)
            
            if record.countryCode in countries and record.featureCode in validCodes:
                country = countries[record.countryCode]
                
                # Add the name of the entity
                country.addTerm(record.name)
                # Add alternative names of the entity
                map(lambda x: country.addTerm(x), record.alternateNames)

    for _, country in countries.iteritems():
        print "%s:\n%s" % (country.CountryName, country.getTerms())
                
if __name__ == '__main__':
    main()