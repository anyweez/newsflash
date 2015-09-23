import poc.db.db as db

# This script simply counts the number of records that are available
#   in the object store and prints it to the screen.

rs = db.RecordStore('localhost')
result = rs.execute("SELECT COUNT(rid) FROM records")

print result[0][0]