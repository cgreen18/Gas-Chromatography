'''
Name: gas_chromatography.py
Authors: Conor Green and Matt McPartlan
Description: Highest abstraction of GC GUI interface. Will be initially called from bash upon startup of Raspberry Pi.
Usage: Call as main
Version:
1.0 - 26 January 2020 - Initial creation. Skeleton to outline work for later
1.1 - 20 February 2020 - Import and create gc_class Gas_Chrom object.
1.2 - 30 March 2020 - Complete overhaul. Utilizes frame and panel classes created in gc_gui and smashes them together using the SplitterWindow.
1.3 - 30 March 2020 - Added Save As window that navigates directories and updates listbox.
1.4 - 31 March 2020 - Added Open window, similar to Save As. Both inherit new window class.
2.0 - 21 April 2020 - Final version. Moved all code to gc_gui.py...
                        and made this a simple App running script.
3.0 - 24 April 2020 - Same as 2.0. Updated version to match gc_class and gc_gui
4.0 - 27 April 2020 - Manually configure serial string constants. Serial integer constants are set normally through yaml file.
'''

import wx
import yaml
import os

import gc_gui

'''
self - MainApp object
param: self.parent - the parent wxPython object, in this case None (main call of MainApp(None))
attribute: self.options - the UI defeaults and current settings loaded from YAML config file
'''
class MainApp(gc_gui.GCFrame):
    def __init__(self, parent):
        self.__version__ = '3.0'
        self.__authors__ = 'Conor Green and Matt McPartlan'
        
        print('\n\n\n\n--------------------------------------------------------------------')
        print('Running gas_chromatography.py')
        print('Press ctrl+c to terminate.')
        print('Messages and errors printed below.')

        with open('config.yaml') as f:
            options = yaml.load(f, Loader=yaml.FullLoader)
            self.options = options

        # dont have time to figure out in yaml
        _dict = {'READ_TMP_CMD_STR' :'001 000 000 000' , 'SET_TMP_CMD_STR': '000 XXX XXX 000'}
        self.options.update(_dict)

        gc_gui.GCFrame.__init__(self, parent, self.options)

def main():
    app = wx.App()
    window = MainApp(None) #GCFrame
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
