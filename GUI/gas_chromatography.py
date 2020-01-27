'''
Name: gas_chromatography.py
Authors: Conor Green and Matt McPartlan
Description: Highest abstraction of GC GUI interface. Will be initially called from bash upon startup of Raspberry Pi.
Usage: Call as main
Version:
1.0 - 26 January 2020 - Initial creation. Skeleton to outline work for later
'''

import numpy as np

class Gas_Chrom(wx.Frame):

    def __init__(self):



    def main(self):
        pass

class Current_Data:

    def __init__(self):
        self.test_number = 0

        self.default_num_data_pts = 50

        default_values = np.zeros(self.default_num_data_pts)
        self.data = default_values

    def run_test(self):
        self.test_number += 1




if __name__ == '__main__':
    main()
