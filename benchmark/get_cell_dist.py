import pycassa, sys, MySQLdb, math

num_buckets = 200
mysql_server = 'ec2-75-101-176-237.compute-1.amazonaws.com'
cassandra_servers = ['ec2-107-22-94-1.compute-1.amazonaws.com',]

def get_timestamps_for_id(cf, rid):
    global num_buckets

    row = cf.get(str(rid), include_timestamp=True, column_count=10000)

    timestamps = [int(row[key][1]) for key in row.keys()]
    timestamps.sort()

    min_time = timestamps[0]
    max_time = timestamps[-1]

    delta = (max_time - min_time) / float(num_buckets)
    distr = []
    for i in xrange(num_buckets+1):
        distr.append(len(filter(lambda x: x <= math.ceil(min_time + (i * delta)), timestamps)))

    return (min_time, max_time, len(timestamps), distr)
   
if len(sys.argv) is 2:
    target_id = int(sys.argv[1]) 
else:
    target_id = None

pool = pycassa.ConnectionPool('newsflash', cassandra_servers)
cf = pycassa.ColumnFamily(pool, 'image_histogram')

if len(sys.argv) is 2:
    target_id = int(sys.argv[1])
    print get_timestamps_for_id(cf, target_id)
else:
#  conn = MySQLdb.connect(host='ec2-75-101-176-237.compute-1.amazonaws.com', user='newsflash', passwd="rDZtewnGUULH2Jjs")
    conn = MySQLdb.connect(host='localhost', user='newsflash', passwd="rDZtewnGUULH2Jjs", db='newsflash')
    cursor = conn.cursor()

    cursor.execute("SELECT rid FROM image")
    nums = cursor.fetchall()
    for num in nums:
        try:
            min_time, max_time, count, distr = get_timestamps_for_id(cf, int(num[0]))
            print '%d\t%s\t%s\t%f\t%d\t%s' % (int(num[0]), min_time, max_time, (max_time - min_time) / float(num_buckets), count, ','.join([str(x) for x in distr]))
        except pycassa.cassandra.c10.ttypes.NotFoundException:
            sys.stderr.write("No data for id %d\n" % int(num[0]))
