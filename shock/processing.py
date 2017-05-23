def countwords(stream):
    stream = stream.map(lambda x: x[1]) \
            .flatMap(lambda line: line.split(" ")) \
            .map(lambda word: (word, 1)) \
            .reduceByKey(lambda a, b: a+b)
    stream.pprint()
    return stream

def splitwords(stream):
    return stream.map(lambda x: x[1]).flatMap(lambda line: line.split(" "))

def reducebykey(stream):
    stream.map(lambda word: (word, 1)) \
            .reduceByKey(lambda a, b: a+b)
    stream.pprint()
    return stream

def showresults(stream):
    stream = stream.map(lambda x: x[1]) \
            .flatMap(lambda line: line.split(" "))
    stream.pprint()
    return stream

def todf(stream):
    if (stream.count() > 0):
        return stream.toDF()
    else:
        return stream

def filterbus(stream):
    return stream.filter(lambda a: "bus" in a)

def temperatures(stream):
    return stream.where("entity == 'temperature'")

def invalidtemperature(stream):
    return stream.where("value > 273.15")

def onlyvalues(stream):
    return stream.select("value")
