package main

import (
//    "fmt"
    "sort"
    "strings"
)

type CountryTagger struct {
    Terms   map[string]string
}

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
//    fmt.Println(fmt.Sprintf("[%s] =   [%s]", strings.Join(words, ","), convertToKey(words)))
    
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
func NewCountryTagger(mongoUrl string) CountryTagger {
    ct := CountryTagger{}
    ct.Terms = make(map[string]string)
    
    ct.Terms[convertToKey([]string{"United", "States"})] = "US"
    ct.Terms[convertToKey([]string{"Afghanistan"})] = "AF"
    ct.Terms[convertToKey([]string{"Russian"})] = "RU"
    ct.Terms[convertToKey([]string{"Russia", "told"})] = "RU"
    
    return ct
}