from articletxt import get_body_text
import os

dir_prefix = '../data/html'
filenames = os.listdir(dir_prefix)
print 'Processing %d files.' % len(filenames)

for filename in filenames:
    text = get_body_text('%s/%s' % (dir_prefix, filename))
    
    # Write the body text out to a file.
    fp = open('../data/text/%s.txt' % filename, 'wb')
    fp.write(text)
    fp.close()