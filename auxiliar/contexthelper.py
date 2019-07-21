class ContextHelper():

    def __init__(self):
        return
    
    def give_me_a_list_for_context(self,number,contexts_dic_list):
        requested_context=[]   
        print("Al entrar en la funcion {}".format(contexts_dic_list))
        for dic in contexts_dic_list: # context_dic_list is a list of dics each one containing the info from an asup file
          for key,value in dic.items(): #dic is a dictionary
            if 'GENERATED_ON' in key:
                    generated_on=value
            if key=='DETAILS':
                
                for details in value: # details is a list with the details of each replication context
                    print("lo que vale details {}".format(details))
                    if int(details[0])==number: # the first item of the list details is the replication ctx number
                        details_copy=list(details)
                        details_copy.insert(0,generated_on)
                        requested_context.append(details_copy)
        return requested_context