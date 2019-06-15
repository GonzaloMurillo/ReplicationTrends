#!/usr/bin/env python
#-*- coding: utf-8 -*-

from flask import Flask, render_template, request
import os
import glob
import gzip
import re
import json
import ast

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/second_step",methods=['GET', 'POST'])
def second_step():
    # This is the path that comes from the form
    ddfs_path = request.form.get('path')+"/" # Is this slash at the end portable for Linux and Windows?
    # This normalizes the path based on the Operating System
    ddfs_path = os.path.normcase(ddfs_path)

    files_and_dates_list = []

    if (ddfs_path == ''):  # if it is empty, we return error
        return (render_template('empty_path.html'))  # Path was empty

    else:
        # on the specified path we want to search for all ddfs files
        ddfs_files_path = ddfs_path+"/ddfs*"
        ddfs_files = []
        files_and_dates_list=[]
        found=False # If we find a

        for file in glob.glob(ddfs_files_path):
            # a list with all the ddfs files present in the path
            ddfs_files.append(file)

        # Now we need to open every file to obtain its generated date
        for index,f in enumerate(ddfs_files):
            # The could be two types of ddfs files
            # normal files and compressed files .gz
            # We need to detect both of them and proceed

            found=False # For each file we set found = False
            if ".gz" in f:  # gzipped version of ddfs file
                opener = gzip.open
            else:

                opener = open


            with opener(f, "rt") as file:
                files_and_dates = {}  # Dictionary with the files and dates
                for line in file:

                    # Regular expression for catching the time in the ddfs log
                    regexp = r'[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]'

                    matchObj = re.match(regexp, line)  # Does it match what we search at the start of the line?
                    if matchObj:
                        # Add to the dictionary the name of the file and line
                        files_and_dates["checkbox"] = os.path.basename(ddfs_files[index])
                        files_and_dates["name_of_file"] = os.path.basename(ddfs_files[index])
                        files_and_dates["start_date"] = matchObj.group()
                        files_and_dates["path"] = ddfs_path

                        files_and_dates_list.append(files_and_dates)
                        files_and_dates={} #  new reference in memory
                        found=True
                        break
                # If after checking all the files, we have not found a line that matches the date format
                # then we do know the date
                if(not found):
                    files_and_dates["checkbox"] = os.path.basename(ddfs_files[index])
                    files_and_dates["name_of_file"] = os.path.basename(ddfs_files[index])
                    files_and_dates["start_date"] = "UNKNOWN"
                    files_and_dates["path"] = ddfs_path
                    files_and_dates_list.append(files_and_dates)
                    files_and_dates = {}  # new reference in memory


    return render_template('second_step.html',path = ddfs_path,ddfs_files = ddfs_files,files_and_dates = files_and_dates,files_and_dates_list=files_and_dates_list)

@app.route("/third_step",methods=['GET', 'POST'])
def third_step():

    cogido=request.form["files_and_dates"] # We take the hidden filed
    json_acceptable_string = cogido.replace("'", "\"") # We want to convert it
    list_of_dicts = json.loads(json_acceptable_string) # We convert it to a list of dics
    lista_seleccionados=[] # We want to have here just the selected
    path = list_of_dicts[0]['path'] # Can this produce an error?
    for diccionarion in list_of_dicts: # For each item in the dictionary
        for key,value in diccionarion.items():
            if key=="checkbox": # if the key is the checkbox, we get the name (if selected)
                checked=request.form.get(value)
                if checked:
                    path_plus_value=path+diccionarion[key]
                    lista_seleccionados.append(path_plus_value) # we add them to the list

    for x in lista_seleccionados:
        print (x)
    return(render_template("third_step.html",seleccionados=lista_seleccionados))

if(__name__== "__main__"):
    app.run(debug=True)
