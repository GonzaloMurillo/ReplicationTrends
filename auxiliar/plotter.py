import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cbook as cbook
import random

# A good tutorial of MatPlotLib I have used:
# https://www.pybonacci.org/2012/05/25/manual-de-introduccion-a-matplotlib-pyplot-iii-configuracion-del-grafico/
class Plotter:
    def __init__(self):
        # Just in case we set the plot in mode no interactive. This delays all drawing until show is called
        # Ans we set hold, so new graphs do not overwrite older graphs
        return    
    def random(self):
        random_name=[]
        alphabet=['a','b','c','d','e','A','B','C','D','E','_']
        for  i in range (0,10):
            n=random.randint(0,10)
            random_name.append(alphabet[n]) 
            
        random_name_string=''.join(map(str, random_name))
        return random_name_string

    def plot(self,list_for_context,ctx_number):
        plt.ioff()
        # Now we name the window to replication_plot
        
        plt.figure('replication_plot'+ctx_number) # Each graphic a new name
        plt.figure(figsize=(13.65,10.24)) # Size of the figure
        precomp_written = []
        precomp_remaining = []
        replicated_precomp = []
        network_usage = []

        dates = []
        list_for_context.reverse() # We reverse for plotting the graph from left to right, being left the lower date
        
        for asup_day in list_for_context:
            
                pre_written = int(asup_day[2].replace(",",""))/1024/1024
                #pre_written = "{0:.2f}".format(pre_written)
                precomp_written.append(pre_written)
                dates.append(asup_day[0][4:10]) # We just want the month and day from the date

                pre_remaining = int(asup_day[3].replace(",",""))/1024/1024
                precomp_remaining.append(pre_remaining)

                rep_precomp = int(asup_day[4].replace(",",""))/1024/1024
                replicated_precomp.append(rep_precomp)

                net_usage = int(asup_day[5].replace(",",""))/1024/1024
                network_usage.append(net_usage)
        
        plt.grid() 
        plt.suptitle("Replication Context:"+ctx_number)
        plt.plot(precomp_written,'.-',label = 'Precomp Written')
        plt.plot(precomp_remaining,'.-',label = 'Precomp Remaining')
        plt.plot(replicated_precomp,'.-',label = 'Replicated Precomp')
        plt.plot(network_usage,'.-',label = 'Network used for Repl')
        plt.legend(loc = 'best')
        plt.xticks(np.arange(len(dates)), dates,size="small", color = 'b', rotation = 45 ) # We write the x 
        plt.ylabel('GBi',size="small")
        random_name=self.random()
        name_of_graph="Graph"+str(random_name) # If we put the same name, we have problems with cache
        plt.savefig("static/"+name_of_graph,dpi=75) #75 dpi is for monitor 

        precomp_written = []
        precomp_remaining = []
        replicated_precomp = []
        network_usage = []
        random_number=self.random()
        list_for_context.reverse() # We need to re-reverse to properly calculate the number of days to catch up
        return name_of_graph 
