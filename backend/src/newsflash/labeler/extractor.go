package main

import (
    // Handy library for HTML searching.
    "github.com/PuerkitoBio/goquery"
    "errors"
    "html"
    "log"
    "io"
    "strings"
    "regexp"
)

func getContent(reader io.Reader) (*goquery.Document, error) {
    return goquery.NewDocumentFromReader(reader)
}

/**
 * Functions that operate on HTML content and attempt to extract interesting
 * nuggets.
 */

func getTitle(doc *goquery.Document) (string, error) {
    title := doc.Find("title").Text()
    
    if len(title) > 0 {
        return title, nil
    } else {
        return "", errors.New("No title found")
    }
}

func getTerms(doc *goquery.Document) ([]string, error) {
    terms := make([]string, 0)
    doc.Find("p").Each(func(i int, s *goquery.Selection) {
        // Decode any HTML-encoded characters so they can be parsed correctly.
        bdy := html.UnescapeString(s.Text())
        // TODO: condense into a regex?
        bdy = strings.Replace(bdy, "-", " ", -1)
        bdy = strings.Replace(bdy, ",", " ", -1)
        bdy = strings.Replace(bdy, ".", " ", -1)
        bdy = strings.Replace(bdy, ";", " ", -1)
        bdy = strings.Replace(bdy, "\"", " ", -1)
        terms = append(terms, strings.Fields(bdy)...)
    })
    
    re, err := regexp.Compile("[^A-Za-z0-9]+")
    if err != nil {
        log.Println("Unexpected regex compilation error: " + err.Error())
        return []string{}, err
    }
    
    for i := 0; i < len(terms); i++ {
        terms[i] = re.ReplaceAllString(terms[i], "")
    }
    
    return terms, nil
}