import db, pycassa, ConfigParser

class MatrixStore(object):
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        self.table_name = config.get('storage', 'matrix_name')
        
        host = config.get('storage', 'matrix_host')
        self.db = db.RecordStore(host)
        
        # Make sure that the table exists.        
        self.db.execute("CREATE TABLE IF NOT EXISTS %s (cid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, x INT, y INT, val FLOAT)" % (self.table_name,))
    
    # Used to set (x, y) = value.  The store currently assumes that
    #   the matrix is symmetric, so (x, y) and (y, x) will always
    #   return the same value.  They actually result in the same 
    #   query.
    def set_val(self, x, y, value):
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
    
    def get_val(self, x, y):
        small = min(x, y)
        large = max(x, y)
        sql = 'SELECT val FROM %s WHERE x = %s AND y = %s' % (self.table_name, '%s', '%s')
        return self.db.execute( sql, (small, large) )[0][0]
    
    # Returns a dictionary mapping rid => similarity values.
    def getrow(self, x):
        sql = 'SELECT x, y, val FROM %s WHERE x = %s OR y = %s' % (self.table_name, '%s', '%s')
        vals = self.db.execute( sql, (x, x) )

        row = {}
        for val in vals:
            if int(val[0]) != int(x):
                row[int(val[0])] = float(val[2])
            else:
                row[int(val[1])] = float(val[2])
            
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
        self.pool_cf.insert(int(x), { str(y) : str(val) })
        self.pool_cf.insert(int(y), { str(x) : str(val) })
    
    def get_val(self, x, y):
        result = self.pool_cf.get(str(x), int(y))
        return float(result[x])
    
    def getrow(self, x):
        result = self.pool_cf.get(str(x))
        output = {}
        for key, value in result:
            output[int(key)] = float(value)

        return output
