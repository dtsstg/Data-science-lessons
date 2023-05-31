import urllib3
import pandas
from spyre import server
import matplotlib

local_id_to_global_id = {1:22,2:24,3:23,4:25,5:3,6:4,7:8,8:19,9:20,10:21,11:9,12:None,13:10,14:11,15:12,
                        16:13,17:14,18:15,19:16,20:None,21:17,22:18,23:6,24:1,25:2,26:7,27:5}
province_id_to_name = {1:'Вінницька',2:'Волинська',3:'Дніпропетровська',4:'Донецька',5:'Житомирська',
                       6:'Закарпатська',7:'Запорізька',8:'Івано-Франківська',9:'Київська',10:'Кіровоградська',
                      11:'Луганська',12:'Львівська',13:'Миколаївська',14:'Одеська',15:'Полтавська',
                       16:'Рівенська',17:'Сумська',18:'Тернопільська',19:'Харківська',20:'Херсонська',
                      21:'Хмельницька',22:'Черкаська',23:'Чернівецька',24:'Чернігівська',25:'Республіка Крим'}

province_options = []
column_selection_options = [dict(label = 'VCI',value = 'VCI'),dict(label = 'TCI',value = 'TCI'),dict(label = 'VHI',value = 'VHI')]
for i in province_id_to_name.keys():
    province_options.append(dict(label = province_id_to_name[i],value = i))

class App(server.App):
    title = "LAB1"

    inputs = [dict(type='dropdown',
                key='province',
                label='Select province',
                options = province_options,
                action_id='update'),
              dict(type='dropdown',
                   key='column',
                   label='Select column',
                   options=column_selection_options,
                   action_id='update'),
              dict(type='text',
                   key='range',
                   label='Select weeks range',
                   value = '9-10',
                   action_id='update')
              ]
    controls = [{"type": "hidden",
                 "id": "update"}]

    tabs = ["Plot", "Table"]

    outputs = [{"type": "plot",
                "id": "plot",
                "control_id": "update",
                "tab": "Plot"},
               {"type": "table",
                "id": "table_id",
                "control_id": "update",
                "tab": "Table",
                "on_page_load": True}]

    def getData(self,params):
        province_id = params['province']
        column = params['column']
        week_range = params['range']
        min_week = int(week_range.split('-')[0])
        max_week = int(week_range.split('-')[1])

        http = urllib3.PoolManager()
        url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={}&year1=1981&year2=2023&type=Mean".format(
            province_id)
        vhi_data = http.request('GET', url, preload_content=False).read().decode('ascii')

        headers = ['Year', 'Week', ' SMN', 'SMT', 'VCI', 'TCI', 'VHI']
        lines = vhi_data.split('\n')
        lines.pop(0)
        lines.pop(0)
        lines[0] = lines[0][9:]
        lines.pop(-1)
        raw = []
        for i in lines:
            raw.append(i.split(',')[:-1])
        df = pandas.DataFrame(raw, columns=headers)
        df = df.astype({"Year": "int", "Week": "int", ' SMN': "float", 'SMT': "float", 'VCI': "float", 'TCI': "float",
                        'VHI': "float"})
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df = df.drop(df.loc[df['VCI'] == -1].index)
        df = df.drop(df.loc[df['TCI'] == -1].index)

        df = df[['Year','Week',column]]
        df = df[df['Week'] >= min_week]
        df = df[df['Week'] <= max_week]
        return df

    def getPlot(self,params):
        province_id = params['province']
        column = params['column']
        week_range = params['range']

        df = self.getData(params).set_index('Year').drop(['Week'],axis=1)
        plt_obj = df.plot()
        plt_obj.set_ylabel(column)
        name = column + " at week range " + week_range + " in "+ province_id_to_name[int(province_id)]
        plt_obj.set_title(name)
        fig = plt_obj.get_figure()
        return fig




app = App()
app.launch()

