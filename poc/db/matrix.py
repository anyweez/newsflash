import db, pycassa, time, json
    
class MatrixStore(object):
    def __init__(self, host='localhost'):
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
        sql = 'SELECT COUNT(val) FROM matrix WHERE x = %s AND y = %s'
        num_rows = self.db.execute( sql, (small, large) )
        if int(num_rows[0][0]) > 0:
            sql = 'UPDATE matrix SET val = %s WHERE x = %s AND y = %s'
            self.db.execute( sql, (value, small, large) )
        else:
            sql = 'INSERT INTO matrix (x, y, val) VALUES (%s, %s, %s)'
            self.db.execute( sql, (small, large, value) )
        tEnd = time.time()
        tTotalSetSQL = tEnd-tInit  	
        self.times["tTotalSetSQL"].append([tInit,tTotalSetSQL])
        self.check_counter(x)

    def get_val(self, x, y):
        tInit = time.time()
        small = min(x, y)
        large = max(x, y)
        sql = 'SELECT val FROM matrix WHERE x = %s AND y = %s'
        tEnd = time.time()
        tTotalGetSQL = tEnd-tInit  	
        self.times["tTotalGetSQL"].append([tInit,tTotalGetSQL])
        self.check_counter()
        return self.db.execute( sql, (small, large) )[0][0]
    
    # Returns a dictionary mapping rid => similarity values.
    def getrow(self, x):
        tInit = time.time()
        sql = 'SELECT x, y, val FROM matrix WHERE x = %s OR y = %s'
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
    def __init__(self, hosts=['localhost:9160']):
        self.db_pool = pycassa.ConnectionPool('newsflash', server_list=hosts)
        self.pool_cf = pycassa.ColumnFamily(self.db_pool, 'Records')
    
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
