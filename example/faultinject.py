#!/usr/bin/python

import sys
import os
import getopt
import time
import random
import signal
import subprocess

#basedir = "/home/jshwei/Desktop/splash_time_automated"
#basedir = "."
currdir = "."
progbin = currdir + "/lulesh"
pin_home = "/home/fang587/pin-3.5-97503-gac534ca30-gcc-linux/"
pinbin = pin_home+"pin"
instcategorylib = pin_home+"source/tools/pinfi/obj-intel64/instcategory.so"
instcountlib = pin_home+"source/tools/pinfi/obj-intel64/instcount.so"
filib = pin_home+"source/tools/pinfi/obj-intel64/faultinjection.so"
#inputfile = currdir + "/inputs/input.2048"
outputdir = currdir + "/prog_output"
basedir = currdir + "/baseline"
errordir = currdir + "/error_output"

if not os.path.isdir(outputdir):
  os.mkdir(outputdir)
if not os.path.isdir(basedir):
  os.mkdir(basedir)
if not os.path.isdir(errordir):
  os.mkdir(errordir)

timeout = 500

optionlist = ["10"]
pid = 0

def execute( execlist):
	#print "Begin"
	#inputFile = open(inputfile, "r")
  global outputfile
  print ' '.join(execlist)
  #print outputfile
  outputFile = open(outputfile, "w")
  p = subprocess.Popen(execlist, stdout = outputFile)
  pid = p.pid
  elapsetime = 0
  while (elapsetime < timeout):
    elapsetime += 1
    time.sleep(1)
    #print p.poll()
    if p.poll() is not None:
      print "\t program finish", p.returncode
      print "\t time taken", elapsetime
      #outputFile = open(outputfile, "w")
      #outputFile.write(p.communicate()[0])
      outputFile.close()
      #inputFile.close()
      return str(p.returncode)
  #inputFile.close()
  outputFile.close()
  print "\tParent : Child timed out. Cleaning up ... "
  p.kill()
  return "timed-out"
	#should never go here
  sys.exit(syscode)


def main():
  #clear previous output
  global run_number, optionlist, outputfile,pid
  outputfile = basedir + "/golden_output"
  execlist = [pinbin, '-t', instcategorylib, '--', progbin]
  execlist.extend(optionlist)
  execute(execlist)


  # baseline
  outputfile = basedir + "/golden_output"
  #execlist = [pinbin, '-t', instcountlib, '--', progbin]
  execlist = [pinbin, '-t', instcountlib,'-fir','1','-rn','main','-fifp','1','--', progbin]
  execlist.extend(optionlist)
  execute(execlist)
  # fault injection
  for index in range(0, run_number):
    outputfile = outputdir + "/outputfile-" + str(index)
    errorfile = errordir + "/errorfile-" + str(index)
    execlist = [pinbin, '-t', filib, '-fioption', 'AllInst','-fir','1','-rn','main','-fifp','1','-firl','32','-firr','1','-idx',str(index),'--', progbin]
    execlist.extend(optionlist)
    ret = execute(execlist)
    if ret == "timed-out":
      error_File = open(errorfile, 'w')
      error_File.write("Program hang\n")
      error_File.close()
    elif int(ret) < 0:
      error_File = open(errorfile, 'w')
      error_File.write("Program crashed, terminated by the system, return code " + ret + '\n')
      error_File.close()
    elif int(ret) > 0:
      error_File = open(errorfile, 'w')
      error_File.write("Program crashed, terminated by itself, return code " + ret + '\n')
      error_File.close()
    datafile = "./x.asc"
    if os.path.isfile(datafile):
        os.rename(datafile,outputdir+"/x.asc."+str(index))
    #with open("memfile","w") as mem_f:
    #    subprocess.Popen("cat /proc/"+str(pid)+"/mem",stdout=mem_f)
    #if os.path.isfile("./memfile"):
    #    os.rename("./memfile",outputdir+"/memfile."+str(index))
if __name__=="__main__":
  global run_number
  assert len(sys.argv) == 2 and "Format: prog fi_number"
  run_number = int(sys.argv[1])
  main()
