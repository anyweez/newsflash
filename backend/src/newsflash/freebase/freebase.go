package main

import (
    "bufio"
    "compress/gzip"
    "flag"
    "fmt"
    "log"
    "io"
    "os"
    newsflash "newsflash/shared"
    "strings"
)

var FreebasePath = flag.String("freebase", "", "The path to the gzipped Freebase dump.")
//var mongoUrl = flag.String("mongo", "localhost:27017", "The network location of the MongoDB doc store.")

/**
 * Opens a gzipped file at the specified location and returns a
 * buffered reader. Freebase files are usually quite large (~30 GB)
 * compressed so a buffered reader is necessary to do anything of
 * of value.
 */
func OpenFreebaseDump(path string) (*bufio.Reader, error) {
    // Open the gzipped Freebase dump.
    fi, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer fi.Close()
    
    zipped, err := gzip.NewReader(fi)
    if err != nil {
        return nil, err
    }
    defer zipped.Close()
    
    return bufio.NewReader(zipped), nil
}

/**
 * Removes formatting cruft from a single fragment of a line (for example,
 * the subject of a tuple. Returns the core element of the fragment with
 * all of the excess stripped away, such as fully qualified URL's.
 */
func ConvertFreebaseField(raw string) string {
    raw = strings.Replace(raw, "<http://rdf.freebase.com/ns/", "", -1)
    // Remove one to get rid of the closing angle bracket.
    return raw[0:len(raw)-1]
}

/**
 * Breaks a line into it's three constituent components: the subject, the
 * predicate, and the object. Also invoked ConvertFreebaseField, which
 * transforms the raw text into a similar format across all fragments and
 * records.
 */
func ParseLine(line string) (string, string, string) {
    fragment := strings.Split(line, "\t")
    
    return ConvertFreebaseField(fragment[0]), 
        ConvertFreebaseField(fragment[1]), 
        ConvertFreebaseField(fragment[2])
}

/**
 * Filtering function that identifies whether a particular record is important
 * to retain. In the vast majority of cases the answer will be no, but this
 * function contains the logic to distinguish. The goal is to make it as fast
 * as possible to reject since that's the common case.
 */
func CheckForKeeper(obj map[string][]string) bool {
    // Check if the notable_type == country. If so, accept and if not reject.

    return false
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

func main() {
    flag.Parse()
    countries := make(map[string]newsflash.CountryTagData)
    
    // Get a file pointer to the specified gzipped Freebase dump so that we
    // can read from it line-by-line.
    reader, err := OpenFreebaseDump(*FreebasePath)
    if err != nil {
        log.Println("Error reading Freebase dump: " + err.Error())
        os.Exit(1)
    }
    
    // This file is likely huge so we need to move through it one line at a
    // time so that memory doesn't get overwhelmed.
    current_subj := ""
    current_fields := make(map[string][]string)
    for {
        line, _, err := reader.ReadLine()
        if err == io.EOF {
            break
        }
        // Parse each line and extract subject, predicate, and object. Subjects
        // are annotated to only include mid's (m.*)
        subj, pred, obj := ParseLine(string(line))
        fmt.Println(fmt.Sprintf("[%s] [%s] [%s]", subj, pred, obj))
        
        // Update the current subject.
        if current_subj != subj {
            // Check to see if the current object is of interest before we
            // throw it away. If so, store it in a persistent mapping so that
            // we can do something responsible with it.
            if CheckForKeeper(current_fields) {
                ctd := ConvertToCTD(current_fields)
                countries[ctd.CountryCode] = ctd
            }
            
            // Reset our state variables.
            current_subj = subj
            current_fields = make(map[string][]string)
        }
        
        // There can be more than one value for each predicate, so we need to initialize
        // an array of strings for each predicate. After it's been initialized, simply
        // throw new values into the array when we find them.
        _, exists := current_fields[pred]
        if !exists {
            current_fields[pred] = make([]string, 0)
        }
        current_fields[pred] = append(current_fields[pred], obj)
    }
    
    // TODO: write out all values from `countries`.
}