# -*- coding: utf-8 -*-
'''
Author: Tim Holtermann (TU Dortmund, AG Apparatedesign)
'''

def plot_graph(Path_graph, Path_plot):
    import networkx as nx
    import matplotlib.pyplot as plt


    graph=nx.read_graphml(Path_graph)
    color=[]
    width=[]
    node_group=nx.get_node_attributes(graph, 'node_group')
    edge_class=nx.get_edge_attributes(graph, 'edge_class')
    edge_sub_class=nx.get_edge_attributes(graph, 'edge_sub_class')  
    dict_group_color={"Vessel":'red', 'Column':'red', 'Pipe tee':'grey', 'Valves':'grey', 'Fittings':'grey', 'Pump':'blue', 
               'Filter':'yellow', 'Heat exchanger':'orange', 'Connector':'brown', 'MSR':'green'}
    
    #color of nodes   
    for node in graph.nodes():
        Found='No'
        for group in dict_group_color:            
            if node_group[node]==group:
                color.append(dict_group_color[group])
                Found='Yes'
        if Found=='No':
            color.append('white')
  
    #width of the connections   
        for edge in graph.edges():
            if edge_class[edge] in ['Signal line', 'Process connection line']:
                width.append(1)
            elif edge_class[edge]=='Piping' and edge_sub_class[edge]=='Main pipe':
                width.append(1)
            elif edge_class[edge]=='Piping' and edge_sub_class[edge]=='Secondary pipe':
                width.append(1)
            elif edge_class[edge]=='Heat transfer medium':
                width.append(1)           
            else:
                width.append(10)    
  
    plot_graph = plt.figure(figsize=(15,10))#leeres Bild erzeugt, worauf gleich gezeichnet wird
    nx.draw_kamada_kawai(graph, node_color=color, node_size=150, font_size=10, width=width, arrowsize=15, with_labels=True)
    plot_graph.savefig(Path_plot)
    
def plot_graph2(Path_graph, Path_plot):
    import networkx as nx
    import matplotlib.pyplot as plt
    import math

    graph=nx.read_graphml(Path_graph)
    color=[]
    width=[]
    node_sizes=[]
    pos={}
    node_group=nx.get_node_attributes(graph, 'node_group')
    edge_class=nx.get_edge_attributes(graph, 'edge_class')
    edge_sub_class=nx.get_edge_attributes(graph, 'edge_sub_class')  
    dict_group_color={"Vessel":'orange', 'Column':'orange', 'Pipe tee':'grey', 'Valves':'grey', 'Fittings':'grey', 'Pump':'blue', 
               'Filter':'yellow', 'Heat exchanger':'red', 'Connector':'brown', 'MSR':'green'}


    
    #color of nodes   
    for node in graph.nodes():
        Found='No'
        for group in dict_group_color:            
            if node_group[node]==group:
                color.append(dict_group_color[group])
                Found='Yes'
        if Found=='No':
            color.append('white')
            
        if node_group[node] in ['Filter', 'Vessel', 'Column', 'Pump','Heat exchanger', '...']:
            node_sizes.append(2000)
        else:
            node_sizes.append(500) 
        
        pos[node]=(float(graph.nodes[node]['node_x']), float(graph.nodes[node]['node_y']))


  
    #width of the connections   
    for edge in graph.edges():
        if edge_class[edge] in ['Signal line', 'Process connection line']:
            width.append(1)
        elif edge_class[edge]=='Piping' and edge_sub_class[edge]=='Main pipe':
            width.append(1)
        elif edge_class[edge]=='Piping' and edge_sub_class[edge]=='Secondary pipe':
            width.append(1)
        elif edge_class[edge]=='Heat transfer medium':
            width.append(1)           
        else:
            width.append(10) 
                
                
                
    ##alpha=1,
    plot_graph = plt.figure(figsize=(40,20))#leeres Bild erzeugt, worauf gleich gezeichnet wird
    #pos=nx.spring_layout(graph, k=3/math.sqrt(graph.order()))
    nx.draw(graph, pos=pos, node_color=color, node_shape='o', node_size=node_sizes, edgecolors='none', font_size=10, width=width, edge_color='grey', arrowsize=20, with_labels=True, font_weight='bold')
    plot_graph.savefig(Path_plot)   

