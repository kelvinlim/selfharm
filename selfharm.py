#! /usr/bin/env python3

import os
import pandas as pd
import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import math

class SelfHarm:
    
    """
 
    
     mort_df.columns
     Index(['HCScode', 'HCS10code', 'WithCNdata', 'TRcode', 'Matchingpaire',
            'Onset_Dx', 'ex_nonsuicide_death', 'New_mortality3vs7years',
            'mortality_3_7years', 'SS_YR_12', 'Mort_12', 'New_timeyr12',
            'time_yr12', 'time_yr', 'Suicide_12', 'Suicide', 'Mortality', 'Gender',
            'EI_SC', 'YoB', 'Age', 'Ageat1stpre', 'Age_AoD', 'Date_1stpre',
            'Time_mth', 'CGI_death', 'COMP_death', 'Aff_death', 'Neg_death',
            'IPOP_1mth_death', 'Med_death', 'Relapse_death', 'Hosp_death',
            'No_SS_death', 'SA_HX_death', 'Clozapine', 'age_onset', 'SS_type',
            'Cause_death', 'Details_death', 'Location_death', 'LoD', 'CoD',
            'CoD_12', 'Relapse_3yr', 'Hosp_3yr', 'SA_HX_3yr', 'Yrs_edu_B',
            'No_SS_3yr', 'Clozapine_3yr', 'Default_death', 'DUP', 'DUP_log',
            'DUP_days', 'DUP_SS', 'DUP_SS_ct', 'M1_Pos', 'M1_Neg', 'M1_Aff',
            'Compliance_mean', 'M1pre_ss', 'M36_SS_ct', 'EP1_hosp', 'adm1_date',
            'dc1_date', 'dur_adm1', 'Total_default_mth_3Y', 'default_hist_3Y',
            'Occup_impair', 'Last_dc_date', 'DoD', 'Dur_dc_death', 'filter_$',
            'twoG_Dx', 'ddd_36mth_mean', 'NEWtwo_group_dx', 'Four_grDx', 'E_case',
            'Match_G', 'match_id'],
           dtype='object')
     
     
     
    """
    
    def __init__(self, verbosity=0, mdir='.', orig='dataorig'):
        
        
        self.verbosity = verbosity
        self.mdir = mdir
        self.orig  = orig
        
        pd.set_option('display.max_rows', None)
        
        mortalityf = 'Mortality SPSS_Matched1234.sav'
        baselinef = 'baseline_Mortality_new.sav'

        print("Loading data - this may take a moment...")
        self.mort_df = pd.read_spss(mortalityf)
        self.base_df = pd.read_spss(baselinef)
        print("Data loaded")
        
        self.pivot_data_write()
        
        pass

    def pivot_data_write(self):
        # pivot data and write into individual files
        # convert to a list of dicts
        self.base = self.base_df.to_dict('records')
        
        items = 'Poscf Negcf Aff SOFAScf dsh compliance'.split(' ')
        
        
        id = 1  # initialize id counter
        for row in self.base[0:None]:
            
            # create dictionary of lists to hold the data
            self.data = {}
            for item in items:
                self.data[item] = []
    
            for item in items:
                for mnum in range(1,31):
                    
                    colname = f"M{mnum}_{item}"
    
                    # append data to corresponding list
                    self.data[item].append(row[colname])
                    
                    if self.verbosity==2:
                        print(colname, ":", row[colname])
            
            # convert categorical to numeric
            self.convert_compliance()
            self.convert_aff()
            
            # create the dataframe
            df = pd.DataFrame(self.data)
            
            # create the filename
            fname = f"sub_{id:04d}.csv"
            if self.verbosity == 0:
                print(fname)
            fp = os.path.join(self.mdir, self.orig, fname)
            # write out dataframe to csv
            df.to_csv(fp, index=False)
            # increment id counter
            id += 1
                    

       
        pass

        
    def pivot_data(self):
        # convert to a list of dicts
        self.base = self.base_df.to_dict('records')
        
        items = 'Poscf Negcf Aff SOFAScf dsh compliance'.split(' ')
        
        # create dictionary of lists to hold the data
        self.data = {}
        for item in items:
            self.data[item] = []
        # create a column to contain the id
        self.data['id'] = []
        
        id = 1  # initialize id counter
        for row in self.base[0:None]:

            for item in items:
                for mnum in range(1,31):
                    # load the id for this subject
                    self.data['id'].append(id)
                    
                    colname = f"M{mnum}_{item}"

                    # append data to corresponding list
                    self.data[item].append(row[colname])
                    
                    if self.verbosity==2:
                        print(colname, ":", row[colname])
                        
            # increment id counter
            id += 1
                    
        self.convert_compliance()
        self.convert_aff()
       
        pass
                    
                
    
    def convert_compliance(self):
        """
        convert from categorical to number
        self.base_df['M1_compliance'].unique()
        
        poor - 0
        fair - 1
        good - 2
        
        """
        for i in range(len(self.data['compliance'])):
            values = self.data['compliance']
            
            currval = values[i]
            
            if currval == 'Poor':
                self.data['compliance'][i] = 0.0
            elif currval == 'Fair':
                self.data['compliance'][i] = 1.0
            elif currval == 'Good':
                self.data['compliance'][i] = 2.0
                    
    def convert_aff(self):
        """
        convert from categorical to number
        self.base_df['M1_Aff'].unique()
        
        Categories (6, object): ['Borderline', 'Markedly ill', 
                                 'Mildly ill', 'Moderately ill', 
                                 'Normal',
                                 'Severly ill']
        
        Borderline
        Markedly ill 
                                 
        Mildly ill
        Moderately ill
                                 
        Normal
        Severly ill
        """
        
        #TODO dictionary to hold values
        remap = {
            'Normal': 0,    
            'Borderline': 1 , 
            'Mildly ill': 2, 
            'Moderately ill': 3, 
            'Markedly ill': 4, 
            'Severly ill': 5                                 
        }
        
        for i in range(len(self.data['Aff'])):
            values = self.data['Aff']
            
            currval = values[i]
            
            # check that it is a string before converting
            if type(currval) == str:
                self.data['Aff'][i] =remap[currval]

                
        
        
    def get_df_columns(self):
        # write out the columns for the dataframes
        mortCols = self.mort_df.columns.to_list()
        fp = open('mortcols.json','w')
        json.dump(mortCols, fp, indent = 4)
        fp.close()
        
        # base
        baseCols = self.base_df.columns.to_list()
        fp = open('basecols.json','w')
        json.dump(baseCols, fp, indent = 4 )
        fp.close()
        
 
    def get_activity_info(self):
        # get the activity data suitable for plotting as a df
        
        """
        
        
        to get at stress measurements self.activity[1]['allDayStress']
        
        len(self.activity[1]['allDayStress']['aggregatorList'])
        
        [{'type': 'TOTAL', 'averageStressLevel': 31, 'averageStressLevelIntensity': 22, 'maxStressLevel': 92, 'stressIntensityCount': 1086, 'stressLevelCount': 0, 'stressOffWristCount': 119, 'stressTooActiveCount': 223, 'totalStressCount': 1428, 'totalStressIntensity': 15737, 'totalStressLevel': 0, 'stressDuration': 34980, 'restDuration': 30180, 'activityDuration': 13380, 'uncategorizedDuration': 7140, 'totalDuration': 85680, 'lowDuration': 18420, 'mediumDuration': 13920, 'highDuration': 2640}, {'type': 'AWAKE', 'averageStressLevel': 46, 'averageStressLevelIntensity': 41, 'maxStressLevel': 92, 'stressIntensityCount': 631, 'stressLevelCount': 0, 'stressOffWristCount': 86, 'stressTooActiveCount': 221, 'totalStressCount': 938, 'totalStressIntensity': -14097, 'totalStressLevel': 0, 'stressDuration': 32220, 'restDuration': 5640, 'activityDuration': 13260, 'uncategorizedDuration': 5160, 'totalDuration': 56280, 'lowDuration': 15720, 'mediumDuration': 13860, 'highDuration': 2640}, {'type': 'ASLEEP', 'averageStressLevel': 9, 'averageStressLevelIntensity': 9, 'maxStressLevel': 60, 'stressIntensityCount': 455, 'stressLevelCount': 0, 'stressOffWristCount': 33, 'stressTooActiveCount': 2, 'totalStressCount': 490, 'totalStressIntensity': 29834, 'totalStressLevel': 0, 'stressDuration': 2760, 'restDuration': 24540, 'activityDuration': 120, 'uncategorizedDuration': 1980, 'totalDuration': 29400, 'lowDuration': 2700, 'mediumDuration': 60, 'highDuration': 0}]
        
        """
        
        items = [             
            'totalSteps', 
            'vigorousIntensityMinutes',
            'floorsAscendedInMeters',
            'minHeartRate',
            'maxHeartRate',
            'currentDayRestingHeartRate',            
        ]
        
    def plot_sleep(self):
        # https://jakevdp.github.io/PythonDataScienceHandbook/04.00-introduction-to-matplotlib.html#Two-Interfaces-for-the-Price-of-One
        # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
        
        """
        ['sleepStartTimestampGMT', 'sleepEndTimestampGMT', 'calendarDate',
               'sleepWindowConfirmationType', 'retro', 'deepSleepSeconds',
               'lightSleepSeconds', 'remSleepSeconds', 'awakeSleepSeconds',
               'unmeasurableSeconds', 'spo2SleepSummary'],
              dtype='object')
        """

        x = range(len(self.sleep_df))
        
        fig, (sl,hr,climb, steps) = plt.subplots(4)
        
        # set figure size
        fig.set_size_inches(6,10)
        
        deep =  self.sleep_df['deepSleepSeconds']/60.0
        light = self.sleep_df['lightSleepSeconds']/60.0
        rem = self.sleep_df['remSleepSeconds']/60.0
        awake = self.sleep_df['awakeSleepSeconds']/60.0
        
        tst = deep + light + rem
        tib = tst + awake
        
        sl.set_ylabel('Sleep(minutes)')
        sl.plot(x,deep)
        sl.plot(x, light)
        sl.plot(x, rem )
        sl.plot(x, awake)
        sl.plot(x,tst)
        sl.plot(x,tib)
        sl.legend(['Deep','Light','REM','Awake','TST','TIB'])

        hr.set_ylabel('HeartRate')
        hr.plot(x, self.act_df['minHeartRate'])
        hr.plot(x, self.act_df['maxHeartRate'])
        hr.plot(x, self.act_df['currentDayRestingHeartRate'])
        hr.legend(['Min','Max','Rest'])

        climb.set_ylabel('Meters Climbed')
        climb.plot(x, self.act_df['floorsAscendedInMeters'])
        
        steps.set_ylabel('Steps')
        steps.plot(x, self.act_df['totalSteps'])
        steps.set_xlabel('Days')

        #plt.show()
        plt.savefig('garmin.png', dpi=100)

    def plot_test(self):
        # https://jakevdp.github.io/PythonDataScienceHandbook/04.00-introduction-to-matplotlib.html#Two-Interfaces-for-the-Price-of-One
        # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
        
        x = np.linspace(0, 2 * np.pi, 400)
        y = np.sin(x ** 2)
        
        fig, axs = plt.subplots(2)
        axs[0].plot(x, y)
        axs[1].plot(x, -y)
        plt.show()
        
    def get_sleep_info(self):
        """
        first row only has 5 columns instead of 11 so skip this
        
        key spo2SleepSummary, accesses another dictionary
        {'userProfilePk': 7940344, 'deviceId': 3363313947, 'sleepMeasurementStartGMT': '2021-06-18T05:02:00.0', 'sleepMeasurementEndGMT': '2021-06-18T08:56:00.0', 'alertThresholdValue': 0, 'averageSPO2': 88.0, 'averageHR': 60.0, 'lowestSPO2': 80}

        'averageSPO2': 88.0, 'averageHR': 60.0, 'lowestSPO2': 80
        
        Also need to get the info sleepStartTimestampGMT, sleepEndTimestampGMT
        
        Returns
        -------
        None.

        """
        items = [
            ''
            
            ]
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="plot sample garmin data for grant"
    )
    parser.add_argument("--start", type = int,
                        help="beginning file list index , default 1",
                        default = 1)
    parser.add_argument("--end", type = str,
                        help="end file list index, default 29",
                        default=29)
    parser.add_argument("--list", help="TODO - list the files to be processed",
                        action = "store_true")
    
    args = parser.parse_args()
    
    # setup default values
    if args.end != None:
        args.end = int(args.end)
    
    c = SelfHarm()
    
    
"""


"""

