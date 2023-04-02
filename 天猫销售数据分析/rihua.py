import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map, Bar, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from pyecharts.faker import Faker
from snapshot_selenium import snapshot
from pyecharts.render import make_snapshot
from pyecharts.charts import Map, Timeline, Bar, Line, Pie
fact_order = pd.read_excel('./日化.xlsx', sheet_name='销售订单表')
dim_product = pd.read_excel('./日化.xlsx', sheet_name='商品信息表')
#print(fact_order)
#print(dim_product)

#print(dim_product.head())
#print(dim_product.describe())#分析核心统计变量均值方差等
#print(dim_product[dim_product.duplicated()].count())  # 没有完全重复的数据
#print(dim_product[dim_product['商品编号'].duplicated()].count())  # ID 唯一没有重复
#print(dim_product.isnull().sum())
fact_order.drop_duplicates(inplace=True)   # 删除重复数据
fact_order.reset_index(drop=True, inplace=True)  # 重建索引
print('*****')
#print(fact_order.isnull().sum())  # 查看空值，有几条数据缺失
fact_order.fillna(method='bfill', inplace=True) # 空值填充
fact_order.fillna(method='ffill', inplace=True) # 空值填充
#print(fact_order.isnull().sum())
print('*****')
fact_order['订单日期'] = fact_order['订单日期'].apply(lambda x: pd.to_datetime(x, format='%Y#%m#%d') if isinstance(x, str) else x)
#print(fact_order[fact_order['订单日期'] > '2021-01-01']) # 有一条脏数据 2050年
fact_order = fact_order[fact_order['订单日期'] < '2021-01-01'] # 过滤掉脏数据
#print(fact_order['订单日期'].max(), fact_order['订单日期'].min())  # 数据区间在 2019-01-01 到 2019-09-30 之间
fact_order['订购数量'] = fact_order['订购数量'].apply(lambda x: x.strip('个') if isinstance(x, str) else x).astype('int')
fact_order['订购单价'] = fact_order['订购单价'].apply(lambda x: x.strip('元') if isinstance(x, str) else x).astype('float')
fact_order['金额'] = fact_order['金额'].astype('float')
#print(fact_order.info())

fact_order['所在省份'] = fact_order['所在省份'].str.replace('自治区|维吾尔|回族|壮族|省|市', '')  # 对省份做个清洗，便于可视化
#fact_order['所在省份'].unique()
fact_order['客户编码'] = fact_order['客户编码'].str.replace('编号', '')
#3.1每月订购情况
from pyecharts import options as opts
from pyecharts.charts import Map, Bar, Line
from pyecharts.components import Table
from pyecharts.options import ComponentTitleOpts
from pyecharts.faker import Faker

fact_order['订单月份'] = fact_order['订单日期'].apply(lambda x: x.month) 
item = fact_order.groupby('订单月份').agg({'订购数量': 'sum', '金额': 'sum'}).to_dict()
x = [f'{key} 月' for key in item['订购数量'].keys()]
y1 = [round(val/10000, 2) for val in item['订购数量'].values()]
y2 = [round(val/10000/10000, 2) for val in item['金额'].values()]
c = (
    Bar()
    .add_xaxis(x)
    .add_yaxis("订购数量（万件）", y1, is_selected=False)
    .add_yaxis("金额（亿元）", y2)
    .set_global_opts(title_opts=opts.TitleOpts(title="每月订购情况"))
    .set_series_opts(
        label_opts=opts.LabelOpts(is_show=True),
    )
)
c.render_notebook()
c.render('3.1每月订购情况.html')
#3.2哪里的人最爱美
item = fact_order.groupby('所在地市').agg({'订购数量': 'sum'}).sort_values(by='订购数量', ascending=False)[:20].sort_values(by='订购数量').to_dict()['订购数量']

c = (
    Bar()
    .add_xaxis([*item.keys()])
    .add_yaxis("订购量", [round(v/10000, 2) for v in item.values()], label_opts=opts.LabelOpts(position="right", formatter='{@[1]/} 万'))
    .reversal_axis()
    .set_global_opts(
        title_opts=opts.TitleOpts("订购数量排行 TOP20")
    )
)
c.render_notebook()
c.render('3.2哪里的人最爱美.html')
#3.3 什么类型的美妆需求量最大
order = pd.merge(fact_order, dim_product, on='商品编号',how='inner')  # 表关联
#print(order.groupby(['商品大类','商品小类']).agg({'订购数量': 'sum'}).sort_values(by=['商品大类', '订购数量'], ascending=[True, False]))
#3.4哪些省份的美妆需求量最大
item = fact_order.groupby('所在省份').agg({'订购数量': 'sum'}).to_dict()['订购数量']
c = (
    Map()
    .add("订购数量", [*item.items()], "china", is_map_symbol_show=False)
    .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
    .set_global_opts(
        title_opts=opts.TitleOpts(title='省份分布'),
        visualmap_opts=opts.VisualMapOpts(max_=1000000),            
    )
)
c.render_notebook()
c.render('3.4哪些省份的美妆需求量最大.html')
#3.5 通过 RFM 模型挖掘客户价值
#RFM 模型是衡量客户价值和客户创利能力的重要工具和手段，其中由3个要素构成了数据分析最好的指标，分别是：R-Recency（最近一次购买时间）F-Frequency（消费频率）M-Money（消费金额）
#设定一个计算权重，比如 R-Recency 20% F-Frequency 30% M-Money 50% ，最后通过这个权重进行打分，量化客户价值，后续还可以基于分数进一步打标签，用来指导二次营销的策略。
data_rfm = fact_order.groupby('客户编码').agg({'订单日期': 'max', '订单编码': 'count', '金额': 'sum'})
data_rfm.columns = ['最近一次购买时间', '消费频率', '消费金额']
data_rfm['R'] = data_rfm['最近一次购买时间'].rank(pct=True)   # 转化为排名 百分比，便于后续切片
data_rfm['F'] = data_rfm['消费频率'].rank(pct=True)
data_rfm['M'] = data_rfm['消费金额'].rank(pct=True)
data_rfm.sort_values(by='R', ascending=False)  
data_rfm['score'] = data_rfm['R'] * 20 + data_rfm['F'] * 30 + data_rfm['M'] * 50
data_rfm['score'] = data_rfm['score'].round(1)
print(data_rfm.sort_values(by='score', ascending=False))#表格结果
