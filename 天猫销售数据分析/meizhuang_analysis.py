import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map, Bar, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from pyecharts.faker import Faker
from snapshot_selenium import snapshot
from pyecharts.render import make_snapshot
from pyecharts.charts import Map, Timeline, Bar, Line, Pie
data2 = pd.read_csv('./双十一淘宝美妆数据.csv')
#print(data2.head())
#print(data2.info())
#print(data2[data2.duplicated()].count())#86条重复数据
data2.drop_duplicates(inplace=True)   # 删除重复数据
data2.reset_index(drop=True, inplace=True)  # 重建索引
print('*****')
#print(data2.isnull().sum())  # 查看空值 ，销售数量和评论数有空值

data2.fillna(0, inplace=True) # 空值填充
data2['update_time'] = pd.to_datetime(data2['update_time']).apply(lambda x: x.strftime("%Y-%m-%d")) # 日期格式化，便于统计
#print(data2[data2['sale_count']>0].sort_values(by=['sale_count']).head())

data2['sale_amount'] = data2['price'] * data2['sale_count']  # 增加一列销售额
#print(data2[data2['sale_count']>0].sort_values(by=['sale_count']))
print('*****')
#2.1每日整体销量走势
result = data2.groupby('update_time').agg({'sale_count':'sum'}).to_dict()['sale_count']
c = (
    Line()
    .add_xaxis(list(result.keys()))
    .add_yaxis("销售量", list(result.values()))
    .set_series_opts(
        areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
                opts.MarkPointItem(type_="average", name="平均值"),
            ]
        ),
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="每日整体销售量走势"))
)
c.render_notebook()
c.render('2.1每日整体销量走势.html')
#2.2品牌销量比较
dts = list(data2['update_time'].unique())
dts.reverse()
tl = Timeline()
tl.add_schema(
#         is_auto_play=True,
        is_loop_play=False,
        play_interval=500,
    )
for dt in dts:
    item = data2[data2['update_time'] <= dt].groupby('店名').agg({'sale_count': 'sum', 'sale_amount': 'sum'}).sort_values(by='sale_count', ascending=False)[:10].sort_values(by='sale_count').to_dict()
    bar = (
        Bar()
        .add_xaxis([*item['sale_count'].keys()])
        .add_yaxis("销售量", [round(val/10000,2) for val in item['sale_count'].values()], label_opts=opts.LabelOpts(position="right", formatter='{@[1]/} 万'))
        .add_yaxis("销售额", [round(val/10000/10000,2) for val in item['sale_amount'].values()], label_opts=opts.LabelOpts(position="right", formatter='{@[1]/} 亿元'))
        .reversal_axis()
        .set_global_opts(
            title_opts=opts.TitleOpts("累计销售量排行 TOP10")
        )
    )
    tl.add(bar, dt)
tl.render_notebook()
tl.render('2.2品牌销量比较柱状图.html')
#2.3饼状图
item = data2.groupby('店名').agg({'sale_count': 'sum'}).sort_values(by='sale_count', ascending=False)[:10].to_dict()['sale_count']
item = {k: round(v/10000, 2) for k, v in item.items()}
c = (
    Pie()
    .add("销量", [*item.items()])
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} 万({d}%)"))
)
c.render_notebook()
c.render('2.3品牌销量比较饼状图.html')
#2.4化妆品价格比较
item = data2.groupby('店名').agg({'price': 'mean'}).sort_values(by='price', ascending=False)[:20].sort_values(by='price').to_dict()
c = (
    Bar()
    .add_xaxis([*item['price'].keys()])
    .add_yaxis("销售量", [round(v, 2) for v in item['price'].values()], label_opts=opts.LabelOpts(position="right"))
    .reversal_axis()
    .set_global_opts(
        title_opts=opts.TitleOpts("平均价格排行 TOP20")
    )
)
c.render_notebook()
c.render('2.4化妆品价格比较.html')
