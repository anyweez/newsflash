# BeautifulSoup = glorious (mal-formed) HTML parser
from BeautifulSoup import BeautifulSoup
import sys, re

if len(sys.argv) < 2:
  print "Please provide the path to the HTML file."
  sys.exit(1)

## First parameter should be the name of the file to read
filename = sys.argv[1]

# Read the file
f = open(filename)
html = f.readlines()
f.close()

soup = BeautifulSoup(''.join(html), convertEntities=BeautifulSoup.HTML_ENTITIES)

articles = soup.findAll('article')

# In the easiest case we can just check for information inside of the <article>
#   tag.  All of the HTML characters and additional tags will be stripped,
#   leaving just plain text.
if len(articles) > 0:
  for segment in articles:
    sibs = segment.findNextSiblings()
    for sib in sibs:
      print sib.text.encode('ascii', errors='ignore')
# In the more challenging case, we don't have <article> tags and need to
#   determine which elements hold the article info.  Right now we're just
#   grabbing the <div> that has the most <p>'s as direct children.  From
#   the articles I've looked at this seems to be pretty indicative of the
#   core content (which conceptually makes sense as well).
else:
  print 'No <article> tags...attempting sketchy heuristics.'

  divs = soup.findAll('div')

  # Get the div with the most <p>'s as children
  p_max = 0
  article = None

  for div in divs:
    subp = div.findAll(['p', 'span'], recursive=False)
    if len(subp) > p_max:
      p_max = len(subp)
      article = div
 
  # Print out the text in the <p> and <span> tags in the chosen article.
  if article is not None:
    sections = article.findAll(['p', 'span'])
    for section in sections:
      print section.text.encode('ascii', errors='ignore')
  else:
    raise Exception('Could not find article body in %s' % (filename))
