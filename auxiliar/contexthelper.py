import locale

class ContextHelper():

    def __init__(self):
        locale.setlocale(locale.LC_ALL, "")
        return
    
    def give_me_a_list_for_context(self,number,contexts_dic_list): # Returns a list with all the information for an specific contexts, that is spread between several autosupports
        requested_context=[]   
        
        for dic in contexts_dic_list: # context_dic_list is a list of dics each one containing the info from an asup file
          for key,value in dic.items(): #dic is a dictionary
            if 'GENERATED_ON' in key:
                    generated_on=value
            if key=='DETAILS':
                
                for details in value: # details is a list with the details of each replication context
                    
                    if int(details[0])==int(number): # the first item of the list details is the replication ctx number
                        details_copy=list(details)
                        details_copy.insert(0,generated_on)
                        requested_context.append(details_copy)
        #print("voy a retornar {}".format(requesdted_context))
        return requested_context

    def give_me_a_list_with_context_numbers(self,context_dic_list): # Returns a list with the context numbers:
        
        context_numbers=[]
        for key,value in context_dic_list[0].items():
            if key == 'DETAILS':
                for i in value:
                    #print("lo que tengo {}".format(i))
                    context_numbers.append(i[0])
        return context_numbers

    def calculate_averages(self,list_for_context):
       
        precomp_written_cumulative = 0
        precomp_remaining_cumulative = 0
        replicated_precomp_cumulative = 0
        replicated_precomp_network_cumulative = 0

        precomp_written_avg = 0
        precomp_remaining_avg = 0
        replicated_precomp_avg = 0
        replicated_precomp_network_avg = 0
        rows=0


        for asup_date in list_for_context:
            columna=0
            rows = rows + 1
            for column in asup_date:
                if(columna == 2):
                    precomp_written_cumulative=precomp_written_cumulative + int(column.strip().replace(",",""))
                if(columna == 3):
                    precomp_remaining_cumulative=precomp_remaining_cumulative + int(column.strip().replace(",",""))
                if(columna == 4):
                    replicated_precomp_cumulative=replicated_precomp_cumulative + int(column.strip().replace(",",""))
                if(columna == 5):
                    replicated_precomp_network_cumulative = replicated_precomp_network_cumulative + int(column.strip().replace(",",""))
                columna = columna + 1

        precomp_written_avg = precomp_written_cumulative / rows
        precomp_remaining_avg = precomp_remaining_cumulative / rows 
        replicated_precomp_avg = replicated_precomp_cumulative / rows
        replicated_precomp_network_avg = replicated_precomp_network_cumulative / rows
        # For format usage, read:https://www.python-course.eu/python3_formatted_output.php
        return '{0:,.0f}'.format(precomp_written_avg),'{0:,.0f}'.format(precomp_remaining_avg),'{0:,.0f}'.format(replicated_precomp_avg),'{0:,.0f}'.format(replicated_precomp_network_avg)