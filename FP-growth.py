import time
from itertools import chain, combinations

class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}
 
    def increment(self, numOccur):
        self.count += numOccur
 
    def display(self, ind=1):
        print('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.display(ind + 1)

def loadData(filePath):
    with open(filePath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        dataSet = [list(map(int, line.split())) for line in lines]
    return dataSet

def createInitSet(dataSet):
    dataDict = {}
    for itemSet in dataSet:
        if frozenset(itemSet) not in dataDict:
            dataDict[frozenset(itemSet)] = 1
        else:
            dataDict[frozenset(itemSet)] += 1
    return dataDict

def createTree(dataDict, minSup):
    headerTable = {}
    for itemSet in dataDict:
        for item in itemSet :
            headerTable[item] = headerTable.get(item, 0) + dataDict[itemSet]
    keysToRemove = [item for item in headerTable if headerTable[item] < minSup]
    for item in keysToRemove:
        del headerTable[item]
    freqItemSet = set(headerTable.keys())
    if len(freqItemSet) == 0:
        return None, None
    for item in headerTable:
        headerTable[item] = [headerTable[item], None]
    fpTree = treeNode("Null", 1, None)
    for itemSet, count in dataDict.items():
        localD = {} 
        for item in itemSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0] 
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p:(p[1],int(p[0])), reverse=True)]
            updateTree(orderedItems, fpTree, headerTable, count)
    return fpTree, headerTable

def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        inTree.children[items[0]].increment(count)
    else:
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
 
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)

def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

def findPrefixPath(basePat, treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

def mineTree(inTree, headerTable, minSup, preFix, freqItemDict):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: str(p[1]))]
    for basePat in bigL:
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        if len(newFreqSet) > 10:
            continue
        if frozenset(newFreqSet) not in freqItemDict:
            freqItemDict[frozenset(newFreqSet)] =  headerTable[basePat][0]
        else:
            freqItemDict[frozenset(newFreqSet)] += headerTable[basePat][0]
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        condTree, headTab= createTree(condPattBases, minSup)
        if headTab != None:
            mineTree(condTree, headTab, minSup, newFreqSet, freqItemDict)

def fpGrowth(dataSet, minSup):
    initSet = createInitSet(dataSet)
    fpTree, headerTable = createTree(initSet, minSup)
    freqItemDict = {}
    mineTree(fpTree, headerTable, minSup, set([]), freqItemDict)
    return freqItemDict

def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))

def associationRule(freqItemDict, minConf):
    rules = 0
    for freqItem, freqItemSup in freqItemDict.items():
        subsets = powerset(freqItem)
        for s in subsets:
            s = frozenset(s)
            if len(s) > 0 and s != frozenset(freqItem):
                conf = freqItemSup / freqItemDict.get(s, 1)
                if conf >= minConf:
                    rules += 1
    return rules

if __name__=="__main__":
    miningStart = time.time()
    minConf = 0.8
    minSup = 813 #minSupRadio = 0.1
    dataSet = loadData("mushroom.dat")
    freqItemDict = fpGrowth(dataSet, minSup)
    miningEnd = time.time()
    rulesStart = time.time()
    rules = associationRule(freqItemDict, minConf)
    rulesEnd = time.time()
    freqItemCounts = [0] * 10
    for itemset in freqItemDict:
        if 1 <= len(itemset) <= 10:
            freqItemCounts[len(itemset) - 1] += 1
    print("Frequent Item Sets : ")
    for i, count in enumerate(freqItemCounts, 1):
        print("|L^{}|={}".format(i, count))
    print("Number of association rules that meet the conditions : {}".format(rules))
    print("Total Execution Time : {} seconds.".format(rulesEnd - miningStart))
    print("i. frequent item set mining : {} seconds.".format(miningEnd - miningStart))
    print("ii. association rule mining : {} seconds.".format(rulesEnd - rulesStart))