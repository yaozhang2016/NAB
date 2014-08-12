import os
import copy
import pandas
import util

class DataSet(object):


  def __init__(self, srcPath):
    self.srcPath = srcPath

    self.fileName = os.path.split(srcPath)[1]

    self.data = pandas.io.parsers.read_csv(self.srcPath,
                                          header=0, parse_dates=[0])


  def write(self, newPath=None):
    path = newPath if newPath else self.srcPath
    self.data.to_csv(path, index=False)

  def modifyData(self, columnName, data=None, write=False):
    # print self.srcPath
    if data:
      self.data[columnName] = data
    else:
      del self.data[columnName]

    if write:
      self.write()

  def getTimestampRange(self, t1, t2):
    tmp = self.data[self.data['timestamp'] >= t1]
    ans = tmp[tmp['timestamp'] <= t2]['timestamp'].tolist()
    return ans


  def __str__(self):
    ans = ''
    ans += 'path:                %s\n' % self.srcPath
    ans += 'file name:           %s\n'% self.fileName
    ans += 'data size:         ', self.data.shape()
    ans += 'sample line: %s\n' % ', '.join(self.data[0])
    return ans


class Corpus(object):

  def __init__(self, srcRoot):
    self.srcRoot = srcRoot
    self.dataSets = self.getDataSets()
    self.numDataSets = len(self.dataSets)

  def getDataSets(self):
    filePaths = util.absoluteFilePaths(self.srcRoot)
    dataSets = [DataSet(path) for path in filePaths]

    def getRelativePath(srcRoot, srcPath):
      return srcPath[srcPath.index(srcRoot)+len(srcRoot):].strip('/')

    self.dataSets = {getRelativePath(self.srcRoot, d.srcPath) : d \
                                                            for d in dataSets}
    return self.dataSets

  def addColumn(self, columnName, data, write=False, newRoot=None):
    corp = self.copy(newRoot) if newRoot else self
    for relativePath in self.dataSets.keys():
      corp.dataSets[relativePath].modifyData(columnName, data[relativePath], write=write)

    return corp

  def removeColumn(self, columnName, write=False, newRoot=None):
    corp = self.copy(newRoot) if newRoot else self
    for relativePath in self.dataSets.keys():
      corp.dataSets[relativePath].modifyData(columnName, write=write)

    return corp

  def copy(self, newRoot=None):

    if newRoot[-1] != '/':
      newRoot += '/'
    if os.path.isdir(newRoot):
      print 'directory already exists'
      return None
    else:
      util.createPath(newRoot)
    newCorpus = Corpus(newRoot)
    for relativePath in self.dataSets.keys():
      newCorpus.addDataSet(relativePath, self.dataSets[relativePath])
      print 'adding %s' % os.path.join(newRoot, relativePath)
    return newCorpus

  def addDataSet(self, relativePath, dataSet):
    self.dataSets[relativePath] = copy.deepcopy(dataSet)
    newPath = self.srcRoot + relativePath
    util.createPath(newPath)
    self.dataSets[relativePath].srcPath = newPath
    self.dataSets[relativePath].write()
    self.numDataSets = len(self.dataSets)

  def getDataSubset(self, query):
    ans = {}
    for relativePath in self.dataSets.keys():
      if query in relativePath:
        ans[relativePath] = self.dataSets[relativePath]
    return ans