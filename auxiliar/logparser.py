
class LogParser():
    
    def __init__(self,file_name,start_string,stop_string):
        self.file_name=file_name
        self.start_string=start_string
        self.stop_string=stop_string
    
    def get_generated_on(self):
        """Returns the GENERATED_ON date contained in the autosupport
            Args:
            none: It takes the filename from the self.current_autosupport_name
            Returns:
            generated_on_date:string

            An string with the serial obtained from the autosupport

        """
        with open(self.file_name) as f:
            for autosupport_read_line in f: 
                if(len(autosupport_read_line)!=0): # If the line is empty we discard it
                    if "GENERATED_ON=" in autosupport_read_line:

                        splitted_generated=autosupport_read_line.split("=") # We get just the date and not the string GENERATED_ON
                        date_time_str_splitted=splitted_generated[1].split() # We split the part that is the date, because we do not want time zone (simplification) is really weird if they change timezone from one autosupport to the other
                        date_time_str_aux=date_time_str_splitted[0]+" "+date_time_str_splitted[1]+" "+date_time_str_splitted[2]+" "+date_time_str_splitted[5]+" "+date_time_str_splitted[3] # We build something that can be understood by the frontend
                        return date_time_str_aux


    def search_and_return(self):
       with open(self.file_name) as file:
         start_token = next(l for l in file if l.strip()==self.start_string) # Used to read until the start token
         result = [line for line in iter(lambda x=file: next(x).strip(), self.stop_string) if line]
         return result

    
    def extract_contexts(self,replication_data):
        if(len(replication_data)==0 or "**** No replication history available" in replication_data[1]):
            print("Warning:This autosuport contains no info about replication. Discarted")
         
        
        contexts=[]
        contexts_by_columns=[]
        data_to_plot=[]
        #print("Received {}".format(replication_data))
        # If there is only one context, we do not have the sum column, so we 
        # need to go from range(5,len(replication,data)-1), instead of range(5,len(replication_data)-2)
        if(len(replication_data)==7): # Just one replication context, no (sum) column
            for i in range(5,len(replication_data)-1):
                contexts.append(replication_data[i])              
        else:
            for i in range(5,len(replication_data)-2):# Real info of the contexts start in line 5 and is 2 lines less that what we read (removing --- and cumulative from the end)
                contexts.append(replication_data[i])
        #print("Contexts now {}".format(contexts))
        for i in range(0,len(contexts)):
            contexts_by_columns.append(contexts[i].split()) # We split by space to have columns
        #print("contexts_by_columns {}".format(contexts_by_columns))
        for k in range(0,len(contexts_by_columns)):
            # A context with all the fields has 13 columns (starting from 0)
            # However, if it is initializing has 8
            lon=len(contexts_by_columns[k])
            if(len(contexts_by_columns[k])==12 or len(contexts_by_columns[k])==9 ):
                contexts_by_columns[k]=contexts_by_columns[k][2:] # This is to remove two fields that go into the first context and are not required (date and time)
            # Removing from the context_by_column the latest fields, that are just date information of when was in sync
            #print("Before removing {}".format(contexts_by_columns[k]))
            # here we are putting in the same line
            # a field like Thu Jun 20 11:21
            # but it could be that there is no date in contexts_by_columns[k][6] but (initializing)
            # so we need to check
            if("initializing" not in contexts_by_columns[k][6]):
                contexts_by_columns[k][6]=contexts_by_columns[k][6]+" "+contexts_by_columns[k][7]+" "+contexts_by_columns[k][8]+" "+contexts_by_columns[k][9]
                #print("Despues del invento {}".format(contexts_by_columns[k]))
                for i in range(0,3): # We delete the last 3 items
                    contexts_by_columns[k].pop()
                    #print("Despues de borrar por detras {}".format(contexts_by_columns[k]))
            
            #contexts_by_columns[k]=contexts_by_columns[k][0:5]
            if(contexts_by_columns[k][0]!='(sum)'): # We do not want to add the cummulative infor
                data_to_plot.append(contexts_by_columns[k])
                
        #print("Plotting the following data:\n")
        #print("Size of the list:")
        #print(len(data_to_plot))   
        #print("Actual data to plot:\n")
        #print(data_to_plot)	
        return data_to_plot

    