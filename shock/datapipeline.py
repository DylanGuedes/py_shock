def countWords(stream):
    stream = stream.map(lambda x: x[1]) \
            .flatMap(lambda line: line.split(" ")) \
            .map(lambda word: (word, 1)) \
            .reduceByKey(lambda a, b: a+b)
    stream.pprint()
    return stream

def splitWords(stream):
    return stream.map(lambda x: x[1]).flatMap(lambda line: line.split(" "))

def reduceByKey(stream):
    stream.map(lambda word: (word, 1)) \
            .reduceByKey(lambda a, b: a+b)
    stream.pprint()
    return stream

def showResults(stream):
    stream = stream.map(lambda x: x[1]) \
            .flatmap(lambda line: line.split(" "))
    stream.pprint()
    return stream

def toDF(stream):
    if (stream.count() > 0):
        return stream.toDF()
    else:
        return stream
