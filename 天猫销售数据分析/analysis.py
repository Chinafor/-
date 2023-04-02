import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map, Bar, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from pyecharts.faker import Faker
from snapshot_selenium import snapshot
from pyecharts.render import make_snapshot
data = pd.read_csv('./tmall_order_report.csv')
#print(data.head())
#print(data.info())
data.columns = data.columns.str.strip()# 列名有空格，需要处理下
#print(data.columns)
#print(data[data.duplicated()].count())#检查重复值
#print(data.isnull().sum())
data['收货地址'] = data['收货地址'].str.replace('自治区|维吾尔|回族|壮族|省', '')  # 对省份做个清洗，便于可视化
#print(data['收货地址'].unique())
#print(data['收货地址'].nunique())
#数据分析可视化
result = {}
result['总订单数'] = data['订单编号'].count()  
result['已完成订单数'] = data['订单编号'][data['订单付款时间'].notnull()].count()  
result['未付款订单数'] = data['订单编号'][data['订单付款时间'].isnull()].count()  
result['退款订单数'] = data['订单编号'][data['退款金额'] > 0].count()  
result['总订单金额'] = data['总金额'][data['订单付款时间'].notnull()].sum()  
result['总退款金额'] = data['退款金额'][data['订单付款时间'].notnull()].sum()  
result['总实际收入金额'] = data['买家实际支付金额'][data['订单付款时间'].notnull()].sum()

#构建表格 1.整体情况
table = Table()

headers = ['总订单数', '总订单金额', '已完成订单数', '总实际收入金额', '退款订单数', '总退款金额', '成交率', '退货率']
rows = [
    [
        result['总订单数'], f"{result['总订单金额']/10000:.2f} 万", result['已完成订单数'], f"{result['总实际收入金额']/10000:.2f} 万",
        result['退款订单数'], f"{result['总退款金额']/10000:.2f} 万", 
        f"{result['已完成订单数']/result['总订单数']:.2%}",
        f"{result['退款订单数']/result['已完成订单数']:.2%}",
    ]
]
table.add(headers, rows)
table.set_global_opts(
    title_opts=ComponentTitleOpts(title='整体情况')
)
table.render_notebook()
table.render('1.1整体情况.html')
#make_snapshot(snapshot, table.render(), "11.png")
#print(table)
#print('****')

#构建表格 2.地区分析
result2 = data[data['订单付款时间'].notnull()].groupby('收货地址').agg({'订单编号':'count'})
result21 = result2.to_dict()['订单编号']
result22=[['上海市',3060],['云南省',667],['内蒙古自治区',176],['北京市',1853],['吉林省',336],['四川省',1752],['天津市',1031],['宁夏回族自治区',40],['安徽省',528],['山东省',1484],['山西省',395],['广东省',2022],['广西壮族自治区',353],['新疆维吾尔自治区',43],['江苏省',1845],['江西省',331],['河北省',885],['河南省',792],['浙江省',1822],['海南省',156],['湖北省',57],['湖南省',935],['甘肃省',132],['福建省',425],['西藏自治区',2],['贵州省',286],['辽宁省',1012],['重庆市',896],['陕西省',441],['青海省',18],['黑龙江省',312]]
c = (
    Map()
    .add(series_name="订单量", data_pair=result22, maptype="china", is_map_symbol_show=True)
    .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    .set_global_opts(
        title_opts=opts.TitleOpts(title='地区分布'),
        visualmap_opts=opts.VisualMapOpts(max_=1000),            
    )
)
c.render_notebook()
c.render('1.2地区分析.html')
#make_snapshot(snapshot, c.render(), "Pyecharts生成图片.png")
print('******')

print(type(result21))
print('******')
#构建表格 3.时间分析
data['订单创建时间'] = pd.to_datetime(data['订单创建时间'])
data['订单付款时间'] = pd.to_datetime(data['订单付款时间'])
result31 = data.groupby(data['订单创建时间'].apply(lambda x: x.strftime("%Y-%m-%d"))).agg({'订单编号':'count'}).to_dict()['订单编号']
c1 = (
    Line()
    .add_xaxis(list(result31.keys()))
    .add_yaxis("订单量", list(result31.values()))
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
            ]
        ),
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="每日订单量走势"))
)
c1.render_notebook()
c1.render('1.3时间分析.html')
#每小时订单走势
result32 = data.groupby(data['订单创建时间'].apply(lambda x: x.strftime("%H"))).agg({'订单编号':'count'}).to_dict()['订单编号']
x = [*result32.keys()]
y = [*result32.values()]
c = (
    Bar()
    .add_xaxis(x)
    .add_yaxis("订单量", y)
    .set_global_opts(title_opts=opts.TitleOpts(title="每小时订单量走势"))
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="峰值"),
                opts.MarkPointItem(name="第二峰值", coord=[x[15], y[15]], value=y[15]),
                opts.MarkPointItem(name="第三峰值", coord=[x[10], y[10]], value=y[10]),
            ]
        ),
    )
)
c.render_notebook()
c.render('1.4每小时订单.html')
#平均时间
s = data['订单付款时间'] - data['订单创建时间']
s[s.notnull()].apply(lambda x: x.seconds / 60 ).mean()  # 从下单到付款的平均耗时为 7.7 分钟