import numpy, sys
import matplotlib.pyplot as plt

def normalize(data):
  largest = float(max(data))

  if largest > 0.0:
    return [num / largest for num in data]
  else: 
    return data

filename = sys.argv[1]

infile = open(filename)
record_lines = infile.readlines()
infile.close()

records = [line.strip().split('\t') for line in record_lines[1:]]
queue1 = [float(record[1]) for record in records]
queue2 = [float(record[2]) for record in records]
queue3 = [float(record[3]) for record in records]

yax = numpy.arange(0.0, 1.0, 1.0 / len(queue1))

queue1 = normalize(queue1)
queue2 = normalize(queue2)
queue3 = normalize(queue3)

plt.plot(queue1, yax, queue2, yax, queue3, yax)
plt.savefig('chart.png')
