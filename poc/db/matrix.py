import db, pycassa, time, json, ConfigParser
    
class MatrixStore(object):
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        self.table_name = config.get('storage', 'matrix_name')
        
        host = config.get('storage', 'matrix_host')
        self.db = db.RecordStore(host)
# Create the counters' dictionary with the first element empty
#   Elements will be updated for each call, including the time when the call was made and the time lapse
        self.times = {"tTotalSetSQL" : [],
                      "tTotalGetSQL" : [],
                      "tTotalGetrowSQL" : [],
                      "tTotalSetCass" : [],
                      "tTotalGetCass" : [],
                      "tTotalGetrowCass" : [],
                      "N" : [],
                      "counterToSave" : 0}
        self.maxCounterToSave = 1000
        
        # Make sure that the table exists.        
        self.db.execute("CREATE TABLE IF NOT EXISTS %s (cid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, x INT, y INT, val FLOAT)" % (self.table_name,))
    
    # Used to set (x, y) = value.  The store currently assumes that
    #   the matrix is symmetric, so (x, y) and (y, x) will always
    #   return the same value.  They actually result in the same 
    #   query.
    def check_counter(self,Nval):
        self.times["N"].append(Nval)
        self.times["counterToSave"] += 1        
        if (self.times["counterToSave"] > self.maxCounterToSave):
            file = open("nodelatency.json", "w") # write mode
            json.dump(self.times, file)    
            print "1000 iterations saved"       
            self.times["counterToSave"] = 0
          
    def set_val(self, x, y, value):
        tInit = time.time()
        small = min(x, y)
        large = max(x, y)
        sql = 'SELECT COUNT(val) FROM %s WHERE x = %s AND y = %s' % (self.table_name, '%s', '%s')
        num_rows = self.db.execute( sql, (small, large) )
        if int(num_rows[0][0]) > 0:
            sql = 'UPDATE %s SET val = %s WHERE x = %s AND y = %s' % (self.table_name, '%s', '%s', '%s')
            self.db.execute( sql, (value, small, large) )
        else:
            sql = 'INSERT INTO %s (x, y, val) VALUES (%s, %s, %s)' % (self.table_name, '%s', '%s', '%s')
            self.db.execute( sql, (small, large, value) )
        tEnd = time.time()
        tTotalSetSQL = tEnd-tInit  	
        self.times["tTotalSetSQL"].append([tInit,tTotalSetSQL])
        self.check_counter(x)

    def get_val(self, x, y):
        tInit = time.time()
        small = min(x, y)
        large = max(x, y)
        sql = 'SELECT val FROM %s WHERE x = %s AND y = %s' % (self.table_name, '%s', '%s')
        tEnd = time.time()
        tTotalGetSQL = tEnd-tInit  	
        self.times["tTotalGetSQL"].append([tInit,tTotalGetSQL])
        self.check_counter()
        return self.db.execute( sql, (small, large) )[0][0]
    
    # Returns a dictionary mapping rid => similarity values.
    def getrow(self, x):
        tInit = time.time()
        sql = 'SELECT x, y, val FROM %s WHERE x = %s OR y = %s' % (self.table_name, '%s', '%s')
        vals = self.db.execute( sql, (x, x) )

        row = {}
        for val in vals:
            if int(val[0]) != int(x):
                row[int(val[0])] = float(val[2])
            else:
                row[int(val[1])] = float(val[2])
        tEnd = time.time()
        tTotalGetrowSQL = tEnd-tInit  	
        self.times["tTotalGetrowSQL"].append([tInit,tTotalGetrowSQL])
        self.check_counter()
        return row
    
class CassandraMatrixStore(object):
    def __init__(self, hosts=[]):
        
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        self.db_host = config.get('storage', 'matrix_host')
        self.table_name = config.get('storage', 'matrix_name')
        
        self.db_pool = pycassa.ConnectionPool('newsflash', server_list=['%s:9160' % self.db_host])
        self.pool_cf = pycassa.ColumnFamily(self.db_pool, self.table_name)
        
    def set_val(self, x, y, val):
        tInit = time.time()
        self.pool_cf.insert(str(x), { str(y) : str(val) })
        tEnd = time.time()
        tTotalSetCass = tEnd-tInit
        self.times["tTotalSetCass"].append([tInit,tTotalSetCass])
        self.check_counter()
        
    def get_val(self, x, y):
        tInit = time.time()
        result = self.pool_cf.get(str(x), str(y))
        tEnd = time.time()
        tTotalGetCass = tEnd-tInit
        self.times["tTotalGetCass"].append([tInit,tTotalGetCass])
        self.check_counter()
        return float(result[x])
    
    def getrow(self, x):
        tInit = time.time()
        result = self.pool_cf.get(str(x))
        output = {}
        for key in result:
            output[int(key)] = float(key)
        tEnd = time.time()
        tTotalGetrowCass = tEnd-tInit  	
        self.times["tTotalGetrowCass"].append([tInit,tTotalGetrowCass])
        self.check_counter()
        return output
