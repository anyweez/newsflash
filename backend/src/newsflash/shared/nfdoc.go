package shared

import (
	"labix.org/v2/mgo/bson"
    "time"
)

type NewsflashDoc struct {
    Id              bson.ObjectId `bson:"_id,omitempty"`
    Title           string `xml:"title"`
    Url             string `xml:"link"`
    
    // The subjects of the article.
    MajorCountries  []string
    // Other countries referenced in the article.
    MinorCountries  []string
    
    LastRetrieval   time.Time
}