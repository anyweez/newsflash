package main

import (
    "flag"
    "fmt"
	"labix.org/v2/mgo/bson"
    newsflash "newsflash/shared"
    "log"
    "net/http"
    "sync"
    "os"
    "time"
)

// TODO: document what's going on
// TODO: read in mapping into CountryTagger
// TODO: somehow pull URL's from a list of RSS feeds 
// TODO: logrus integration

var numParallel = flag.Int("count", 2, "The number of tasks to be executed simultaneously.")
var mongoUrl = flag.String("mongo", "localhost:27017", "The network location of the MongoDB doc store.")

var MAX_NGRAM_SIZE = 3

var wg = sync.WaitGroup{}
var MongoSession newsflash.DBSession


func init() {
    flag.Parse()
    
    // Initialize the MongoDB session so that it can be used in a couple of 
    // different places.
    var err error
    MongoSession, err = newsflash.NewDBSession(*mongoUrl)
    if err != nil {
        log.Println("Error connecting to MongoDB instance: " + err.Error())
        os.Exit(1)
    }
    
    log.Println("MongoDB session initialized.")
}

/**
 * Process that retrieves documents containing URL's, fetches the content
 * of those URL's, and annotates the host document with information about
 * the country that is the subject of the article as well as other countries
 * involved in the story.
 */
func main() {
    flag.Parse()
    
    // Create a read-only object that can convert tuples of words into
    // nation labels. Note that this is only intended to handle small
    // quantities of words in a single call (i.e. likely 1-3 words).
    tagger := NewCountryTagger()
    docs := make([]newsflash.NewsflashDoc, 0)
    
    session := MongoSession.Fork()
    defer session.Close()
     
    c := session.DB("newsflash").C("articles")
    c.Find(bson.M{}).All(&docs)
    
    fmt.Println(fmt.Sprintf("Found %d docs.", len(docs)));
    
    work := make(chan newsflash.NewsflashDoc)
    
    // Kick off a few different goroutines, each of which will handle
    // a job at a time and have read-only access to the tagger.
    for i := 0; i < *numParallel; i++ {
        wg.Add(1)
        go annotate(work, &tagger)
    }
    
    for i := 0; i < len(docs); i++ {
        work <- docs[i]
    }
    
    close(work)
    
    wg.Wait()
    fmt.Println("Done!")
}

func annotate(queue chan newsflash.NewsflashDoc, tagger *CountryTagger) {
    defer wg.Done()
    
    session := MongoSession.Fork()
    defer session.Close()
    
    c := session.DB("newsflash").C("articles")
    
    // Constantly poll the queue's channel until it closes.
    for {
        document, alive := <- queue
        
        // If there are no more tasks, terminate this goroutine.
        if !alive {
            return
        }
        
        fmt.Println(fmt.Sprintf("[Fetching] %s", document.Url));
        resp, err := http.Get(document.Url)
        
        if err != nil {
            log.Println("HTTP error: " + err.Error())
            continue
        }
    
        defer resp.Body.Close()
            
        // Get the URL without any redirects (common w/ RSS feeds).
        document.Url = resp.Request.URL.String()
        document.LastRetrieval = time.Now()
        
        content, err := getContent(resp.Body)
        if err != nil {
            log.Println("Error reading body: " + err.Error())
            continue
        }
        
        document.Title, err = getTitle(content)
        terms, err := getTerms(content)
        
        docScore := make(map[string]int)
        // Iterate through all possible word lengths.
        for length := 1; length <= MAX_NGRAM_SIZE; length++ {
            for i := 0; i < len(terms); i++ {
                upper := min(i+length, len(terms)-1)
                ngram := make([]string, length, length)
                copy(ngram, terms[i:upper])

                label, valid := tagger.LabelWords(ngram)
                
                // If we get a label, add it to the tally.
                if valid {
                    _, exists := docScore[label]
                    if exists {
                        docScore[label] += 1
                    } else {
                        docScore[label] = 1
                    }
                }
            }
        }
        // A basic algorithm to identify what the "major" and "minor" countries in an article
        // are, which accounts for the number of occurences (counted as unweighted events)
        // in relation to the total length of the article.
        document.MajorCountries, document.MinorCountries = selectCountries(docScore, len(terms))
        
        fmt.Println(fmt.Sprintf("[Storing] %+v", document))
        // TODO: update the Mongo document.
        c.Update(bson.M{ "_id": document.Id }, document)
    }
}
                      
func min(a int, b int) int {
    if a < b {
        return a
    }
    
    return b
}

func selectCountries(docScore map[string]int, wordCount int) ([]string, []string) {
    majorMin := wordCount / 1000
    
    major := make([]string, 0)
    minor := make([]string, 0)
    
    for label, count := range docScore {
        if count > majorMin {
            major = append(major, label)
        } else if count > 3 {
            minor = append(minor, label)
        }
    }
    
    return major, minor
}