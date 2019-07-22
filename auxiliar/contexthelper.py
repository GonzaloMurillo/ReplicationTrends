class ContextHelper():

    def __init__(self):
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
        print("voy a retornar {}".format(requested_context))
        return requested_context

    def give_me_a_list_with_context_numbers(self,context_dic_list): # Returns a list with the context numbers:
        
        context_numbers=[]
        for key,value in context_dic_list[0].items():
            if key == 'DETAILS':
                for i in value:
                    print("lo que tengo {}".format(i))
                    context_numbers.append(i[0])
        return context_numbers