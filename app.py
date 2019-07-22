#!/usr/bin/env python
#-*- coding: utf-8 -*-

from flask import Flask, render_template, request
from auxiliar import logparser
from auxiliar import contexthelper
import os
import glob
import gzip
import re
import json
import ast

app = Flask(__name__)

# FIRST STEP OF THE APP WIZARD 
@app.route("/",methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# SECOND STEP OF THE APP WIZARD

@app.route("/second_step",methods=['GET', 'POST'])
def second_step():
    # This is the path that comes from the form field called autosupports_path
    autosupports_path = request.form.get('autosupports_path')
    if (not autosupports_path):  # if it is empty, we return error
        return (render_template('error.html',error_code="You have not specified any path. Please go back and fill up the field path."))  # Path was empty
       
    # We normalize the path
    # It deals with Windows and Linux differences in / \
    # https://docs.python.org/3/library/os.path.html
    autosupports_path = autosupports_path + "/"
    autosupports_path = os.path.normcase(autosupports_path)
    

    # If non existant path, we display an error by calling the error.html 
    # template

    if not os.path.exists(autosupports_path):
        #raise Exception("Path not valid")
         return (render_template('error.html',error_code="The specified path does not exist or is not valid"))  
    
    # On the specified path we want to search for all autosupport files
    # We just try to find files starting with autosupport
    autosupports_files_path = autosupports_path+"/autosupport*" 

    autosupport_files = [] # List containing the autosupport files found in the path
    
    # files_and_dates_ld
    # This will be a list of dicts
    # [{'checkbox':'autosupport','name_of_file':'autosupport','start_date':'','path':''}]
    files_and_dates_ld = [] 
    
    # Boolean variable that wil be True
    # if we find the string GENERATED_ON, on the autosupport
    found=False 

    try:
        for file in glob.glob(autosupports_files_path):
            
            autosupport_files.append(file)
    except Exception as e:
        print(e)
  
    # If we do not find any autosupport file
    # Then we display an error message

    if(len(autosupport_files)==0):
        return(render_template('error.html',error_code="The specified path does not contain autosupport files. Please go back and specify a path containing autosupport files."))
        #raise Exception("No autosupport files")
 
    # Now we need to open every file to obtain its generated date
    for index,f in enumerate(autosupport_files): 
        # The could be two types of autosupport files
        # normal files and compressed files .gz
        # We need to detect both of them and proceed

        found=False # For each file we set found = False
        if ".gz" in f:  # gzipped version of autosupport file
            opener = gzip.open # This is a nice trick
        else:
            opener = open # This is a nice trick

        try:
            file=opener(f, "rt") # We use a generic opener function that reacts to .gz and normal files
        except Exception as e:
            print(e)

        files_and_dates = {}  # Dictionary with the files and dates

        # Now for each autosupport file found
        # We gather the required info using Regular Expressions
        # Regular expression for catching the time in the autosupport log
        regexp = r'GENERATED_ON=.*' # We want to search for the GENERATED_ON, on the autosupport files.
        #regexp = r'[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]'

        for line in file:
            
            matchObj = re.match(regexp, line)  # Does it match what we search at the start of the line?
            if matchObj:
                # Add to the dictionary the name of the file and line
                files_and_dates["checkbox"] = os.path.basename(autosupport_files[index])
                files_and_dates["name_of_file"] = os.path.basename(autosupport_files[index])
                files_and_dates["start_date"] = matchObj.group()
                files_and_dates["start_date"]  = files_and_dates["start_date"].split("=")[1] # We just need the date, not the "GENERATED ON" string
                files_and_dates["path"] = autosupports_path
                files_and_dates_ld.append(files_and_dates)
                files_and_dates={} #  new reference in memory
                found=True
                break
        

            # If after checking all the files, we have not found a GENERATED_ON line
            # then we do know the date
    if(not found):
        files_and_dates["checkbox"] = os.path.basename(autosupport_files[index])
        files_and_dates["name_of_file"] = os.path.basename(autosupport_files[index])
        files_and_dates["start_date"] = "UNKNOWN"
        files_and_dates["path"] = autosupports_path
        files_and_dates_ld.append(files_and_dates)
        files_and_dates = {}  # Destroy the object, as we are going to use in the next bucle iteration

    # We render the Jinja Template
    return render_template('second_step.html',path = autosupports_path,autosupport_files = autosupport_files,files_and_dates_ld=files_and_dates_ld)

# THIRD STEP OF THE APP WIZARD 

@app.route("/third_step",methods=['GET', 'POST'])
def third_step():
    
    # info_of_contexts_in_asups will be a list of lists, where each item on the list
    # will be all the information for an specific context in all the asups files analyzed
    # so info_of_contexts_in_asups[0] will for example contain all the information of one
    # context across all asup files
    info_of_contexts_in_asups=[]
   

    # This is where we link step 2 and step 3, taking the info from a hidden field in the previous form
    hidden_filed_in_form=request.form["files_and_dates"] # We take the hidden filed

    # Because this is just a text representation, we need to convert to a Python
    # object, and we use json for that
    json_acceptable_string = hidden_filed_in_form.replace("'", "\"") # We want to convert it
    # info_asups_from_step_two will be a list of dictionaries
    # that represents all the asup files on the path (both selected and not selected)
    info_asups_from_step_two = json.loads(json_acceptable_string) # We convert it to a list of dics
    
    """
    An example of what selected_asups contains:
    [{'checkbox': 'autosupport', 'name_of_file': 'autosupport', 'path': 'c:\\users\\murilg\\...xamples\\', 'start_date': 'Thu May  2 06:46:52...CEST 2019'},
    {'checkbox': 'autosupport.1', 'name_of_file': 'autosupport.1', 'path': 'c:\\users\\murilg\\...xamples\\', 'start_date': 'Wed May  1 06:46:43...CEST 2019'}, 
    {'checkbox': 'autosupport.2', 'name_of_file': 'autosupport.2', 'path': 'c:\\users\\murilg\\...xamples\\', 'start_date': 'Tue Apr 30 06:46:54...CEST 2019'},
    {'checkbox': 'autosupport.3', 'name_of_file': 'autosupport.3', 'path': 'c:\\users\\murilg\\...xamples\\', 'start_date': 'Mon Apr 29 06:46:50...CEST 2019'}, 
    {'checkbox': 'autosupport.4', 'name_of_file': 'autosupport.4', 'path': 'c:\\users\\murilg\\...xamples\\', 'start_date': 'Sun Apr 28 06:46:55...CEST 2019'},
    {'checkbox': 'autosupport.5', 'name_of_file': 'autosupport.5', 'path': 'c:\\users\\murilg\\...xamples\\', 'start_date': 'Sat Apr 27 06:46:44...CEST 2019'}]

    """
    
    list_of_selected_asups=[] # We want to have here just the selected asups (the ones marked by the user)
    path = info_asups_from_step_two[0]['path'] # We obtain the path for all ASUPS. Can this produce an error?
    for one_asup in info_asups_from_step_two: # For each item in the dictionary of ASUPS
        for key,value in one_asup.items():
            if key=="checkbox": # if the key is the checkbox, we check if is was checked in the form
                checked=request.form.get(value)
                if checked: # If string is not empty, then is because it was checked (the string will contain the name)
                    path_plus_value=path+one_asup[key] # We just build the path, plus the name of the file
                    list_of_selected_asups.append(path_plus_value) # we add it to the list

    # This list will contain the information in the ASUP that is related with the
    # Replication Data Transferred over 24 hr, and for every context.
    replication_data=[]
    contexts_dic={}
    # contexts_dic_list will be a list where each item will be a dictionary containing information about
    # the contexts in an ASUP file.
    # The format of each item in the list (a dictionary), will be:
    #{'ASUP_FILE': 'c:\\users\\murilg\\...tosupport', 'DETAILS': [[...], [...], [...], [...]], 'GENERATED_ON': 'Thu May 2 2019 06:46:52'}
    # Details is where we have the information of the replication history for the last 24 hrs in a format like this one
    # [['1', '2,227,815,101', '371,596,567,439', '0', '0', '0.00', 'Wed Dec 5 01:00'], ['2', '4,833,505,928', '937,430,050,087', '0', '0', '0.00', 'Thu Nov 29 01:00'], ['3', '4,833,505,928', '82,860,672,773', '10,040,121,830', '151,923,216', '1.00', 'Thu Apr 18 01:00'], ['4', '2,227,815,101', '0', '2,208,978,412', '26,421,227', '1.00', 'Wed May 1 11:55']]

    contexts_dic_list=[]
   
    # Now we need to search into the files selected, to obtain the Replication Data Transferred over 24 hours
    for autosupport in list_of_selected_asups:
        # Just a call to the Constructor of the LogParser
        log_parser=logparser.LogParser(autosupport,'Replication Data Transferred over 24hr','Replication Detailed History')
        generated_on=log_parser.get_generated_on() # We obtain the GENERATED_ON string on the ASUP file
        replication_data=log_parser.search_and_return() # We obtain the replication data on the ASUP, in pure text

        # We want a list of list variable (list_of_contexts_in_asup) with the processed information of replication_data
        # present in the ASUP we are reading
        # Something like this:
        """
        [['1', '2,227,815,101', '371,596,567,439', '0', '0', '0.00', 'Wed Dec 5 01:00'],
        ['2', '4,833,505,928', '937,430,050,087', '0', '0', '0.00', 'Thu Nov 29 01:00'],
        ['3', '4,833,505,928', '82,860,672,773', '10,040,121,830', '151,923,216', '1.00', 'Thu Apr 18 01:00'],
        ['4', '2,227,815,101', '0', '2,208,978,412', '26,421,227', '1.00', 'Wed May 1 11:55']]

        """
        # We call extract_context, to obtain the list above

        list_of_contexts_in_asup=log_parser.extract_contexts(replication_data)
        contexts_dic['ASUP_FILE']=autosupport
        contexts_dic['GENERATED_ON']=generated_on
        contexts_dic['DETAILS']=list_of_contexts_in_asup # We store in a key DETAILS of the dic, the replication values
        num_contexts=len(list_of_contexts_in_asup) # We store here the number of contexts
        # We add the current dictionary holding replication information 
        # on this particular ASUP to context_dic_list
        # So context_dic_list will contain the replication information contained in all the selected ASUPs
        contexts_dic_list.append(contexts_dic) 
        
        # Because we iterate, we need to reset this two variables
        # to avoid messing it up
        list_of_contexts_in_asup=[] 
        contexts_dic={}
        
    # Call to the constructor of ContextHelper
    log=contexthelper.ContextHelper()
    # Context by number is just a list that contains the contexts numbers in the asup files
    # TODO. What would happen if all the asups do not contain the same num of contexts?
    context_by_number=log.give_me_a_list_with_context_numbers(contexts_dic_list) 
    
    # Now for each context number
    for ctx_number in context_by_number:
        # Here a lot of good things happen
        # info_of_contexts_in_asups will be a list of list
        # where each item is a list with all the info in all the asups for one specific context
        # we need to thank you to the function give_me_a_list_for_context
        info_of_contexts_in_asups.append(log.give_me_a_list_for_context(ctx_number,contexts_dic_list))
    
   # And here we print the third_step template
    return(render_template("third_step.html",info_of_contexts_in_asups=info_of_contexts_in_asups))

if(__name__== "__main__"):
    app.run(debug=True)
