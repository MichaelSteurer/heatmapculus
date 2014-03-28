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
import argparse
import sys
import string
import os
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

if len(logging.getLogger().handlers) > 1:
  logging.getLogger().addHandler(console)


def parse_float(num):
    try:
      return float(num.replace(",", "."))
    except ValueError:
      return "Nan"


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


def transform_array_to_heatmap(coordinates, resize_factor=1):
  border = 10

  x_list = [element[1] for element in coordinates]
  z_list = [element[3] for element in coordinates]


  min_x, max_x = int(min(x_list)), int(max(x_list))
  min_z, max_z = int(min(z_list)), int(max(z_list))

  logging.info("min_x: %s, max_x: %s" % (min_x, max_x))
  logging.info("min_y: %s, max_y: %s" % (min_z, max_z))

  heatmap_size_x = ((max_x - min_x)) / resize_factor + 1 + 2 * border
  heatmap_size_z = ((max_z - min_z)) / resize_factor + 1 + 2 * border

  offset_x = abs(int(min(x_list)))
  offset_z = abs(int(min(z_list)))

  logging.debug("Heatmap Size: %s/%s" % (heatmap_size_x, heatmap_size_z))
  logging.debug("Transformation Offset: %s/%s" % (offset_x, offset_z))

  heatmap_array = np.zeros((heatmap_size_z, heatmap_size_x))
  for (ts, x, y, z, phi_x, phi_y, phi_z) in coordinates:
    current_x = int((x + offset_x ) / resize_factor) + border
    current_z = int((z + offset_z ) / resize_factor) + border

    #logging.debug("Mapping X: %d -> %d" % ((x), current_x))
    #logging.debug("Mapping Y: %d -> %d" % ((z), current_y))

    #numpy arrays: first row and then column!
    heatmap_array[current_z][current_x] += 1
  return heatmap_array


def main(csv_file, background_image, heatmap_scale, offset_x, offset_y):
  img = imread(background_image)
  image_height = img.shape[0]
  image_width = img.shape[1]

  coordinates = list()
  if os.path.isdir(csv_file):
    for filename in os.listdir(csv_file):
      try:
        coordinates += parse_file(csv_file + "/" + filename)
      except:
        logging.error("Could not parse file %s" % filename)
  else:
    coordinates += parse_file(csv_file)

  heatmap_array = transform_array_to_heatmap(coordinates, resize_factor=1)

  ##Filter Array
  def array_transformed(x):
    return np.log(x) if x!= 0 else -np.inf
  func = vectorize(array_transformed)
  heatmap_array = func(heatmap_array)

  #np.set_printoptions(precision=1, suppress=True, linewidth=200)

  ##Show Heatmap
  plt.figure(frameon=False, figsize=(15,12))

  #determine offset according to the first and min/max coordinates
  min_x = min([element[1] for element in coordinates])
  first_x = coordinates[0][1]
  min_y = min([element[3] for element in coordinates])
  first_y = coordinates[0][3]

  delta_x = (first_x - min_x) * heatmap_scale
  delta_x = offset_x - delta_x

  delta_y = (first_y - min_y) * heatmap_scale
  delta_y = offset_y - delta_y

  #imshow(heatmap_array, alpha=1)
  heatmap_size_x = heatmap_array.shape[1] * heatmap_scale
  heatmap_size_y = heatmap_array.shape[0] * heatmap_scale

  imshow(heatmap_array, alpha=1, extent=(delta_x, delta_x + heatmap_size_x, delta_y, delta_y + heatmap_size_y))
  plt.imshow(img, zorder=-1, extent=(0, image_width, image_height, 0))

  plt.show()


#  heatmap_scale = 6.2
#  offset_x = -20
#  offset_y = 180

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
           description='',
           add_help=False)
  parser.add_argument('-s', '--source', required=True, help="")
  parser.add_argument('-m', '--magnify', required=True, type=float, help="")
  parser.add_argument('-x', '--offset_x', required=True, type=int, help="")
  parser.add_argument('-y', '--offset_y', required=True, type=int, help="")
  parser.add_argument('-i', '--background_image', required=True, help="")
  parser.add_argument('--help', action='help')
  cmd = parser.parse_args()

#  if not os.path.isdir(cmdValues):
#    print "The provided parameter is not a directory"
#    sys.exit(-2)

  main(cmd.source, cmd.background_image, cmd.magnify, cmd.offset_x, cmd.offset_y)

  sys.exit(0)
