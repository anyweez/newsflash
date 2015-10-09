package main

import (
    "sort"
	"labix.org/v2/mgo/bson"
    "strings"
)

type CountryTagger struct {
    Terms   map[string]string
}

/**
 * Function to convert a series of words into a properly-formatted key. This needs
 * to be consistent for terms in the CountryTagData records and those that are read
 * in from articles; this function is the gold standard and is re-run on CTD data
 * at startup time, so this function can be freely changed.
 */
func convertToKey(words []string) string {
    // Stem all of the words.
    // Sort alphabetically.
    sort.Strings(words)
    // Join with '|'.
    return strings.ToLower(strings.Join(words, "|"))  
}

/**
 * Accepts an n-gram and returns a country label or an empty string if no 
 * country is known. How this matching occurs can evolve over time.
 */
func (ct *CountryTagger) LabelWords(words []string) (string, bool) {
    value, ok := ct.Terms[convertToKey(words)]
        
    if ok {
        return value, true
    } else {
        return "", false
    }
}

/**
 * Constructs a new CountryTagger instance.
 */
func NewCountryTagger() CountryTagger {
    session := MongoSession.Fork()
    defer session.Close()
    
    // Fetch CountryTagData from Mongo
    ctd := make([]CountryTagData, 0)
    session.DB("newsflash").C("country_tags").Find(bson.M{}).All(&ctd)
    
    ct := CountryTagger{}
    ct.Terms = make(map[string]string)
    
    for i := 0; i < len(ctd); i++ {
        current := ctd[i]
        // Iterate through all of the terms for this country and convert them
        // to properly-formatted keys.
        for j := 0; j < len(current.Terms); j++ {
            terms := strings.Fields(current.Terms[j])
            ct.Terms[convertToKey(terms)] = current.CountryCode 
        }
    }
    
    return ct
}