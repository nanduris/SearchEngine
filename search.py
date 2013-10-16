# imports
import urllib, re
import bisect
import itertools
import operator
import collections
import os
import math
from porterStemmer import PorterStemmer

# global definitions
numOfDocs = 3024
terms = {}
documents = {}
offset = 0
totalDocLength = 0
avgDocLength = 0
numOfTerms = 0
numOfUniqTerms = 0

# stop list used for stopping technique
stopList = ['document', 'will', 'discuss', 'being', 'of', 'any', 'or', 'a', 'which', 'has', 'at', 'one', 'in', 'some', 'include', 'about', 'the', 'an', 'move', 'by', 'into', 'based', 'either', 'report', 'must', 'its', 'on', 'with', 'and', 'how', 'has', 'been', 'doing', 'since', 'both', 'over', 'as', 'something', 'identify', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


# data structures used

# Term class with attributes: name, ctf, df and documents
class Term:
    def __init__(self, termName, ctf, df, termDocs):
        self.termName = termName
        self.ctf = ctf
        self.df = df
        self.termDocs = termDocs

# Document class with attributes: document ID, document Length and tf
class Document:
    def __init__(self, docId, docLen, tf):
        self.docId = docId
        self.docLen = docLen
        self.tf = tf


# parse the documents and store in 3 files

def parseDocs():
    global terms
    global documents
    files = os.listdir("./cacm")
    sp = open("stopWords.txt")
    stopData = sp.read()
    stopTerms = stopData.lower().split("\n")
    stopTerms = stopTerms[:len(stopTerms) - 1]
    
    filep1 = open("terms.txt", "a")
    filep2 = open("mappings.txt", "a")
    filep3 = open("documents.txt", "a")
    
    termId = 1 
    
    
    for f in files:
        fp = open("./cacm/" + f)
        documentName = f.split(".")[0]
        
        documentId = documentName.split("-")[1]
        line = fp.read()
        data = re.compile(r'.*?<pre>(.*?)</pre>', re.DOTALL).match(line).group(1)
        data = data.replace("\n", " ")
        splitword = re.compile(r'CA\d+', re.DOTALL).findall(data)[0]
        text = data.split(splitword)
        words = text[0]
        words = words.replace("CACM", " ")
        words = words.lower()
        words = re.compile(r'(\w+)', re.DOTALL).findall(words)
        
        stemmer = PorterStemmer()
        words = map(lambda word: stemmer.stem(word, 0, len(word) - 1), words)
        docLength = len(words)   
        
        global totalDocLength
        totalDocLength += docLength
        
        count = collections.Counter(words)   
        
        filep3.write(documentId + " " + documentName + " " + str(docLength) + "\n") 
        
        
           
        
        for term in words:
            if term not in stopTerms and term not in stopList:
                
                global numOfTerms
                numOfTerms += 1
                
                if term in terms:
                    #print(term)
                    attributes = terms[term]
                    #print(attributes)
                    idterm = attributes[0]
                    tf = count[term]
                    documentDetails = attributes[3]
                    latestDoc = len(documentDetails)
                    lastTermId = documentDetails[latestDoc - 1]
                    #print(latestDoc)
                    if documentId == lastTermId[0]:
                        ctf = attributes[1]
                        ctf = ctf + 1
                        df = attributes[2]
                        terms[term] = idterm, ctf, df, documents[term]
                        #print(terms[term])               
                    else:
                        documents[term] = documents[term] + [[documentId, documentName, docLength, tf]]     
                        ctf = attributes[1]
                        ctf = ctf + 1
                        df = attributes[2]
                        df = df + 1
                        terms[term] = idterm, ctf, df, documents[term]
                        #print(terms[term])               
                
                if term not in terms:
                    #print(termId)
                    ctf = 1
                    tf = count[term]
                    df = 1
                    documents[term] = [[documentId, documentName, docLength, tf]]
                    terms[term] = termId, ctf, df, documents[term]
                    
                    termId += 1
                    #print(termId)
                    #print(terms[term])
                    
                    
    
                    
    
    for key in terms:
        
        attributes = terms[key]
        key_termName = key
        key_termId = attributes[0]
        key_ctf = attributes[1]
        key_df = attributes[2]
        key_documents = attributes[3]
        
        offsetLength = len(str(key_termId)) + 1
        
        filep2.write(str(key_termId) + " ")
        
        for doc in key_documents:
            docId = doc[0]
            tf = doc[3]
            offsetLength += len(docId) + len(str(tf)) + 2  
            filep2.write(docId + " " + str(tf) + " ")
            
        
        filep2.write("\n")
        
        global offset
        filep1.write(key_termName + " " + str(key_termId) + " " + str(key_ctf) + " " + str(key_df) + " " + str(offset) + " " + str(offsetLength) + "\n")
        offset += offsetLength + 1
    

# searches the files for queries
def searchFiles(query):
    
    global terms
    global avgDocLength
    global totalDocLength
    global numOfUniqTerms
    
    sp = open("stopWords.txt")
    stopData = sp.read()
    stopTerms = stopData.lower().split("\n")
    stopTerms = stopTerms[:len(stopTerms) - 1]
    
    avgDocLength = totalDocLength / numOfDocs
    
    
    retrievedDocs = {}
    
    for key in query:
        if key not in stopTerms and key not in stopList:
            if key in terms:
                retrievedDocs[key] = search(key)
     
    #for x in [x for x in retrievedDocs.keys() if retrievedDocs[x] == None]:
     #   retrievedDocs.pop(x)     
    return retrievedDocs

#searches the word in the terms.txt file
def search(term):
    
    
    word_docs = {}
    
    filept1 = open("terms.txt")
    
    data = filept1.read()
    startPt = data.find(term)
    #print(startPt)
    
    page = data[startPt:]
    #print(page)
    
    endPt = page.find("\n")
    #print(endPt)
    
    text = page[:endPt]
    #print(text)
    
    term_attributes = text.split(" ")
    
    if len(term_attributes) == 6:
        term_id = term_attributes[1]
        #print(term_id)
        add_value = len(term_id)
        term_ctf = term_attributes[2]
        term_df = term_attributes[3]
        term_offset = term_attributes[4]
        term_offset_length = term_attributes[5]
            
        s_pt = int(term_offset)
        e_pt = s_pt + int(term_offset_length)
            
        filept2 = open("mappings.txt")
            
        line = filept2.read()
            
        line = line[s_pt : e_pt]  
            
            
            
        line_docs = line.split(" ")
            
        line_docs = line_docs[1 : len(line_docs) - 1]
            
            
            
            
        
        filept3 = open("documents.txt")
        doc_buf = filept3.read()
            
        for i in line_docs:
            
            value = line_docs.index(i) % 2
            
            if value == 0:
                docId = i
                dtf = line_docs[value + 1]
                
                start = doc_buf.find(docId)
                buf = doc_buf[start:]
                end = buf.find("\n")
                doc_values = buf[:end]
                doc_values = doc_values.split(" ")
                doc_id = doc_values[1]
                doc_name = doc_values[0]
                doc_len = doc_values[2]
                doc_tf = dtf
                
                word_docs[doc_id] = Document(doc_id, int(doc_len), int(doc_tf))
            
        
        return Term(term, int(term_ctf), int(term_df), word_docs)
            
    
# process the set of queries and get the related documents   
def processQuery():
    
    f = open("Queries.txt")
    text = f.read()
    lines = text.splitlines()
    for i in lines:
        raw_query = i
        raw_query = raw_query.replace("\n", "")
        raw_query = raw_query.lower()
        query = re.compile(r'(\w+)', re.DOTALL).findall(raw_query)
        
        print(query)
        
        queryNum = query[0]
        #print(queryNum)
        
        query = re.compile(r'[a-z]+',re.DOTALL).findall(raw_query)
        
        query = filter(None, query)
        #print(query)
        stemmer = PorterStemmer()
        query = map(lambda word: stemmer.stem(word, 0, len(word) - 1), query)

        
        queryLen = len(query)
        #print(queryLen)

        #run the models
        okapiTF(query, queryNum)
        tfIdf(query, queryNum, queryLen)
        smoothing(query, queryNum, 'Laplace')
        smoothing(query, queryNum, 'Jelinek-Mercer')
        bm25(query, queryNum)

    print("Queries processed")


# Vector SPace Model 1
def tfIdf(query, queryNum, queryLen):
    webDocs = searchFiles(query)
    #print(webDocs)

    okapiTFQuery = applyOkapiToQuery(query, queryLen)

    docResults = {}
    for word in webDocs.keys():
        docs = webDocs[word].termDocs
        queryTF = okapiTFQuery[word]
        
        for doc in docs.keys():
            okapiTF = okapiFormula(docs[doc].tf, docs[doc].docLen)
            if doc in docResults:
                docResults[doc] = docResults[doc] + (okapiTF * queryTF)
            else:
                docResults[doc] = okapiTF * queryTF

    backitems=[ [v[1],v[0]] for v in docResults.items()]
    backitems.sort(reverse = True)
    sortedlist=[ backitems[i][1] for i in range(0,len(backitems))]
    outputToFile(sortedlist, docResults, "tf-idf", queryNum)
                
#okapiTF for queries    
def applyOkapiToQuery(query, queryLen):
    okapiTFQuery = {}
    for word in query:
        okapiTFQuery[word] = okapiFormula(1, queryLen)
    return okapiTFQuery

#okapiFormula
def okapiFormula( tf, docLen):
    return int(tf)/(int(tf) + .5 + 1.5 * int(docLen) / avgDocLength)

#Vector Space Model 2
def okapiTF(query, queryNum):
    webDocs = searchFiles(query)

    docResults = {}
    #tf for documents considering idf
    for word in webDocs.keys():
        docs = webDocs[word].termDocs
        #calulating idf
        if webDocs[word].df == 0:
            idf = 0
        else:
            idf = math.log ((numOfDocs/webDocs[word].df),2)
        #okapiTF along with idf for documents
        for doc in docs.keys():
            weight = okapiFormula(docs[doc].tf, docs[doc].docLen) * idf
            if doc in docResults:
                docResults[doc] += weight
            else:
                docResults[doc] = weight

    backitems=[ [v[1],v[0]] for v in docResults.items()]
    backitems.sort(reverse = True)
    sortedlist=[ backitems[i][1] for i in range(0,len(backitems))]
    outputToFile(sortedlist, docResults, "okapi",queryNum)


#BM-25 Formula
def bm25Formula( tf, df, docLen, qtf):
    k1 = 1.2
    RI = 0
    R = 0
    k2 = 100
    subpart1 = ((RI + .5)/(R - RI + .5))/((df - RI + .5)/(numOfDocs - df - R + RI + .5))
    
    subpart2 = (k1 + 1) * tf / (kForBM25(k1, docLen) + tf)

    subpart3 = ((k2 + 1) * qtf / ( k2 + qtf))

    return math.log(subpart1,2)*subpart2*subpart3

#Calculating k for BM-25
def kForBM25(k1,docLen):
    b = 0.9
    return k1 * ( (1-b) + b * docLen/avgDocLength)

#BM-25 Model
def bm25(query,queryNum):    
    webDocs = searchFiles(query)

    qtf = {}
    
    for word in query:
        if word in qtf:
            qtf[word] += 1
        else:
            qtf[word] = 1

    docResults = {}
    for word in webDocs.keys():
        docs = webDocs[word].termDocs
        
        for doc in docs.keys():
            okapiTF = bm25Formula(docs[doc].tf, webDocs[word].df, docs[doc].docLen, qtf[word])
            if doc in docResults:
                docResults[doc] += okapiTF
            else:
                docResults[doc] = okapiTF

    backitems=[ [v[1],v[0]] for v in docResults.items()]
    backitems.sort(reverse = True)
    sortedlist=[ backitems[i][1] for i in range(0,len(backitems))]
    outputToFile(sortedlist, docResults, "BM-25", queryNum)

#Smoothing
def smoothing(query, queryNum, smoothType):
    webDocs = searchFiles(query)

    allDocs = {}
    docResults = {}
    for word in webDocs.keys():
        temp = webDocs[word].termDocs
        for docId in temp.keys():
            allDocs[docId] = temp[docId].docLen
    
    for doc in allDocs.keys():
        docResults[doc] = 1
        for word in webDocs.keys():
            docs = webDocs[word].termDocs
            cf = webDocs[word].ctf
            if doc in docs:
                docResults[doc] = getSmoothenedValue(docResults[doc],docs[doc].tf, cf, docs[doc].docLen, smoothType)
            else:
                docResults[doc] = getSmoothenedValue(docResults[doc],0.0, cf, allDocs[doc], smoothType)

    items=docResults.items()
    backitems=[ [v[1],v[0]] for v in items]
    backitems.sort(reverse = True)
    sortedlist=[ backitems[i][1] for i in range(0,len(backitems))]

    outputToFile(sortedlist, docResults, smoothType, queryNum)

#gets the smoothened value based on the type of model    
def getSmoothenedValue(currentValue, tf, ctf, docLen, smoothType):
        #Laplace Formula
    if smoothType == 'Laplace':
        return currentValue * laplaceFormula(tf, docLen)
        #Jelinek-Mercer Formula
    else:
        return currentValue * jelinekMercerFormula(tf, ctf, docLen)

# Jelenik-Mercer Formula    
def jelinekMercerFormula(tf, ctf, docLen):
    lambdaa = 0.2
    return (lambdaa * tf/docLen) + ((1 - lambdaa) * (ctf/numOfTerms))

# Laplace Formula
def laplaceFormula(tf, docLen):
    return (tf + 1) / ( docLen + numOfUniqTerms)

# writing to an external file
def outputToFile(docIds, TFs, expName,queryNum):
    outputFile = open(expName + "Output.txt", 'a')
    rank = 1
    for doc in docIds:
        if rank <= 1000:
            outputFile.write(str(queryNum) + " Q0 " + str(doc) + " " + str(rank) + " " + str(TFs[doc]) + " " + expName + "\n")
            rank += 1
        else:
            break
    outputFile.close()



#search("what")   
parseDocs()
processQuery()    
    
    
    

