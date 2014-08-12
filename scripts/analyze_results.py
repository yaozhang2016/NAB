#!/usr/bin/env python
# ----------------------------------------------------------------------
# Copyright (C) 2014, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

helpString = """ This script takes a batch of alert log files generated by
run_anomaly.py, scores them, and produces a detailed summary file. """

import os
import numpy
import csv
import yaml
from lib.corpus import Corpus as ResultsCorpus
from lib.label import CorpusLabel

from optparse import OptionParser

from pprint import pprint
# from confusion_matrix import pPrintMatrix

from helpers import (parseConfigFile,
                     getCSVFiles,
                     getDetailedResults)

import sys

def analyzeResults(options):
  """
  Score the output of detectors.
  """

  # Setup
  profiles, detector = parseConfigFile(options)

  resultsCorpus = ResultsCorpus(options.resultsDir)
  corpusLabel = CorpusLabel(options.labelDir, options.dataDir)

  print resultsCorpus.numDataSets
  # Analyze all files
  detailedResults = getDetailedResults(resultsCorpus, corpusLabel, profiles)
  # costIndex = detailedResults[0].index("Cost")

  pprint(detailedResults)
  sys.exit()
  # Write out detailed results
  detailedResultsArray = numpy.array(detailedResults)

  # Skip first row and first two columns
  detailedView = detailedResultsArray[1:,2:].astype('float')

  # Summarize data for file writing
  detailedTotalsArray = numpy.sum(detailedView, axis=0)
  detailedTotalsList = detailedTotalsArray.tolist()
  detailedOutput = os.path.join(options.resultsDir, "detailedResults.csv")
  with open(detailedOutput, 'w') as outFile:

    writer = csv.writer(outFile)
    writer.writerows(detailedResults)
    totalsRow = ['Totals', '']
    totalsRow.extend(detailedTotalsList)
    writer.writerow(totalsRow)

  # Load and compare results to leaderboard
  with open("leaderboard.yaml") as fh:
    leaderboard = yaml.load(fh)

  print "#" * 70
  print "LEADERBOARD"
  pprint(leaderboard)

  print "#" * 70
  print "YOUR RESULTS"
  print "Detector: ", detector

  print "Total cost:",
  print totalsRow[costIndex]

  print "Detailed summary file:", detailedOutput

  congrats(totalsRow[costIndex], leaderboard)


def congrats(currentCost, leaderboard):
  """
  Prints a congratulatory note if the measured results are better than
  known values.
  """
  bestKnownCost = leaderboard["FullCorpus"]["Cost"]
  if currentCost < bestKnownCost:
    print "Congratulations! These results improve on the state of the art."
    print "Your minimum cost (%d) is less than the best known value (%d)" % \
           (currentCost, bestKnownCost)

if __name__ == '__main__':
  # All the command line options
  parser = OptionParser(helpString)
  parser.add_option("-d", "--resultsDir",
                    help="Path to results files. Single detector only!")
  parser.add_option("--verbosity", default=0, help="Increase the amount and "
                    "detail of output by setting this greater than 0.")
  parser.add_option("--config", default="benchmark_config.yaml",
                    help="The configuration file to use while running the "
                    "benchmark.")
  parser.add_option("--profiles", default="user_profiles.yaml",
                    help="The configuration file to use while running the "
                    "benchmark.")
  parser.add_option("--labelDir", default="labels",
                    help="This holds all the label windows for the corpus.")

  parser.add_option("--dataDir", default="data",
                    help="This is the directory that holds the NAB corpus.")

  options, args = parser.parse_args()
  print options.resultsDir
  # Main
  analyzeResults(options)