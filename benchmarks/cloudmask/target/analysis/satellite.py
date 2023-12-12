#
# Authors:
#   Gregor von Laszewski
#   Ruochen Gu

import os
from datetime import datetime
from pprint import pprint

import eumdac
import h5py
import humanize
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from astral import LocationInfo
from astral.sun import sun

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile

import environment

class Sentinel:

    def __init__(self, data_dir=None):
        self.file_name = None
        self.file_info = None
        self.df = pd.DataFrame()
        if data_dir is None:
            try:
                self.DATA_DIR = os.environ.get("DATA_DIR")
            except KeyError:
                raise EnvironmentError("DATA_DIR not set")
        else:
            self.DATA_DIR = data_dir

    def credentials(self):
        def exists(filename):
            return os.path.exists(path_expand(filename))

        EDITOR = os.environ.get("EDITOR")

        print ("Checking Credentials")
        for filename in ["~/.esat/consumer-key", "~/.esat/consumer-secret"]:
            print("   ", filename, "exists", exists(filename))

        if not exists("~/.esat/consumer-key") or not exists("~/.esat/consumer-secret"):
            Shell.open("https://api.eumetsat.int/api-key/")
            # Shell.mkdir("~/.esat")
            for file_path in ["~/.esat/consumer-key", "~/.esat/consumer-secret"]:
                # writefile(file_path, '')
                print(f"Empty file created at: {file_path}")
                Shell.run(f"{EDITOR} {file_path}")
        else:
            print(f"The esat credentials already exist")

    def token(self):
        consumer_key = readfile(f"~/.esat/consumer-key").strip()
        consumer_secret = readfile(f"~/.esat/consumer-secret").strip()

        creds = (consumer_key, consumer_secret)

        _token = eumdac.AccessToken(creds)

        # pprint(_token.expiration)

        try:
            print(f"This token '{_token}' expires {_token.expiration}. ", end="")
            now = datetime.now()
            duration = now - _token.expiration
            print(f"This is in {humanize.naturaltime(duration)}.")
        except:
            print(f"Esat token error.")

        return _token


    @staticmethod
    def parse_file_name(file_name):
        components = [obj for obj in file_name.split('_') if obj != '']



        try:
            hdf = h5py.File(file_name, 'r')
        except:
            hdf = None

        if "/day/" in file_name:
            day = True
        elif "/night" in file_name:
            day = False
        else:
            day = None


        return {
            "filename": os.path.basename(file_name),
            "mission_id": components[0],
            "data_source": components[1],
            "processing_level": components[2],
            "data_type_id": components[3],
            "start_time": datetime.strptime(components[4], "%Y%m%dT%H%M%S"),
            "stop_time": datetime.strptime(components[5], "%Y%m%dT%H%M%S"),
            "creation_date": datetime.strptime(components[6], "%Y%m%dT%H%M%S"),
            "instance_id": components[7] + '_' + components[8] + '_' + components[9] + '_' + components[10],
            "center_id": components[11],
            "class_id": components[12] + '_' + components[13] + '_' + components[14].split('.')[0],
            "file_extension": components[14].split('.')[1],
            "hdf_file": hdf,
            "daylight": "day" if day else "night"
        }

    def add_files(self, file_names):
        data = []
        for counter, file_name in enumerate(file_names, start=1):
            print (counter, file_name)

            entry = Sentinel.parse_file_name(file_name)

            entry['counter'] = counter
            data.append(entry)

        df = pd.DataFrame(data)
        df['dt_m'] = (df['stop_time'] - df['start_time']).dt.total_seconds() / 60
        df = df[['counter',
                 'daylight',
                 'start_time',
                 'stop_time',
                 'dt_m'] + [col for col in df.columns if col not in ['counter',
                                                                     'daylight',
                                                                     'start_time',
                                                                     'stop_time',
                                                                     'dt_m']]]
        self.df = df
        return df

    @staticmethod
    def hdf_info(self):
        file = self.hdf_file
        print(file.keys())
        for key in file.keys():
            dset = file[key]
            print(key, "-->", dset.dtype, dset.shape)

    # not used
    @staticmethod
    def plot_gantt_chart(dataframe):
        # Sort DataFrame by start time for correct Gantt chart representation
        df = dataframe.sort_values(by=['start_time'])

        # Create Gantt chart
        fig = px.timeline(df,
                          x_start='start_time',
                          x_end='stop_time',
                          y='counter',
                          color='processing_level',
                          labels={'counter': 'counter',
                                  'mission_id': 'Mission ID',
                                  'start_time': 'Start Time',
                                  'stop_time': 'Stop Time'},
                          title='SLSTR Products Gantt Chart',
                          )

        # Add counter as the first element in the labels
        fig.update_layout(xaxis_title='Time',
                          yaxis_title='Counter',
                          showlegend=False)
        fig.update_traces(text=df.apply(lambda row: f"{row['counter']} - {row.name}", axis=1),
                          hoverinfo='text+y')

        # Show the chart
        fig.show()

    @staticmethod
    def plot_scatterplot(dataframe):
        # Sort DataFrame by start time for correct Gantt chart representation
        df = dataframe.sort_values(by=['start_time'])

        plt.figure(figsize=(16 * 5, 9 * 5))

        df.plot(kind='scatter', x='start_time', y='counter', label='Start Time', c='green', s=10)
        df.plot(kind='scatter', x='stop_time', y='counter', label='Stop Time', c='red', s=10, ax=plt.gca())

        plt.title('SLSTR Products Scatter Plot')
        plt.xlabel('Date & Time')
        plt.ylabel('Counter')
        plt.legend()

        # dtime = pd.date_range(start = '2019-10-01', end = '2019-10-31', freq = '10min')
        dtime = pd.date_range(start=df.iloc[0]['start_time'].strftime('%Y-%m-%d'),
                              end=df.iloc[-1]['stop_time'].strftime('%Y-%m-%d'), freq='10min')

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=3))
        plt.gca().xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        plt.setp(plt.gca().xaxis.get_majorticklabels(), rotation=45)
        plt.gca().set_xlim(dtime[0], dtime[-1])

        plt.show()

    def plot_satelite_matrix(self, sort_by_time=False, display_time_in_title=False, size=15, fontsize=15, x_offset=0,
                          y_offset=0, dx=100, counter_in_title=True):
        if sort_by_time:
            self.df = self.df.sort_values(by=['start_time'])

        fig, axs = plt.subplots(10, 10, figsize=(size, size))
        for i in range(100):
            dset = self.df.iloc[i]['hdf_file']['bayes']
            data = np.asarray(dset)
            row, col = divmod(i, 10)
            axs[row][col].imshow(data, cmap='gray')

            label = ""

            if counter_in_title:
                # time = self.df.iloc[i]['start_time'].strftime('%Y-%m-%d')[-2:]
                # time = self.df.iloc[i]['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                label = str(self.df.iloc[i]['counter'])
                axs[row][col].text(x_offset, y_offset, label, color='red', fontsize=fontsize)

            if display_time_in_title:
                # time = self.df.iloc[i]['start_time'].strftime('%Y-%m-%d')[-2:]
                # time = self.df.iloc[i]['start_time'].strftime('%Y-%m-%d %H:%M:%S')
                label = self.df.iloc[i]['start_time'].strftime('%d %H:%M:%S')
                axs[row][col].text(x_offset + dx, y_offset, label, color='blue', fontsize=fontsize)

                # axs[row][col].title.set_text(time)
                # axs[row][col].title.set_color('red')
                # axs[row][col].title.set_position([0.5, 10.0])

            axs[row][col].axis('off')

        plt.show()
        plt.savefig('images/matrix_plot.png', dpi=300)
        # plt.savefig('inference_image_matrix.png', dpi=500)
        return plt

    @staticmethod
    def is_daytime(latitude, longitude, starttime):

        # Getting the location information
        location = LocationInfo(latitude, longitude)

        # Calculating the sunrise and sunset times for the given date and location
        s = sun(location.observer, date=starttime)

        # Checking if the timestamp is between sunrise and sunset
        return s["sunrise"] < starttime < s["sunset"]

    def export_to_latex(self,
                        file_name='images/mask-table.tex',
                        selected_columns=['counter',
                                                'daylight',
                                                'start_time',
                                                'stop_time',
                                                'creation_date',
                                                'instance_id']):

        table = self.df[selected_columns].style.to_latex()
        table = table.replace("tabular", "longtable")
        writefile(file_name, table)
        return table

