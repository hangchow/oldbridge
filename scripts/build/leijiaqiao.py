"""雷家桥纳入古纤道记录，不再单独统计。"""
ARTICLE='https://mp.weixin.qq.com/s/h6jN9bar1KS1yqiSRhC7sw'
PLAN='https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web149/site/attach/0/4454e18d84fe412390efc00be64ee79b.pdf'
REPORT='https://news.sohu.com/20090402/n263176217.shtml'

def apply(rows):
    rows = [r for r in rows if (r.get('dist'), r.get('town'), r.get('name')) != ('临平区', '东湖街道', '雷家桥')]
    if not any((r.get('dist'),r.get('town'),r.get('name'))==('临平区','东湖街道','雷家桥古纤道') for r in rows):
        rows.append(dict(dist='临平区',town='东湖街道',name='雷家桥古纤道',struct='古纤道（石砌）',len='70米',era='清末民国初',loc='姚家埭村顺风路794号，京杭大运河与造桥港交汇处',level='杭州市文物保护单位（第五批）',doc='—',src=ARTICLE,srcs=[ARTICLE,PLAN,REPORT],commons=None,note='古纤道长70米；纤道上的雷家桥为单孔石梁桥，桥长11.3米、宽1.95米、跨度6.5米，已并入本条记录'))
    return rows
