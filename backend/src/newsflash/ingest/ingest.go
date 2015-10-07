package main

/**
 * This application reads in a set of RSSRecords containing URL's of RSS feeds.
 * It retrieves those RSS feeds, which are assumed to contain a list of documents,
 * and extracts some information about each document, including most importantly
 * the URL where the full documents can be retrieved.
 *
 * After retrieving this information, it forms NewsflashDoc's for each document
 * and inserts them into the db.articles collection.
 */

import (
    "flag"
    "time"
    "log"
    "os"
    "net/http"
    "io/ioutil"
    "encoding/xml"
	"labix.org/v2/mgo/bson"
    "sync"
    newsflash "newsflash/shared"
)
/**
 * 1. Read all RSS feeds from Mongo.
 * 2. For each, retrieve the feed and parse out URL's.
 * 3. Put URL's in DB.articles collection and update LastIngestion timestamp
 */

type RSSRecord struct {
    Id              bson.ObjectId `bson:"_id"`
    Title           string
    Url             string
    
    LastIngestion   time.Time
}

type RawRSSFeed struct {
    Title   string `xml:"channel>title"`
    Stories []newsflash.NewsflashDoc `xml:"channel>item"`
}

var mongoUrl = flag.String("mongo", "localhost:27017", "The network location of the MongoDB doc store.")
var MongoSession newsflash.DBSession
var wg = sync.WaitGroup{}

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

func main() {
    session := MongoSession.Fork()
    defer session.Close()
    
    rss := make([]RSSRecord, 0)
    
    // Fetch all RSS records
    session.DB("newsflash").C("rss").Find(bson.M{}).All(&rss)
    
    for _, record := range rss {
        wg.Add(1)
        go fetch(record)
    }
    
    wg.Wait()
    log.Println("Finished.")
}

func fetch(rss RSSRecord) {
    defer wg.Done()
    log.Println("Fetching RSS: " + rss.Url)
    
    resp, err := http.Get(rss.Url)
    if err != nil {
        log.Println("Couldn't fetch RSS feed: " + err.Error())
        return
    }
    
    defer resp.Body.Close()
    
    contents, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        log.Println("Error reading response body: " + err.Error())
        return
    }
    
    // Read stories from XML feed into an in-memory object
    feed := RawRSSFeed{}
    xml.Unmarshal(contents, &feed)

    session := MongoSession.Fork()
    defer session.Close()
    
    collection := session.DB("newsflash").C("articles")
    
    // Insert each of the documents assuming that it doesn't already exist.
    // Two documents are considered to be identical if their URL's and titles
    // match exactly, otherwise they are different.
    for _, article := range feed.Stories {
        // Note that these fields are not indexed, so this will be a pretty slow
        // lookup. At this point the speed of this process is not a bottleneck so 
        // this isn't a pressing issue.
        // TODO: convert these fields into a hash and build an index so that this
        // is faster.
        existing, err := collection.Find(bson.M{
            "url": article.Url,
            "title": article.Title,
        }).Count()
        
        if err != nil {
            log.Println("Error reading database: " + err.Error())
            continue
        }
        
        // Only insert the doc if there are no existing documents
        // that match.
        if existing == 0 {
            collection.Insert(article)
        }
    }
    
    // Save the RSS record with updated fields.
    rss.Title = feed.Title
    rss.LastIngestion = time.Now()
    session.DB("newsflash").C("rss").Update(
        bson.M{ "_id": rss.Id },
        rss,
    )
}