def Dexpi2graph(DEXPI_path, save_path_graph, save_path_graph_no_MSR, path_IDlist, path_errorLog, savename):
    
    import pandas as pd
    import networkx as nx
    import xml.etree.ElementTree as ET
    import nltk
    import sys
    
    mytree = ET.parse(DEXPI_path)#load DEXPI-File    
    myroot = mytree.getroot()        
    ID_list=pd.DataFrame(columns=['ID', 'P&ID_name', 'neighbors'])#mapping DataFrame    
    Error_log=pd.DataFrame(columns=['Warning', 'Node(s)'])          
    graph=nx.DiGraph()# create directed graph
    
    print('########################################')
    print('Start to process DEXPI file: ', savename)
    print('########################################')
    print('Collecting Equipment...')
    #EQUIPMENT
    
    i=0
    
    for equipment in myroot.findall('Equipment'):#all equipments
    
        #predefine the optional attributes
        P1='Not available'
        unit_P1='Not available'
        unit_P2='Not available'
        P2='Not available'   
        T1='Not available'
        unit_T1='Not available'  
        unit_T2='Not available'  
        T2='Not available' 
        V='Not available'
        unit_V='Not available'
        I='Not available'
        CH='Not available'
        L='Not available'
        O='Not available'
        M='Not available'
        a='Not available'
        b='Not available'
        R='Not available'
        
        #read
        ID=equipment.get('ID')
        N=equipment.get('TagName')
        
        #read equipment coordinates.
        Position = equipment.findall('Position/Location')
        x=float(Position[0].get('X').replace(',', '.'))#Unfortunately the entry is a string and the number format may have to be changed. 
        y=float(Position[0].get('Y').replace(',', '.'))
        
        #Read all equipment attributes
        for equipment_attributes in equipment.findall('GenericAttributes/GenericAttribute'):
            if equipment_attributes.get('Name')=='CLASS':#selecting the class
                C=equipment_attributes.get('Value')
                
            elif equipment_attributes.get('Name')=='SUB_CLASS':#selecting the sub class
                C_sub=equipment_attributes.get('Value')
                
            elif equipment_attributes.get('Name')=='VPE_PRESSURE_DESIGN_MAX':#selecting max design pressure
                #In general, entry is a string containing value and unit, so the string has to be tokenized
                if len(nltk.word_tokenize(equipment_attributes.get('Value')))==2:#Assure correct entry
                    P1=float(nltk.word_tokenize(equipment_attributes.get('Value'))[0].replace(',', '.'))
                    unit_P1=nltk.word_tokenize(equipment_attributes.get('Value'))[1]
                elif equipment_attributes.get('Value')=='': 
                    P1=''
                    unit_P1=''
                else:
                    sys.exit('Invalid entry in Equipment properties') 
                    
            elif equipment_attributes.get('Name')=='VPE_PRESSURE_DESIGN_MIN':#selecting min design pressure
                if len(nltk.word_tokenize(equipment_attributes.get('Value')))==2:
                    P2=float(nltk.word_tokenize(equipment_attributes.get('Value'))[0].replace(',', '.'))#first token of dexpi string is selected
                    unit_P2=nltk.word_tokenize(equipment_attributes.get('Value'))[1]
                elif equipment_attributes.get('Value')=='': 
                    P2=''
                    unit_P2=''
                else:
                    sys.exit('Invalid entry in Equipment properties') 
                    
            elif equipment_attributes.get('Name')=='VPE_TEMP_DESIGN_MAX':#selecting max design temperature
                if len(nltk.word_tokenize(equipment_attributes.get('Value')))==2:            
                    T1=float(nltk.word_tokenize(equipment_attributes.get('Value'))[0].replace(',', '.'))#first token of dexpi string is selected
                    unit_T1=nltk.word_tokenize(equipment_attributes.get('Value'))[1]
                elif equipment_attributes.get('Value')=='': 
                    T1=''
                    unit_T1=''
                else:
                    sys.exit('Invalid entry in Equipment properties') 
                    
            elif equipment_attributes.get('Name')=='VPE_TEMP_DESIGN_MIN':#selecting min design temperature
                if len(nltk.word_tokenize(equipment_attributes.get('Value')))==2:  
                    T2=float(nltk.word_tokenize(equipment_attributes.get('Value'))[0].replace(',', '.'))#first token of dexpi string is selected
                    unit_T2=nltk.word_tokenize(equipment_attributes.get('Value'))[1]
                elif equipment_attributes.get('Value')=='': 
                    T2=''
                    unit_T2=''
                else:
                    sys.exit('Invalid entry in Equipment properties')   
                    
            elif equipment_attributes.get('Name')=='VPE_MAT_PARTS_MEDIA_CONTACT':#selecting material in contact with medium
                M=equipment_attributes.get('Value')
                
            elif equipment_attributes.get('Name')=='VPE_TNK_VOL_BRUTTO':#selecting volume
                if len(nltk.word_tokenize(equipment_attributes.get('Value')))==2: 
                    V=nltk.word_tokenize(equipment_attributes.get('Value'))[0]
                    unit_V=nltk.word_tokenize(equipment_attributes.get('Value'))[1]
                elif equipment_attributes.get('Value')=='': 
                    V=''
                    unit_V=''
                else:
                    sys.exit('Invalid entry in Equipment properties')      
                    
            elif equipment_attributes.get('Name')=='INSULATION':#selecting insulation (Yes/No)
                I=equipment_attributes.get('Value')   
                
            elif equipment_attributes.get('Name')=='COOLING_HEATING_SYSTEM':#selecting cooling/heating system
                CH=equipment_attributes.get('Value')
                
            elif equipment_attributes.get('Name')=='FN_LOCATION':#selecting location
                L=equipment_attributes.get('Value')#outside
    
        #opportunity to determine the unit operation        
        for unit in ['Vessel']:        
                O='Vessel'
        for unit in ['Column']:
                O='Column'
    
        #Add equipment as node with attributes to graph
        graph.add_node(ID, node_ID=ID, node_name=N, node_class=C, node_sub_class=C_sub, node_material=M, 
                   node_unit_V=unit_V, node_P_max=P1, node_unit_P1=unit_P1, node_P_min=P2, node_unit_P2=unit_P2, 
                   node_T_max=T1, node_unit_T1=unit_T1, node_T_min=T2, node_unit_T2=unit_T2, node_volume=V, 
                   node_insulation=I, node_cool_heat_system=CH, node_x=x, node_y=y, node_location=L, node_request=R, 
                   node_a=a, node_b=b, node_operation=O)#create node with attributes       
       
        #add to Dataframe
        ID_list.loc[i,'ID']=ID
        ID_list.loc[i,'class']=C
        ID_list.loc[i,'P&ID_name']=N
        i+=1
    
                   
    #MSR
    print('Collecting Instrumentation Function...')
    
    for PIF in myroot.findall('ProcessInstrumentationFunction'):#all MSR
    
        #predefine the optional attributes
        P1='Not available'
        unit_P1='Not available'
        unit_P2='Not available'
        P2='Not available'   
        T1='Not available'
        unit_T1='Not available'  
        unit_T2='Not available'  
        T2='Not available' 
        V='Not available'
        unit_V='Not available'
        I='Not available'
        CH='Not available'
        L='Not available'
        O='Not available'
        M='Not available'
        a='Not available'
        b='Not available'
        R='Not available'
        
        #Read
        ID=PIF.get('ID')
        N=PIF.get('TagName')
        
        #Read equipment coordinates
        Position = PIF.findall('Position/Location')
        x=float(Position[0].get('X').replace(',', '.'))
        y=float(Position[0].get('Y').replace(',', '.'))
        
        #Read all attributes
        for PIF_attributes in PIF.findall('GenericAttributes/GenericAttribute'):
            
            if PIF_attributes.get('Name')=='CLASS':#selecting the class
                C=PIF_attributes.get('Value')
                
            if PIF_attributes.get('Name')=='PCE_CAT_FUNC':#selecting the type of request
                R=PIF_attributes.get('Value')
                
            elif PIF_attributes.get('Name')=='SUB_CLASS':#selecting the sub class
                C_sub=PIF_attributes.get('Value')
                
            elif PIF_attributes.get('Name')=='LOCATION':#selecting location
                L=PIF_attributes.get('Value')
        
        #Add MSR-unit as node with attributes to graph            
        graph.add_node(ID, node_ID=ID, node_name=N, node_class=C, node_sub_class=C_sub, node_material=M, 
                   node_unit_V=unit_V, node_P_max=P1, node_unit_P1=unit_P1, node_P_min=P2, node_unit_P2=unit_P2, 
                   node_T_max=T1, node_unit_T1=unit_T1, node_T_min=T2, node_unit_T2=unit_T2, node_volume=V, 
                   node_insulation=I, node_cool_heat_system=CH, node_x=x, node_y=y, node_location=L, node_request=R, 
                   node_a=a, node_b=b, node_operation=O)#create node with attributes 
        
        #add to Dataframe
        ID_list.loc[i,'ID']=ID
        ID_list.loc[i,'class']=C
        ID_list.loc[i,'P&ID_name']=N    
        i+=1 
    
    
    #PIPING COMPONENTS
    
    j=1         
    k=1
    
    print('Collecting Piping Components...')
       
    for piping_component in myroot.findall('PipingNetworkSystem//PipingComponent'):#select all piping components
    
        #predefine optional attributes
        P1='Not available'
        unit_P1='Not available'
        unit_P2='Not available'
        P2='Not available'   
        T1='Not available'
        unit_T1='Not available'  
        unit_T2='Not available'  
        T2='Not available' 
        V='Not available'
        unit_V='Not available'
        I='Not available'
        CH='Not available'
        L='Not available'
        O='Not available'
        M='Not available'
        a='Not available'
        b='Not available'
        R='Not available'
        
        #Read
        ID=piping_component.get('ID')
        N=piping_component.get('TagName')
        
        #Read equipment coordinates
        Position = piping_component.findall('Position/Location')
        x=float(Position[0].get('X').replace(',', '.'))
        y=float(Position[0].get('Y').replace(',', '.'))
        
        #in case of a pipe tee
        if piping_component.get('ComponentClass')=='Pipe tee': 
               
            C=piping_component.get('ComponentClass')
            N='Pipe_tee_'+str(j)#P&ID name does not exist, so name by consecutive numbers
            
            ID_list.loc[i,'ID']=ID
            ID_list.loc[i,'class']=C
            ID_list.loc[i,'P&ID_name']=N
            
            i+=1
            j+=1
        
        #in case of an in/-outlet    
        elif piping_component.get('ComponentClass')=='Arrow' or piping_component.get('ComponentClass')=='Flow in pipe connector symbol' or piping_component.get('ComponentClass')=='Flow out pipe connector symbol':            
            
            C=piping_component.get('ComponentClass')
            N='C_'+str(k)#P&ID name does not exist, so name by consecutive numbers
            
            #Read attributes
            for Attribute in piping_component.findall('GenericAttributes/GenericAttribute'):
                if Attribute.get('Name')=='PRODUCT':
                    a=Attribute.get('Value')
                if Attribute.get('Name')=='DESCRIPT':
                    b=Attribute.get('Value') 
                    
            ID_list.loc[i,'ID']=ID
            ID_list.loc[i,'class']=C
            ID_list.loc[i,'P&ID_name']=N
    
            i+=1
            k+=1
        
        #other piping components    
        else:
            
            #Read attributes
            for piping_component_attribute in piping_component.findall('GenericAttributes/GenericAttribute'):
                if piping_component_attribute.get('Name')=='CLASS':
                    C=piping_component_attribute.get('Value')
                elif piping_component_attribute.get('Name')=='SUB_CLASS':
                    C_sub=piping_component_attribute.get('Value')
                    
            #add to Dataframe
            ID_list.loc[i,'ID']=ID
            ID_list.loc[i,'class']=C
            ID_list.loc[i,'P&ID_name']=N
            i+=1
            
        #Add piping component node with attributes to graph
        graph.add_node(ID, node_ID=ID, node_name=N, node_class=C, node_sub_class=C_sub, node_material=M, 
                   node_unit_V=unit_V, node_P_max=P1, node_unit_P1=unit_P1, node_P_min=P2, node_unit_P2=unit_P2, 
                   node_T_max=T1, node_unit_T1=unit_T1, node_T_min=T2, node_unit_T2=unit_T2, node_volume=V, 
                   node_insulation=I, node_cool_heat_system=CH, node_x=x, node_y=y, node_location=L, node_request=R, 
                   node_a=a, node_b=b, node_operation=O)#create node with attributes  
    
        
    #PIPING CONNECTIONS
    
    print('Process Piping Connections...')
    
    i=1
    k=1
    nodes_from_nothing=[]
    nodes_to_nothing=[]
    nodes_not_registrated=[]
    
    for PNS in myroot.findall('PipingNetworkSystem/PipingNetworkSegment'):
        
        #identificate connection
        for connection in PNS.findall('Connection'):
            FromID=connection.get('FromID')
            ToID=connection.get('ToID')
            
            #Connection only added if the node already exists
            if FromID in list(graph.nodes()) and ToID in list(graph.nodes()):
                
                #Connection only added if there is a start and end point
                if FromID!="" and ToID!="" and FromID!=None and ToID!=None:
                
                    #predefine optional parameter
                    M='Not available'
                    D='Not available'
                    C_pipe='Not available'
                    Nu='Not available'
    
                    #Read attributes
                    for piping_attribute in PNS.findall('GenericAttributes/GenericAttribute'):
                        
                        if piping_attribute.get('Name')=='CLASS':#selecting the class
                            C=piping_attribute.get('Value')
                            
                        elif piping_attribute.get('Name')=='SUB_CLASS':#selecting the sub class
                            C_sub=piping_attribute.get('Value')
                            
                        elif piping_attribute.get('Name')=='VPE_MAT_MAIN_MATERIAL':#selecting the material
                            M=piping_attribute.get('Value') 
                            
                        elif piping_attribute.get('Name')=='NOMINAL_DIAMETER':#selecting Diameter
                            D=piping_attribute.get('Value')
                            
                        elif piping_attribute.get('Name')=='MAT_INAME':#selecting pipe class
                            C_pipe=piping_attribute.get('Value')
                            
                        elif piping_attribute.get('Name')=='PIPENO':#selecting Pipe number
                            Nu=piping_attribute.get('Value') 
                            
                    #Add piping connection as edge with attributes to graph
                    graph.add_edge(FromID, ToID, edge_class=C, edge_sub_class=C_sub, edge_material=M,
                               edge_diameter=D, edge_pipe_class=C_pipe, edge_number=Nu)#Adding connection as edge to graph   
    
                #Notice invalid connections
                elif FromID=="" or FromID==None:
                    nodes_from_nothing.append(ToID)                
                elif ToID=="" or ToID==None:
                    nodes_to_nothing.append(FromID) 
    
            #Notice node(s) that was not registrated before
            else:
                if FromID not in list(graph.nodes()) and FromID!=None and FromID!='':
                    nodes_not_registrated.append(FromID)
                elif ToID not in list(graph.nodes()) and ToID!=None and ToID!='':
                    nodes_not_registrated.append(ToID)
    
    #Add warning(s) to the error log
    if nodes_from_nothing!=[]:       
        Error_log.loc[k,'Warning']='There is at least one node without a source. Please make sure it is correct.'
        Error_log.loc[k,'Node(s)']=str(nodes_from_nothing)
        k+=1
    if nodes_to_nothing!=[]:       
        Error_log.loc[k,'Warning']='There is at least one node without a destination. Please make sure it is correct.' 
        Error_log.loc[k,'Node(s)']=str(nodes_to_nothing)
        k+=1 
    if nodes_not_registrated!=[]:      
        Error_log.loc[k,'Warning']='At least one exported edge contains a node that was not registrated before.'
        Error_log.loc[k,'Node(s)']=str(nodes_not_registrated)
        k+=1
    
                          
    #MSR CONNECTIONS
    print('Process Instrumentation Connections...')
    
    for InfoFlow in myroot.findall('ProcessInstrumentationFunction/InformationFlow'):
        
        for connection in InfoFlow.findall('Connection'):
            FromID=connection.get('FromID')
            ToID=connection.get('ToID')
            
            #Connection only added if there is a start and end point
            if FromID and ToID!=None:
            
                #predefine optional parameter
                M='Not available'
                D='Not available'
                C_pipe='Not available'
                Nu='Not available'
                
                #Read attributes
                for attributes in InfoFlow.findall('GenericAttributes/GenericAttribute'):
                    
                    if attributes.get('Name')=='CLASS':
                        C=attributes.get('Value')
                        
                    elif attributes.get('Name')=='SUB_CLASS':#selecting the sub class
                        C_sub=attributes.get('Value')
                
                #Add MSR connection as edge to graph
                graph.add_edge(FromID, ToID, edge_class=C, edge_sub_class=C_sub, edge_material=M,
                           edge_diameter=D, edge_pipe_class=C_pipe, edge_number=Nu)#Adding connection as edge to graph
    
    
    
    ###################################################################################################################      
    ### PROCESS DATA ################################################################################################
    ###################################################################################################################
    print('Clean collected data...')
        
    #REMOVE EMPTY NODES
    
    Empty_1='No'
    Empty_2='No'
    
    for node in graph.nodes():
        if node == "":
            Empty_1='Yes'
        if node == None:
            Empty_2='Yes'
            
    if Empty_1=='Yes':
        graph.remove_node("")    
    if Empty_2=='Yes':
        graph.remove_node(None)
        
    
    #REMOVE ISOLATED NODES
    
    node_class=nx.get_node_attributes(graph, 'node_class')
    node_name=nx.get_node_attributes(graph, 'node_name')
    nodes_isolated={} 
    
    #Identificate every isolated node which is not an Agitator or orifice plate      
    for node in graph.nodes():
        if nx.is_isolate(graph, node) and node_class[node] not in ['Agitator', 'Orifice plate']:
            nodes_isolated[node]=node_name[node]
    
    #Showing a warning if necessary        
    if nodes_isolated!={}:
        Error_log.loc[k,'Warning']='Isolated nodes were identificated and removed. Please make sure it is correct.'
        Error_log.loc[k,'Node(s)']=str(nodes_isolated)
        k+=1    
        
    graph.remove_nodes_from(nodes_isolated.keys())#remove isolated nodes from graph   
     
        
    #CONVERT NODES LIKE PIPING EQUIPMENT AND HOSE IN TO EDGES
    
    node_class=nx.get_node_attributes(graph, 'node_class')
    node_sub_class=nx.get_node_attributes(graph, 'node_sub_class')
    edge_class=nx.get_edge_attributes(graph, 'edge_class')
    remove=[]
    nodes_problem=[]
    pipe_attributes={'Piping with conduit':{'Insulation':'No', 'Heated/cooled':'No'},
                     'Piping insulated':{'Insulation':'Yes', 'Heated/cooled':'No'},
                     'Piping heated or cooled':{'Insulation':'No', 'Heated/cooled':'Yes'},
                     'Piping, heating or cooled insulated':{'Insulation':'Yes', 'Heated/cooled':'Yes'}}#preparation for creating new edge with new attributes (dict to avoid repeating script)
    
    #Add following new attributes to the already existing nodes
    for edge in graph.edges():
        if edge_class[edge]=='Piping':
            graph.add_edge(edge[0], edge[1], edge_insulation='No', edge_heated_cooled='No')
        else:
            graph.add_edge(edge[0], edge[1], edge_insulation='Not available', edge_heated_cooled='Not available')
    
    # Select all relevant nodes
    for node in graph.nodes():
        if node_class[node] in ['Hose', 'Pipe equipment']:
            
            #checking the right connection format, save node and its neighbors
            if len(list((graph.in_edges(node))))==1 and len(list((graph.out_edges(node))))==1:
                remove.append(node)
                all_neighbors=list((nx.all_neighbors(graph, node)))
                FromID=all_neighbors[0]
                ToID=all_neighbors[1]
                
                #In case of a pipe equipment the attributes of the edge in front can be taken over
                if node_class[node]=='Pipe equipment': 
                    C=nx.get_edge_attributes(graph, 'edge_class')[(FromID, node)]
                    C_sub=nx.get_edge_attributes(graph, 'edge_sub_class')[(FromID, node)]
                    M=nx.get_edge_attributes(graph, 'edge_material')[(FromID, node)]
                    D=nx.get_edge_attributes(graph, 'edge_diameter')[(FromID, node)]
                    C_pipe=nx.get_edge_attributes(graph, 'edge_pipe_class')[(FromID, node)]
                    Nu=nx.get_edge_attributes(graph, 'edge_number')[(FromID, node)]
    
                    #the remaining additional attributes depend on the sub class of pipe equipment (saved in the dict above)
                    for sub_class in pipe_attributes:  
                        if node_sub_class[node]==sub_class:                
                            graph.add_edge(FromID, ToID, edge_class=C, edge_sub_class=C_sub, edge_material=M,
                                       edge_diameter=D, edge_pipe_class=C_pipe, edge_number=Nu,
                                       edge_insulation=pipe_attributes[sub_class]['Insulation'],
                                       edge_heated_cooled=pipe_attributes[sub_class]['Heated/cooled'])
                            
                #in case of a hose, attributes can not be taken from pipe in front cause of having own attriubtes
                elif node_class[node]=='Hose':
                    #predefine optional parameter
                    M='Not available'
                    D='Not available'
                    C_pipe='Not available'
                    Nu='Not available'                 
                    
                    #Read hose attributes
                    C=node_class[node]
                    C_sub=node_sub_class[node]
    
                    graph.add_edge(FromID, ToID, edge_class=C, edge_sub_class=C_sub, edge_material=M,
                               edge_diameter=D, edge_pipe_class=C_pipe, edge_number=Nu,
                               edge_insulation='No',
                               edge_heated_cooled='No')
    
            #if the node is not connected in the expected way, a warning is shown
            else:
                nodes_problem.append(node)
     
    if nodes_problem!=[]:
        Error_log.loc[k,'Warning']='Problems in converting hose and piping components. At least one node is connected in an unexpected way.'
        Error_log.loc[k,'Node(s)']=nodes_problem
        k+=1
        
    graph.remove_nodes_from(remove)#remove old nodes for pipe equipment and nodes from graph
    
    
    #EQUIPMENT GROUPS
    print('Group collected Equipment and Attributes...')
    
    node_class=nx.get_node_attributes(graph, 'node_class')
    node_sub_class=nx.get_node_attributes(graph, 'node_sub_class')
    dict_group={'Vessel':['Vessel', 'Vessel with two Diameters', 'Spherical vessel', 'Vessel with dome', 'Vessel, general', 'Silo', 'Gas cylinder', 'Basin', 'Barrel', 'Tank', 'Vessel with agigator', 'Bag', 'Container'],
                'Column':['Column'],
                'Shaping machines':['Vertical shaping machine', 'Horizontal shaping machine'],
                'Crushing/Grinding':['Crushing maschine', 'Mill'],
                'Dryer':['Dryer'],
                'Centrifuge':['Centrifuge'],
                'Separator':['Separator'],
                'Sieving':['Basket band and screening machine', 'Sieving machine'],
                'Mixer/Kneader':['Kneader', 'Mixing pipe', 'Rotating mixer', 'Static mixer'],
                'Valves/Fittings':['Steam trap', 'Flange', 'Orifice plate', 'Flap trap (form 2)', 'Angle check valve','Angle globe valve', 'Angle valve, general', 'Ball valve', 'Breather valve', 'Breather flap', 'butterfly valve', 'Butterfly valve', 'Check valve', 'Check valve angled', 'Check valve angled globe type', 'Check valve globe type', 'Diaphragm valve', 'Float valve', 'Gate valve', 'Globe valve', 'Plug cock', 'Plug valve', 'Pressure reducing valve', 'Safety valve', 'Safety angle valve', 'Safety valve, angled type', 'Swing check valve', 'Three-way ball valve', 'Three-way globe valve', 'Three-way valve, general', 'Valve (general)', 'Valve, angle ball type', 'Valve, angle globe type', 'Valve, angle type (general)', 'Valve, ball type', 'Valve, butterfly type (Form 1)', 'Valve, butterfly type (Form 2)', 'Valve, gate type', 'Valve, general', 'Valve, globe type', 'Valve, needle type', 'Valve, three-way ball type', 'Valve, three-way globe type', 'Valve, three-way type (general)', 'Airtight butterfly valve', 'Flame arrestor', 'Fire protection flap', 'Rupture disk'],
                'Filter':['Filter', 'Band Filter', ' Ion exchange filter', 'Air filter', 'Biological filter', 'Filter press', 'Fluid filter', 'Gas filter', 'Liquid rotary filter'],
                'Pump':['Fluid pump', 'Liquid pump', 'Liquid jet pump'],
                'Compressor':['Compressor', 'Ejector compressor', 'Vacuum pump', 'Vakuum pump', 'Jet vacuum pump', 'Jet vakuum pump'],
                'Heat exchanger':['Heat exchanger', 'Heat exchanger ', 'Heat exchanger, detailed', 'Spiral type heat exchanger','Heat exchanger', 'detailed, Tube bundle with U-tubes', 'Electric Heaters', 'Facility for heating or cooling'],
                'Pipe tee':['Pipe tee'],
                'Connector':['Arrow', 'Flow in pipe connector symbol', 'Flow out pipe connector symbol'],
                'MSR':['PCE Request']}#groups
    dict_sub_group={'Vessel':{'Vessel (solid)':{'Silo':'General', 'Bag':'General', 'Container':'Container for solids'},
                              'Vessel (gaseous)':{'Gas cylinder':'General'},
                              'Vessel (liquid)':'All other'}, 
                    'Valves/Fittings':{'Valve (safety)':{'Safety valve':['spring loaded', 'General'], 'Safety angle valve':['Spring loaded', 'General'], 'Safety valve, angled type':['General', 'spring loaded'], 'Flame arrestor':'all', 'Rupture disk':'all'}, 
                                       'Valve (operation)':'All other'},
                    'Filter':{'Filter (gaseous)':{'Air filter':'General', 'Gas filter':'all'}, 
                              'Filter (liquid)':'All other'},
                    'Heat exchanger':{'Heat exchanger (electric)':{'Electric Heaters':'General', 'Facility for heating or cooling':'General'},
                                      'Heat exchanger (medium)':'All other'}}#sub groups
    
    #create following attributes
    for node in graph.nodes():
        graph.add_node(node, node_group='Not available')
        graph.add_node(node, node_sub_group='Not available')
    
    
    #sorting into groups by the dict (node class has to match with one of the listed classes under a specific group name)
    for name_group in dict_group:
        for node in graph.nodes():
            if node_class[node] in dict_group[name_group]:
                graph.add_node(node, node_group=name_group)#overwrite attribute            
    
    
    node_group=nx.get_node_attributes(graph, 'node_group')
    no_sub_group=[]#List to collect the nodes which are not sorted after sorting
    
    #sorting into sub groups by the dict
    for node in graph.nodes():
        grouped='No'
        for group in dict_sub_group:#regarding all groups  
            if node_group[node]==group:#select nodes belongs to the regarded group
                for sub_group in dict_sub_group[group]:#regarding all sub groups
                
                    if dict_sub_group[group][sub_group]=='All other':#everything else
                        graph.add_node(node, node_sub_group=sub_group)
                        grouped='Yes'
                        break
                        
                    else:
                        for Class in dict_sub_group[group][sub_group]:
                            if Class==node_class[node]:                            
                                sub_classes=dict_sub_group[group][sub_group][Class]
                                
                                #Case of only one sub class (entry as string) or the signal word "all"
                                if type(sub_classes)==str:                                                       
                                    if sub_classes==node_sub_class[node] or sub_classes=='all':    
                                        graph.add_node(node, node_sub_group=sub_group)
                                        grouped='Yes'
                                        break
                                        
                                #Case of more than one sub classes (entry as list)        
                                elif type(sub_classes)==list:
                                    for Subclass in sub_classes:
                                        if Subclass==node_sub_class[node]:
                                            graph.add_node(node, node_sub_group=sub_group)
                                            grouped='Yes'
                                            break
                                        
            #To break out of all loops except the last to start the next sorting                            
                            if grouped=='Yes':
                                break
                    if grouped=='Yes':
                        break
            if grouped=='Yes':
                break
        
        #If no sub group was found for the node (Requirement is that a potential sub group must exist)    
        if grouped=='No' and node_group[node] in dict_sub_group.keys():
            no_sub_group.append(node)                                        
    
    node_sub_group=nx.get_node_attributes(graph, 'node_sub_group')
    
    
    #ASSIGN AGITATORS TO VESSELS
    print('Assign agitators to connected equipment...')
    
    node_class=nx.get_node_attributes(graph, 'node_class')
    node_x=nx.get_node_attributes(graph, 'node_x')
    node_y=nx.get_node_attributes(graph, 'node_y')
    Position={} 
    Agitators=[]
    
    #Create new attribute for every node
    for node in graph.nodes():
        if node_sub_group[node]=='Vessel (liquid)':
            graph.add_node(node, node_agitator='No')                
        else:
            graph.add_node(node, node_agitator='not available')
        
    #Select agitators and vessels        
    for node in graph.nodes():
        if node_class[node]=='Agitator':
            Agitators.append(node)
            for other_node in graph.nodes():
                if node_group[other_node]=='Vessel':
                    
                    #Calculate distance by using coordinates
                    x_agitator=node_x[node]
                    x_other_node=node_x[other_node]
                    y_agitator=node_y[node]
                    y_other_node=node_y[other_node]
                    Position_difference=abs(x_agitator-x_other_node)+abs(y_agitator-y_other_node)#Calculate Position difference
                    Position[Position_difference]=other_node#save distance together with node
            
            #identificate nearest node to agitator and notice it in the attribute        
            node_assign=Position[min(Position.keys())]
            graph.add_node(node_assign, node_agitator='Yes')
    
    graph.remove_nodes_from(Agitators)
    
    
    #EXCHANGE FLANGE WITH THE ORIFICE PLATE
    
    node_class=nx.get_node_attributes(graph, 'node_class')
    node_name=nx.get_node_attributes(graph, 'node_name')
    node_x=nx.get_node_attributes(graph, 'node_x')
    node_y=nx.get_node_attributes(graph, 'node_y')
    Position={} 
    Orifice_plates=[]
    
    #Select orifice plates and flanges        
    for node in graph.nodes():
        if node_class[node]=='Orifice plate':
            Orifice_plates.append(node)
            for other_node in graph.nodes():
                if node_class[other_node]=='Flange':
                    
                    #calculate distance by using coordinates
                    x_flange=float(node_x[node])
                    x_other_node=float(node_x[other_node])
                    y_fange=float(node_y[node])
                    y_other_node=float(node_y[other_node])
                    Position_difference=abs(x_flange-x_other_node)+abs(y_fange-y_other_node)
                    Position[Position_difference]=other_node#save distance togehter with node
                           
            #identificate node with the smallest distance
            #reset the attributes
            #set the attributes of the orifice plate (Recent ID keeps the same until relabeling)
            node_assign=Position[min(Position.keys())]        
            graph.add_node(node_assign, node_ID='', node_name='', node_class='', node_sub_class='', node_x='', node_y='', node_group='', node_sub_group='')
            graph.add_node(node_assign, node_ID=node, node_name=node_name[node], node_class=node_class[node],  node_sub_class=node_sub_class[node], node_x=node_x[node], node_y=node_y[node], node_group=node_group[node], node_sub_group=node_sub_group[node])
    
    graph.remove_nodes_from(Orifice_plates)                       
    
    
    ############################################################################################################
    ############################### COMPLETED DEXPI DATA EXTRACTION ###############################################
    ############################################################################################################
    print('Extract complete DEXPI data...')
    
    #AVOID NO-LABEL NODES
    print('--> avoid no-label nodes')
     
    node_name=nx.get_node_attributes(graph, 'node_name')
    no_label_nodes=[]
    double_names=[]
    
    #Identificate no-label nodes and give them the ID as name
    for node in graph.nodes():
        if node_name[node]=='':
            node_name[node]=node
            no_label_nodes.append(node)  
    
    #Warning
    if no_label_nodes!=[]:
        Error_log.loc[k,'Warning']='Warning: At least one node is not labeled. Label of such a node was exchanged with ID of DEXPI-Export. To avoid it, please add a label for the node in the P&ID.'   
        Error_log.loc[k,'Node(s)']=str(no_label_nodes)
        k+=1
        
        
    #AVOID SAME NAME
    print('--> avoid same name')
    
    i=0
    
    #Identificate more time names
    for node_1 in graph.nodes():
        i+=1
        j=0
        for node_2 in graph.nodes():
            j+=1
            if node_name[node_1]==node_name[node_2] and i!=j and node_name[node_1] not in double_names:#avoid similarity because of same node and noticing a name for more than one time in the list
                double_names.append(node_1)
    
    #Identificate nodes with the more time names and give them consecutive numbers            
    for name in double_names:
        i=1           
        for node in graph.nodes():
            if node_name[node]==name:
                node_name[node]=name+' ('+str(i)+')'
                i+=1
    
    #Warning
    if double_names!=[]:
        Error_log.loc[k,'Warning']='At least one label is used more than one time. That is not possible cause a clear assignment must be given. For this run the nodes are numbered. For next run, please use clear label.'   
        Error_log.loc[k,'Node(s)']=str(double_names)
        k+=1  
              
    
    #RELABELING
    print('Relabeling...')
                  
    graph=nx.relabel_nodes(graph, node_name)
    
    node_name=nx.get_node_attributes(graph, 'node_name')
    node_class=nx.get_node_attributes(graph, 'node_class')
    node_sub_class=nx.get_node_attributes(graph, 'node_sub_class')
    node_group=nx.get_node_attributes(graph, 'node_group')
    node_sub_group=nx.get_node_attributes(graph, 'node_sub_group')
    node_ID=nx.get_node_attributes(graph, 'node_ID')
    
    
    
    #INVALID DRAWING (Example: Only inlets or outlets in valve)
    
    neighbors=[]
    all_neighbors=[]
    nodes_wrong_connection=[]
    
    #Notice in/out edges for every relevant nodes (except Vessel and MSR)
    for node in graph.nodes():
        if node_group[node]!='Vessel' and 'PIF' not in node_ID[node]:
            all_neighbors=list(nx.all_neighbors(graph, node))
            neighbors=list(nx.neighbors(graph, node))
            
            #every node with at least two edges and having only inlets or only outlets means invalid drawing and is noticed
            if len(all_neighbors)>1:#there must be more than one edge
                if len(neighbors)==0 or len(all_neighbors)-len(neighbors)==0:
                    nodes_wrong_connection.append(node)
    
    #Warning           
    if nodes_wrong_connection!=[]:
        Error_log.loc[k, 'Warning']='At least one node is wrong connected in the P&ID. Please check P&ID for the next run'
        Error_log.loc[k, 'Node(s)']=nodes_wrong_connection
        k+=1
 
