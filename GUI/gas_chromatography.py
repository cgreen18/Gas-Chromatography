'''
Name: gas_chromatography.py
Authors: Conor Green and Matt McPartlan
Description: Highest abstraction of GC GUI interface. Will be initially called from bash upon startup of Raspberry Pi.
Usage: Call as main
Version:
1.0 - 26 January 2020 - Initial creation. Skeleton to outline work for later
1.1 20 February 2020 - Import and create gc_class Gas_Chrom object.
'''



import wx

import gc_class as gc

class Gas_Chromatography(wx.Frame):

    def __init__(self):
        my_gc = gc.Gas_Chrom()


    def main(self):
        pass


if __name__ == '__main__':
    main()
