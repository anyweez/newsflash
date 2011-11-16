import MySQLdb, cPickle

class Record(object):
    def __init__(self):
        pass

class RecordStore(object):
    def __init__(self, host):
        user = 'newsflash'
        pw = 'rDZtewnGUULH2Jjs'
        db = 'newsflash'
    
        self.conn = MySQLdb.connect(host, user, pw, db)
        self.cursor = self.conn.cursor()
    
    def get(self, rid):
        sql = "SELECT object FROM records WHERE rid = %s"
        self.cursor.execute(sql, (rid,))
        
        data = self.cursor.fetchone()
        return cPickle.loads(data[0])
    
    def store(self, record):
        sql = "INSERT INTO records (object) VALUES (%s)"
        self.cursor.execute(sql, (cPickle.dumps(record),))
        
        # Returns the ID of the last item inserted on this connection.
        #   This should be exactly what we need.
        return int(self.cursor.lastrowid)
    
    def update(self, rid, record):
        sql = "UPDATE records SET object = %s WHERE rid = %s"
        self.cursor.execute(sql, (cPickle.dumps(record), rid))
    
    def getrange(self, rmin, rmax):
        sql = "SELECT object FROM records WHERE rid >= %s AND rid <= %s ORDER BY rid DESC"
        self.cursor.execute(sql, (rmin, rmax))
        
        rows = self.cursor.fetchall()
        return [cPickle.loads(row[0]) for row in rows]
