import MySQLdb, cPickle, hashlib, ConfigParser

class Record(object):
    def __init__(self):
        pass

class RecordStore(object):
    def __init__(self, host):
        user = 'newsflash'
        pw = 'rDZtewnGUULH2Jjs'
        db = 'newsflash'
        
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        self.table_name = config.get('storage', 'object_type')
        self.identifier = config.get('storage', 'object_identifier')
    
        self.conn = MySQLdb.connect(host, user, pw, db)
        self.cursor = self.conn.cursor()

        # Make sure that the table exists.        
        self.execute("CREATE TABLE IF NOT EXISTS %s (rid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, object TEXT, hash TEXT, identifier TEXT)" % (self.table_name,))
    
    def get(self, rid):
        sql = "SELECT object FROM %s WHERE rid = %s" % (self.table_name, '%s')
        self.cursor.execute(sql, (rid,))
        
        data = self.cursor.fetchone()
        return cPickle.loads(data[0])
    
    def store(self, record):
        sql = "INSERT INTO %s (object, hash, identifier) VALUES (%s, %s, %s)" % (self.table_name, '%s', '%s', '%s')
        otext = cPickle.dumps(record)
        identifier = getattr(record, self.identifier)
        self.cursor.execute(sql, 
            (otext, hashlib.sha224(otext).hexdigest(), identifier))
      
        # Fetch the ID of the record we just inserted. 
        sql = "SELECT rid FROM %s WHERE hash = %s" % (self.table_name, '%s')
        self.cursor.execute(sql, (hashlib.sha224(otext).hexdigest(),))
 
        response = self.cursor.fetchone()

        # Returns the ID of the last item inserted on this connection.
        #   This should be exactly what we need.
        return int(response[0])
    
    def update(self, rid, record):
        sql = "UPDATE %s SET object = %s, hash = %s WHERE rid = %s" % (self.table_name, '%s', '%s', '%s')
        otext = cPickle.dumps(record)
        self.cursor.execute(sql, (otext, hashlib.sha224(otext).hexdigest(), rid))
    
    def getrange(self, rmin, rmax):
        sql = "SELECT object FROM %s WHERE rid >= %s AND rid <= %s ORDER BY rid DESC"
        self.cursor.execute(sql, (self.table_name, rmin, rmax))
        
        rows = self.cursor.fetchall()
        return [cPickle.loads(row[0]) for row in rows]
    
    def record_exists(self, record):
        sql = "SELECT rid FROM %s WHERE hash = %s" % (self.table_name, '%s')
        otext = cPickle.dumps(record)
        
        self.cursor.execute(sql, (hashlib.sha224(otext).hexdigest(),))
        result = self.cursor.fetchone()
        
        if result != None:
            return result[0]
        else:
            return False
        
    def execute(self, query, params = []):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
