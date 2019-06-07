#!/usr/bin/env python
#-*- coding: utf-8 -*-

from flask import Flask,render_template,request
import os
import glob
import gzip
import re

app=Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/second_step")
def second_step():


    ddfs_path=request.args.get('path') # This is the path that comes from the form
    ddfs_path=os.path.normcase(ddfs_path) # This normalizes the path based on the Operating System

    if (ddfs_path == ''): # if it is empty, we return error
        return (render_template('empty_path.html')) # Path was empty

    else:
        ddfs_files_path=ddfs_path+"/ddfs*" # on the specified path we want to search for all ddfs files
        ddfs_files=[]
        for file in glob.glob(ddfs_files_path):
            ddfs_files.append(file) # a list with all the ddfs files present in the path
        files_and_dates={} # Dictionary with the files and dates
        regexp=r'[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]'

        # Now we need to open every file to obtain its generated date
        for index,f in enumerate(ddfs_files):

            if ".gz" in f:
                with gzip.open(f, "rt") as file:
                    for line in file:
                        matchObj=re.match(regexp, line)
                        if matchObj:
                            files_and_dates[os.path.basename(ddfs_files[index])]=matchObj.group() # Add to the dictionary the name of the file and line
                            break
            else:
                with open(f) as file:
                    for line in file:
                        matchObj = re.match(regexp, line)
                        if matchObj:
                            files_and_dates[os.path.basename(ddfs_files[
                                                                 index])] = matchObj.group()  # Add to the dictionary the name of the file and line
                            break

    print(files_and_dates)
    return render_template('second_step.html',path=ddfs_path,ddfs_files=ddfs_files,files_and_dates=files_and_dates)

if(__name__== "__main__"):
    app.run(debug=True)
