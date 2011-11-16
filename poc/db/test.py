import db

rstore = db.RecordStore('localhost')

record = db.Record()
record.title = 'The Neverending Story'
record.author = 'e.e. cummings'

# Test the storing capability.
newid = rstore.store(record)
print 'The new record is stored at ID #%d' % (newid,)

# Try to refetch whatever we just stored.
fromdb = rstore.get(newid)
print "Here's the data again: [%s, %s]" % (fromdb.title, fromdb.author) 

# Fetch a range of things.
itemlist = rstore.getrange(1, 100)
print "Looked for the first 100 items.  Found %s" % len(itemlist)
print "Item #1: [%s, %s]" % (itemlist[0].title, itemlist[1].author)