def get_filenames(directory_path):
    # List all items in the directory
    items = os.listdir(directory_path)

    # Filter out directories and get only filenames with absolute paths
    absolute_paths = [os.path.abspath(os.path.join(directory_path, item)) for item in items if os.path.isfile(os.path.join(directory_path, item))]

    return absolute_paths



sentinel = Sentinel()
sentinel.credentials()

DATA_DIR = environment.DATA_DIR

print ("DATA_DIR", DATA_DIR)


files = []


for directory in [f'{DATA_DIR}/ssts/day', f'{DATA_DIR}/ssts/night']:
     dir_files = get_filenames(directory)
     files = files + dir_files

pprint(files)

sentinel.add_files(files)

print(sentinel.df)

#

# Example usage with multiple file names
# file_names = [
#     "S3A_SL_2_LST____20151229T095534_20151229T114422_20160102T150019_6528_064_365______LN2_D_NT_001.SEN3",
#     "S3B_SL_1_RBT_BW_20160101T120000_20160101T130000_20160101T140000_GLOBAL___________LN2_R_NT_002.SEN3",
#     # Add more file names as needed
# ]


# Displaying the DataFrame
# print(df)

# Plotting Gantt chart using the class method
# SLSTRFileNameParser.plot_gantt_chart(df)

# Checking if timestamps are daytime using the class method
# latitude = 37.7749  # Replace with the latitude of the specific location
# longitude = -122.4194  # Replace with the longitude of the specific location

# Assuming you want to check daytime for the first file in the DataFrame
# print(f"{df.iloc[0]['filename']} is daytime: {SLSTRFileNameParser(df.iloc[0]['filename']).is_daytime(latitude, longitude)}")