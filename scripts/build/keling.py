"""客岭古道桥梁；跨淳安、临安的桥梁只计一次。"""
ARTICLE = 'https://www.qdhnews.com.cn/content/content_9759225.html'
PLAN = 'https://zjjcmspublic.oss-cn-hangzhou-zwynet-d01-a.internet.cloud.zj.gov.cn/jcms_files/jcms1/web2241/site/attach/0/4d955e01f6bc4cb0b9f5b46a565f47c4.pdf'


def apply(rows):
    for dist,town,name,note in [
      ('淳安县','瑶山乡','云溪廊桥','客岭古道南端，俗称驮桥；据千岛湖新闻网报道，始建于明弘治年间，2010年重修'),
      ('临安区','湍口镇','海卜桥','千岛湖新闻网《客岭古道》称桥位于淳安、临安交界的岭坑口，记为明代；《临安印记（下）》列为清代，年代记载有异，待核；跨区桥暂在临安区计一次'),
    ]:
        matches=[r for r in rows if (r.get('dist'),r.get('town'),r.get('name'))==(dist,town,name)]
        assert len(matches)==1, (dist,town,name,len(matches))
        r=matches[0]
        if note not in (r.get('note') or ''): r['note']=(r.get('note')+'；' if r.get('note') else '')+note
        if ARTICLE not in r.setdefault('srcs',[]):r['srcs'].append(ARTICLE)
    additions=[
      dict(dist='淳安县',town='瑶山乡',name='里畈白佛桥',struct='石桥（两孔）',len='—',era='—',loc='岭后源村永安自然村，白佛殿后附近跨沈溪',level='杭州市历史建筑',doc='—',src=PLAN,srcs=[PLAN,ARTICLE],note='又名永安桥，俗称白佛桥；据《客岭古道》，位于客岭北麓，桥头原有白佛殿。瑶山单元详细规划将里畈白佛桥列为历史建筑，具体公布批次待核',commons=None),
      dict(dist='淳安县',town='瑶山乡',name='客岭古道双塆脚古石桥（暂称）',struct='石桥',len='—',era='—',loc='何家村客坑坞双塆脚附近，客岭古道起岭处',level='尚未定级（待核实）',doc='—',src=ARTICLE,srcs=[ARTICLE],note='《客岭古道》记过云溪桥沿客坑坞至双塆脚，靠右至古石桥开始起岭；桥名、形制、位置和保护等级待核，可能与文中概述的古道石拱桥为同一座',commons=None),
    ]
    # 同一份政府规划还逐项列出瑶山乡六座历史建筑桥梁。
    for name, loc in [
        ('张家村朱坑桥','张家村毛家坞口'),
        ('琅坑村三元桥','琅坑源村琅坑自然村东南面花栏坞口'),
        ('四联村回澜桥','琅坑源村四联自然村东北面'),
        ('四联村拱桥','琅坑源村四联自然村村头'),
        ('四联村柘树桥','琅坑源村四联自然村东面'),
        ('南川村村脚桥','琅坑源村南川自然村村脚'),
    ]:
        additions.append(dict(dist='淳安县',town='瑶山乡',name=name,struct='—',len='—',era='—',loc=loc,level='杭州市历史建筑',doc='—',src=PLAN,srcs=[PLAN],note='列入《杭州市淳安县瑶山单元（CA30）详细规划》历史建筑清单，具体公布批次待核',commons=None))
    for row in additions:
        if not any((r.get('dist'),r.get('town'),r.get('name'))==(row['dist'],row['town'],row['name']) for r in rows): rows.append(row)
    return rows
