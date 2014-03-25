#!/usr/bin/env python
# encoding: utf-8
"""

main.py
Created on 25.03.14 at 10:30

Michael Steurer, 2014
Institute for Information Systems and Computer Media
Graz University of Technology

"""

#import MySQLdb
from numpy import vectorize
import sys
import string
import pprint
import csv
import numpy as np
from pylab import *
import logging

log_format = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=log_format,
                    level=logging.DEBUG, stream=sys.stdout)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)


def parse_float(num):
    try: return float(num.replace(",", "."))
    except ValueError: return "Nan"


def parse_file(csv_file):
  coordinates = list()
  with open(csv_file, 'r') as csvfile:
    for row in csv.reader(csvfile, delimiter=','):
      ts = parse_float(row[0])
      x = parse_float(row[1])
      y = parse_float(row[2])
      z = parse_float(row[3])
      phi_x = parse_float(row[4])
      phi_y = parse_float(row[5])
      phi_z = parse_float(row[6])

      coordinates.append((ts, x, y, z, phi_x, phi_y, phi_z))
  return coordinates


def transform_array_to_heatmap(coordinates, resize_factor):
  x_list = [element[1] for element in coordinates]
  z_list = [element[3] for element in coordinates]

  heatmap_size_x = (int(max(x_list)) - int(min(x_list))) / resize_factor + 1
  heatmap_size_z = (int(max(z_list)) - int(min(z_list))) / resize_factor + 1
  heatmap_array = np.zeros((heatmap_size_x, heatmap_size_z))

  offset_x = -int(min(x_list))
  offset_z = -int(min(z_list))

  logging.info("Heatmap Size: " + str(heatmap_size_x) + "/" + str(heatmap_size_z))

  for (ts, x, y, z, phi_x, phi_y, phi_z) in coordinates:
    current_x = int((x + offset_x) / resize_factor)
    current_z = int((z + offset_z) / resize_factor)

    logging.debug("Mapping: %d -> %d" % ((x + offset_x), current_x))
    logging.debug("Mapping: %d -> %d" % ((z + offset_z), current_z))

    heatmap_array[current_x][current_z] += 1
  return heatmap_array

def main(csv_file):
  coordinates = parse_file(csv_file)
  resize_factor = 3
  heatmap_array = transform_array_to_heatmap(coordinates, resize_factor)

  ##Filter Array
  def array_transformed(x):
    return x if x!= 0 else -np.inf
  func = vectorize(array_transformed)
  heatmap_array = func(heatmap_array)

  #np.set_printoptions(precision=1, suppress=True, linewidth=200)

  ##Show Heatmap
  plt.figure(frameon=False)
  imshow(heatmap_array, cmap=cm.jet, alpha=1)
  show()

if __name__ == "__main__":
  if len(sys.argv) == 2:
    csv_file = sys.argv[1]
    main(csv_file)
  else:
    print "Usage wrong"
    sys.exit(-2)

  sys.exit(0)
