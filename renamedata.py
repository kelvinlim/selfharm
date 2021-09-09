#! /usr/bin/env python
# read the data

import os
import pandas as pd
import glob
import argparse
from sklearn.preprocessing import StandardScaler

class RenameData:
    
    """
    class to rename columns of dataframes to be compatble with R
    
    """
    def __init__(self, index=[0,None], nostd=False,
                 mdir = '.'):
        
        
        self.args = {
            'dataorig': 'dataorig' ,
            'datanew': 'data',
            'mdir': mdir
            }
    

        self.no_std = nostd        
        self.work( index=index)
          
 
    def rename_columns(self, df):
        
        # create a dict for renaming 
        
        renames = {}
        
        for colname in df.columns:
            if '-' in colname:  # check if invalid character is present
                renames[colname] = colname.replace('-', '.', 10)
            
        
        newdf = df.rename(columns=renames)

        return newdf
    

        
    def standardize_df_col(self, diag=False):
        """
        standardize the columns in the dataframe
        https://machinelearningmastery.com/normalize-standardize-machine-learning-data-weka/
        
        * get the column names for the dataframe
        * convert the dataframe into into just a numeric array
        * scale the data
        * convert array back to a df
        * add back the column names
        * set to the previous df
        """
        
        # describe original data - first two columns
        if diag:
            print(self.newdf.iloc[:,0:2].describe())
        # get column names
        colnames = self.newdf.columns
        # convert dataframe to array
        data = self.newdf.values
        # standardize the data
        data = StandardScaler().fit_transform(data)
        # convert array back to df, use original colnames
        self.newdf = pd.DataFrame(data, columns = colnames)
        # describe new data - first two columns
        if diag:
            print(self.newdf.iloc[:,0:2].describe())
        
        
    def work(self, drop_columns='', index=[0,None]):
        # get the csv files from the data directory
    
        self.files = glob.glob(os.path.join(
            self.args['mdir'], self.args['dataorig'], "*.csv"))
        self.files.sort()
        

        
        for file in self.files[index[0]:index[1]]:
            print(file)
            # read in the data
            dforig = pd.read_csv(file)
            # remove na rows
            dforig.dropna(inplace=True)
            
            # only process files if min number of entries
            if len(dforig) >=24:
                
                # rename columns
                self.newdf = self.rename_columns(dforig)
                       
                # standardize ?
                if not self.no_std:
                    self.standardize_df_col()
                
    
                newfilepath = os.path.join(
                    self.args['mdir'],self.args['datanew'], 
                    os.path.basename(file))
                self.newdf.to_csv(newfilepath, index=False)
            
    
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="rename columns in csv files making them R compatible, \
            also standardizes the data to mean of 0 and stdev of 1"
    )
    parser.add_argument("--start", type = int,
                        help="beginning file list index , default 0",
                        default = 0)
    parser.add_argument("--end", type = str,
                        help="end file list index, default None",
                        default=None)
    parser.add_argument("--mdir", type = str,
                     help="main directory, default is the current directory",
                     default='.')   
    parser.add_argument("--nostd", help="do not standardize the columns",
                     action = "store_true")
    parser.add_argument("--list", help="TODO - list the files to be processed",
                        action = "store_true")

    args = parser.parse_args()

    # setup default values
    if args.end != None:
        args.end = int(args.end)
 
    #c = RenameData(drop_columns='90') # to drop 90%
    #c = RenameData(drop_columns='') # keep all columns; do all files
    c = RenameData( 
                    index=[args.start,args.end], nostd=args.nostd,
                    mdir = args.mdir)



