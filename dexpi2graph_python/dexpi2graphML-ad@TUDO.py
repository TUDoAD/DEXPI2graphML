import PySimpleGUI as psg
import os
from PIL import Image, ImageTk
import functions
import subprocess
import lxml
import pandas as pd

#psg.theme('Default')

# Define window content
col_left = [[psg.Text("Choose DEXPI - P&ID - folder...")],
          [psg.Input(key='path_dexpi'), psg.FolderBrowse()],
          [psg.Text("Processing Information / Console...")],
          [psg.Output(size=(60,30), key='_output_')],
          [psg.Button('Convert'), psg.Button('show graphML P&ID in Explorer'), psg.Button('show Plot in Explorer')],
          ]

image_elem =psg.Image(size=(600, 450), key='plot_graph', visible=True, background_color ='white')
list_elem = psg.Listbox(os.listdir('./Output/graphs_plots'), key='selected_plot', size=(50,5))

col_right =[[psg.Text('Plot')] ,
          [image_elem],
          [list_elem],
          [psg.Button('P&ID-graph Plot'), psg.Button('show graphML'), psg.Button('show Error Log')]]

col_bottom = [[psg.Image('./GUI_figs/AD_Logo_EN_600dpi_gui.png')],
          [psg.Text(' CC: Technische Universität Dortmund, AG Apparatedesign \n Author: Jonas Oeing')]]

layout = [[psg.Column(col_left), psg.Column(col_right, element_justification='c')],
          [ psg.Column(col_bottom)]]


# create window
window = psg.Window('dexpi2graph - ad@TUDO', layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    list_elem.update(os.listdir('./Output/graphs_plots')) 
    if event == 'Convert':
        
        if values['path_dexpi']=='':
            psg.popup('Enter path of the DEXPI folder!')
            
        else:
            print('open directory:', values['path_dexpi'])
            print('Start conversion of DEXPI files into graphML...')
            
            for file in os.listdir(values['path_dexpi']):
                savename=file[:-4]
                functions.Dexpi2graph(values['path_dexpi']+'/'+file, './Output/graphs_graphml/complete/', './Output/graphs_graphml/noPCE/', './Output/NodeLists/', './Output/errorLog/', savename)
                functions.plot_graph2('./Output/graphs_graphml/complete/'+file, './Output/graphs_plots/'+savename)    
        list_elem.update(os.listdir('./Output/graphs_plots'))    
            
    ### Kasten auswahl einfügen
    if event == 'show graphML P&ID in Explorer':
        Application = os.getcwd()
        Application = 'explorer "'+Application+'\Output\graphs_graphml\complete"'
        subprocess.Popen(Application) 
    
    if event == 'P&ID-graph Plot': 
        if values['selected_plot']==[]:
            psg.popup('Choose a P&ID-graph!')
            
        else:
            img = Image.open('./Output/graphs_plots/'+values['selected_plot'][0])
            img.thumbnail((600, 500))
            image_elem.update(data=ImageTk.PhotoImage(img), size=(600, 450))
        
    if event == 'show Plot in Explorer':
        Application = os.getcwd()
        Application = 'explorer "'+Application+'\Output\graphs_plots"'
        subprocess.Popen(Application) 
    
    if event == 'show graphML':
        if values['selected_plot']==[]:
            psg.popup('Choose a P&ID-graph!')
            
        else:
            window.FindElement('_output_').Update('')
            file = values['selected_plot'][0][:-4]
            xml_file = './Output/graphs_graphml/complete/'+file+'.xml'
            tree = lxml.etree.parse(xml_file)
            pretty = lxml.etree.tostring(tree, encoding="unicode", pretty_print=True)
            print(pretty)
            
    if event == 'show Error Log':
        if values['selected_plot']==[]:
            psg.popup('Choose a P&ID-graph!')
            
        else:
            window.FindElement('_output_').Update('')
            file = values['selected_plot'][0][:-4]
            error_file = './Output/errorLog/'+file+'_ErrorLog.xlsx'
            error_df = pd.read_excel(error_file)
            for i in range(0, len(error_df)):
                print(error_df['Warning'][i])
                print(error_df['Node(s)'][i])
                print('\n')
            

    # See if user wants to quit or window was closed
    if event == psg.WINDOW_CLOSED:
        break
    # Output a message to the window
    