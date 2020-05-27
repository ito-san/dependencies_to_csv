# coding:UTF-8

import csv
import glob
import os
import sys
from xml.etree import ElementTree

argvs = sys.argv
argc = len(argvs)

if argc != 2:
  print("Usage: # python {0} directory".format(argvs[0]))
  quit()

class Dependency:
  def __init__(self):
    self.name = ''
    self.depend = []
    self.build_depend = []
    self.build_export_depend = []
    self.exec_depend = []
    self.test_depend = []
    self.buildtool_depend = []
    self.doc_depend = []

depend_max = 0
build_depend_max = 0
build_export_depend_max = 0
exec_depend_max = 0
test_depend_max = 0
buildtool_depend_max = 0
doc_depend_max = 0

excludes = []

def parse_element(root, target):
  global excludes
  deps = []
  for name in root.iter(target):
    deps.append(name.text)
  return deps

def parse(path):
  dep = Dependency()
  tree = ElementTree.parse(path)
  root = tree.getroot()

  dep.name = root.find("name").text
  dep.depend = parse_element(root, 'depend')
  dep.build_depend = parse_element(root, 'build_depend')
  dep.build_export_depend = parse_element(root, 'build_export_depend')
  dep.exec_depend = parse_element(root, 'exec_depend')
  dep.test_depend = parse_element(root, 'test_depend')
  dep.buildtool_depend = parse_element(root, 'buildtool_depend')
  dep.doc_depend = parse_element(root, 'doc_depend')
  return dep

def exclude_element(dep):
  global excludes
  dep.depend = [e for e in dep.depend if e not in excludes]
  dep.build_depend = [e for e in dep.build_depend if e not in excludes]
  dep.build_export_depend = [e for e in dep.build_export_depend if e not in excludes]
  dep.exec_depend = [e for e in dep.exec_depend if e not in excludes]
  dep.test_depend = [e for e in dep.test_depend if e not in excludes]
  dep.buildtool_depend = [e for e in dep.buildtool_depend if e not in excludes]
  dep.doc_depend = [e for e in dep.doc_depend if e not in excludes]
 
def calculate_column(dep):
  global depend_max
  depend_max = max(depend_max, len(dep.depend))

  global build_depend_max
  build_depend_max = max(build_depend_max, len(dep.build_depend))

  global build_export_depend_max
  build_export_depend_max = max(build_export_depend_max, len(dep.build_export_depend))

  global exec_depend_max
  exec_depend_max = max(exec_depend_max, len(dep.exec_depend))

  global test_depend_max
  test_depend_max = max(test_depend_max, len(dep.test_depend))

  global buildtool_depend_max
  buildtool_depend_max = max(buildtool_depend_max, len(dep.buildtool_depend))

  global doc_depend_max
  doc_depend_max = max(doc_depend_max, len(dep.doc_depend))

def generate_row(list, max):
  row = []
  for i in range(max):
    if i < len(list):
      row.append(list[i])
    else:
      row.append("")
  return row

def generate_header():
  h = ["name"]
  for i in range(depend_max):
    h.append("depend")

  for i in range(build_depend_max):
    h.append("build_depend")

  for i in range(build_export_depend_max):
    h.append("build_export_depend")

  for i in range(exec_depend_max):
    h.append("exec_depend")

  for i in range(test_depend_max):
    h.append("test_depend")

  for i in range(buildtool_depend_max):
    h.append("buildtool_depend")

  for i in range(doc_depend_max):
    h.append("doc_depend")
  
  return h

def main():
  # Make exlude list
  for line in open(".excludes"):
    line = line.strip()
    if not line:
      continue
    if line.startswith('#'):
      continue
    excludes.append(line)

  # Collect dependencies
  dependencies = []
  for (root, dirs, files) in os.walk(argvs[1]):
    for filename in files:
      if filename == "package.xml":
        dependencies.append(parse(os.path.join(root, filename)))
  
  # Add packages to exlude list
  for dep in dependencies:
    excludes.append(dep.name)

  # Remove dependencies entried in exclude
  for i in range(len(dependencies)):
    exclude_element(dependencies[i])

  # Calculate max column
  for dep in dependencies:
    calculate_column(dep)

  # Generate header
  header = generate_header()

  # Output to csv
  with open('packages.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(header)
    for dep in dependencies:
      row = [dep.name]
      row.extend(generate_row(dep.depend, depend_max))
      row.extend(generate_row(dep.build_depend, build_depend_max))
      row.extend(generate_row(dep.build_export_depend, build_export_depend_max))
      row.extend(generate_row(dep.exec_depend, exec_depend_max))
      row.extend(generate_row(dep.test_depend, test_depend_max))
      row.extend(generate_row(dep.buildtool_depend, buildtool_depend_max))
      row.extend(generate_row(dep.doc_depend, doc_depend_max))
      w.writerow(row)

if __name__ == "__main__":
  main()