###################################################################################################################
### CREATE A GRAPH WITHOUT MSR AND SAFETY EQUIPMENT ###############################################################    
###################################################################################################################

    graph_no_MSR=graph.copy()#copy graph
    print('create a 2nd graph without PCE and safety equipment...')
    
    #REMOVE SIGNAL LINES
    
    edge_class_MSR=nx.get_edge_attributes(graph_no_MSR, 'edge_class')
    
    edges=[]
    for edge in graph_no_MSR.edges():
        if edge_class_MSR[edge]=='Signal line':
            edges.append(edge)
            
    graph_no_MSR.remove_edges_from(edges)
    
    
    #REMOVE MSR AND CONNECTED VALVES
    
    list_MSR=[]
    list_MSR_valve=[]
    node_ID_MSR=nx.get_node_attributes(graph_no_MSR, 'node_ID')
    node_group_MSR=nx.get_node_attributes(graph_no_MSR, 'node_group')
    
    for node in graph_no_MSR.nodes():
        if 'PIF' in node_ID_MSR[node]:
            list_MSR.append(node)
            all_neighbors=list(nx.all_neighbors(graph_no_MSR, node)) 
            if len(all_neighbors)==1:
                node_neighbor=all_neighbors[0]
                all_neighbors=list(nx.all_neighbors(graph_no_MSR, node_neighbor)) 
                if len(all_neighbors)==2 and node_group_MSR[node_neighbor]=='Valves/Fittings':
                    list_MSR_valve.append(node_neighbor)
                      
    graph_no_MSR.remove_nodes_from(list_MSR)      
    graph_no_MSR.remove_nodes_from(list_MSR_valve)
    
################################################################################################################### 
    excel_ID_path=path_IDlist+savename+'.xlsx'   
    ID_list.to_excel(excel_ID_path) #save ID list
    Error_log.to_excel(path_errorLog+savename+'_ErrorLog.xlsx') #save Error_log   
    nx.write_graphml(graph, save_path_graph+savename+'.xml', encoding='utf-8', prettyprint=True, infer_numeric_types=False)#save the plot
    nx.write_graphml(graph_no_MSR, save_path_graph_no_MSR+savename+'_noMSR.xml', encoding='utf-8', prettyprint=True, infer_numeric_types=False)    
    
    print('Conversion and storing of the DEXPI file ', savename, 'completed!')
    
    return [graph, graph_no_MSR, k]  

                         