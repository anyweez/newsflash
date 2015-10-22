package main

import (
    "bufio"
    "compress/gzip"
    "flag"
    "fmt"
    "log"
    "os"
    newsflash "newsflash/shared"
    mgo "gopkg.in/mgo.v2"
    "strings"
)

var FreebasePath = flag.String("freebase", "", "The path to the gzipped Freebase dump.")
var ParallelCount = flag.Int("parallel", 2, "The number of lines that should be processed in parallel per stage.")
//var mongoUrl = flag.String("mongo", "localhost:27017", "The network location of the MongoDB doc store.")

type SimpleNameRequest struct {
    Country string
    Target  string
    Why     string
}

/**
 * Opens a gzipped file at the specified location and returns a
 * buffered reader. Freebase files are usually quite large (~30 GB)
 * compressed so a buffered reader is necessary to do anything of
 * of value.
 */
func OpenFreebaseDump(path string) (*bufio.Reader, error, func()) {
    // Open the gzipped Freebase dump.
    fi, err := os.Open(path)
    if err != nil {
        return nil, err, func (){}
    }
    
    zipped, err := gzip.NewReader(fi)
    if err != nil {
        return nil, err, func (){}
    }
    
    return bufio.NewReader(zipped), nil, func () {
        fi.Close()
        zipped.Close()
    }
}

/**
 * Removes formatting cruft from a single fragment of a line (for example,
 * the subject of a tuple. Returns the core element of the fragment with
 * all of the excess stripped away, such as fully qualified URL's.
 */
func ConvertFreebaseField(raw string) string {
    if strings.HasPrefix(raw, "<http") {
        raw = strings.Replace(raw, "<http://rdf.freebase.com/ns/", "", -1)
        // Remove one to get rid of the closing angle bracket.
        raw = raw[0:len(raw)-1]
    }
    
    // If there are at least two quotation marks, trim off everything outside
    // of the outermost quotes.
    if strings.Index(raw, "\"") >= 0 {
        start := strings.Index(raw, "\"")
        end := strings.LastIndex(raw, "\"")
        
        if start != end {
            raw = raw[start+1:end]
        }
    }
    
    return raw
}

/**
 * Breaks a line into it's three constituent components: the subject, the
 * predicate, and the object. Also invoked ConvertFreebaseField, which
 * transforms the raw text into a similar format across all fragments and
 * records.
 */
func ParseLine(line string) (string, string, string) {
    // If the string is localized to anything but English, throw it out.
    // Can't currently support multiple languages and Freebase coverage
    // seems to be pretty spotty.
    if strings.Index(line, "@") >= 0 {
        i := strings.Index(line, "@")
        if line[i:i+3] != "@en" {
            return "", "", ""
        }
    }
    
    fragment := strings.Split(line, "\t")
    
    return ConvertFreebaseField(fragment[0]), 
        ConvertFreebaseField(fragment[1]), 
        ConvertFreebaseField(fragment[2])
}

/**
 * When a keeper is found we need to transform the map into the proper
 * data structure that can be recognized by the rest of the pipeline. This
 * function pulls important fields from the mapping and stores them in a
 * CountryTagData object, which is stored in Mongo and can be read by
 * other components in the Newsflash pipeline.
 *
 * TODO: map the actual fields once we know the predicates.
 */
func ConvertToCTD(obj map[string][]string) newsflash.CountryTagData {
    ctd := newsflash.CountryTagData{}
    
    ctd.CountryName = "tbd"
    ctd.CountryCode = "tbd"
    ctd.LeaderName = "tbd"
    ctd.Terms = append(ctd.Terms, []string{}...)
    
    return ctd
}

/**
 * Perform two passes over a Freebase file; the first pass identifies all entities
 * that are labeled as countries. The second pass finds and stores relevant fields
 * for the entities that were labeled in the first pass.
 */
func main() {
    flag.Parse()
    
    countries, names := RunFirstStage(*FreebasePath)
    countries = RunSecondStage(*FreebasePath, countries, names)
    
    // Store data for valid countries.
    log.Println("Storing in database...")
    session, err := mgo.Dial("172.30.0.101")
    if err != nil {
        log.Println("Couldn't connect to MongoDB: " + err.Error())
        return
    }
    defer session.Close()
    
    collection := session.DB("newsflash").C("country_tags")
    
    for _, country := range countries {
        if len(country.CountryCode) > 0 {
            collection.Insert(country)
            log.Println(fmt.Sprintf("Valid: %+v", country))
        } else {
            log.Println(fmt.Sprintf("Invalid: %+v", country))
        }
    }
}