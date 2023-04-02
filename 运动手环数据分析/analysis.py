import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pygal
from pygal.style import *
from pygal.maps import *
#设置pygal与jupyter notebook交互
from IPython.display import display, HTML
base_html = """
<!DOCTYPE html>
<html>
  <head>
  <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/svg.jquery.js"></script>
  <script type="text/javascript" src="https://kozea.github.io/pygal.js/2.0.x/pygal-tooltips.min.js""></script>
  </head>
  <body>
    <figure>
      {rendered_chart}
    </figure>
  </body>
</html>
"""

data = pd.read_csv('./dailyActivity_merged.csv')
#print(data.head())
print('*****')
#print(data.isnull().sum())
#print(data.info())
#更改数据类型
data["ActivityDate"] = pd.to_datetime(data["ActivityDate"], format="%m/%d/%Y")
#添加汇总字段
data["TotalMinutes"] = data["VeryActiveMinutes"] + data["FairlyActiveMinutes"] + data["LightlyActiveMinutes"] + data["SedentaryMinutes"]
#print(data["TotalMinutes"].sample(5))
#添加Day记录星期几
data["Day"] = data["ActivityDate"].dt.day_name()
#print(data["Day"].head())
#描述性统计数据
#print(data.describe())
#1每日总步数和消耗的卡路里之间的联系
figure = px.scatter(data_frame = data, x="Calories",
                    y="TotalSteps", size="VeryActiveMinutes", 
                    trendline="ols", 
                    title="总步数和消耗的卡路里的关系")
#figure.show()
#plotly.offline.plot(figure, filename='./lifeExp.html')
figure.write_html("1每日总步数和消耗的卡路里之间的联系.html")
#2每日总路程和消耗的卡路里之间的联系
figure = px.scatter(data_frame = data.dropna(), x="Calories",
                    y="TotalDistance", size="VeryActiveMinutes", 
                    trendline="lowess", color='TotalSteps',
                    title="总路程和消耗的卡路里的关系")
#figure.show()
figure.write_html("2每日总路程和消耗的卡路里之间的联系.html")
#3总活动时间
label = ["Very Active Minutes", "Fairly Active Minutes", "Lightly Active Minutes", "Inactive Minutes"]
counts = data[["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]].mean()
colors = ["gold","lightgreen", "pink", "blue"]
fig = go.Figure(data=[go.Pie(labels=label, values=counts)])
fig.update_layout(title_text="总活动时间")
fig.update_traces(hoverinfo="label+percent", textinfo="value", textfont_size=24, marker=dict(colors=colors, line=dict(color="black", width=5)))
#fig.show()
fig.write_html("3总活动时间.html")
#4一周每天不同的活跃时间
d = data.groupby('Day')['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes'].sum().reset_index()
Bar_Chart = pygal.Bar(
    width=800,   #宽度
    height=600,   #高度
    print_values=True,
    print_labels=True,
    print_values_position='top',
    print_labels_position='bottom',
    x_title='星期',
    y_title='',
    legend_at_bottom=True,       #是否显示图例
    style=DefaultStyle
) 
Bar_Chart.title = ' 一周中每天不同活跃程度活动时间 ' 
Bar_Chart.x_labels = d['Day'].tolist()
Bar_Chart.add('Very Active', d["VeryActiveMinutes"].tolist()) 
Bar_Chart.add('Fairly Active', d["FairlyActiveMinutes"].tolist()) 
Bar_Chart.add('Lightly Active', d["LightlyActiveMinutes"].tolist()) 
HTML(base_html.format(rendered_chart=Bar_Chart.render(is_unicode=True)))#图片渲染
Bar_Chart.render_to_file('4一周每天不同的活跃时间.svg')
#5一周中每一天的非活动分钟数
day = data["Day"].value_counts()
label = day.index
counts = data["SedentaryMinutes"]
colors = ['gold', 'lightgreen', "pink", "blue", "skyblue", "cyan", "orange"]
fig = go.Figure(data=[go.Pie(labels=label, values=counts)])
fig.update_layout(title_text='每一天的非活动分钟数')
fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30,
                  marker=dict(colors=colors, line=dict(color='black', width=3)))
#fig.show()
fig.write_html("5一周中每一天的非活动分钟数.html")
#6每一天燃烧的卡路里数
calories = data["Day"].value_counts()
label = calories.index
counts = data["Calories"]
colors = ['gold','lightgreen', "pink", "blue", "skyblue", "cyan", "orange"]
fig = go.Figure(data=[go.Pie(labels=label, values=counts)])
fig.update_layout(title_text='每一天燃烧的卡路里数')
fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=30, marker=dict(colors=colors, line=dict(color='black', width=3)))
#fig.show()
fig.write_html("6每一天燃烧的卡路里数.html")
#7每日步数
box_plot = pygal.Box()
box_plot.title = '每日步数'
weeks = ["Monday",  "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for we in weeks:

    box_plot.add(we, data[data["Day"] == we]["TotalSteps"].tolist())

HTML(base_html.format(rendered_chart=box_plot.render(is_unicode=True)))#图片渲染
box_plot.render_to_file('7每日步数.svg')

