"""根据《临安印记（下）》补充古道和遗址中记载的桥。"""
SOURCE = '../../../文保名录/杭州市/临安印记（下）桥梁相关页.pdf'


def apply(rows):
    # 《临安印记》将下列七座列为马啸段沿途尚存建筑；单桥位置、年代待核。
    for name in ('大成永安桥', '涂家永安桥', '马啸坑口桥', '大石门桥', '银龙桥', '宝善桥', '阳山象形桥'):
        add(rows, '清凉峰镇', name, '—', '—', '—',
            '原马啸乡杭徽古道马啸段，大成村至浙川村沿线；具体位置待核',
            '据《临安印记（下）》第230页，列入当时沿线保存的清至民国时期建筑；单桥年代、现状及与其他记录是否重复待核')
    add(rows, '岛石镇', '龙泉庵遗址东石拱桥（暂称）', '石拱桥（单孔）', '5米', '—',
        '山川村新川自然村南部佛堂山，龙泉庵遗址东30米',
        '据《临安印记（下）》第233页，桥宽3米、净跨3.6米、矢高3.2米，专为香客进庵上香而建；原名、年代和现状待核')
    add(rows, '昌化镇', '昌化县桥渡木桥遗址（暂称）', '木桥', '约100米', '清同治十二年（1873）碑记',
        '东街村南门弄，昌化溪北岸，原桥南北向跨昌化溪',
        '据《临安印记（下）》第234页，书中称木桥及船渡码头遗址，桥渡碑记载1873年修建经过；桥体是否仍存待核，不能以书中历史长度推定现状')
    add(rows, '岛石镇', '柳岭古道北凉亭石梁桥（暂称）', '石梁桥', '2米', '—',
        '岛石村下塔自然村通往原新桥乡柳川村的柳岭古道，北凉亭前10米',
        '据《临安印记（下）》第233页，桥宽1.5米，净跨1至1.4米；原名、年代和现状待核')
    add(rows, '潜川镇', '沈洪古道扁担山脚石拱桥（暂称）', '石拱桥（单孔）', '—', '清（古道年代，桥待核）',
        '沈家坞村西南沈洪古道扁担山脚',
        '据《临安印记（下）》第236页，为古道同期修筑；原名、现状待核')
    add(rows, '天目山镇', '百丈岭古驿道石拱桥（暂称）', '石拱桥（单孔）', '—', '清',
        '原藻溪镇藻溪村藻溪自然村百丈岭脚古驿道',
        '据《临安印记（下）》第236页，书中称清代建筑、调查时尚存；原名和现状待核')
    # 纠正上次录入时对书中桥名的误读。
    for r in rows:
        if r['dist']=='临安区' and r['town']=='板桥镇' and r['name'] in ('紫坞坞石拱桥','紫块坞石拱桥'): r['name']='紫垅坞石拱桥'
    # 同书独立条目明确了古道桥名，不重复计数。
    rows[:] = [r for r in rows if not (r['dist']=='临安区' and (r['town'], r['name']) in {('河桥镇','曹家石拱桥'), ('潜川镇','白石岩石拱桥')})]
    for town, old, new in [('潜川镇','沈洪古道扁担山脚石拱桥（暂称）','扁担山脚石拱桥'), ('天目山镇','百丈岭古驿道石拱桥（暂称）','百丈岭脚石拱桥')]:
        r = next((r for r in rows if r['dist']=='临安区' and r['town']==town and r['name']==old), None)
        if r:
            target = next((x for x in rows if x['dist']=='临安区' and x['town']==town and x['name']==new), None)
            if target: rows.remove(r)
            else:
                r['name'] = new
                r['note'] = r.get('note','').replace('原名、现状待核', '现状待核').replace('原名和现状待核', '现状待核')
    for r in rows:
        if r.get('dist') == '临安区' and SOURCE in r.get('srcs', []):
            r['note'] = (r.get('note') or '').replace('按三普调查实录独立条目归入一般不可移动文物；正式登记名单、现状和后续等级变化待核', '按《临安印记（下）》独立条目归入一般不可移动文物，名录及调查资料截至2009年9月30日；现状和此后保护等级变化待核')
    from linan_xia_data import BRIDGES
    for town, name, struct, length, era, loc, page in BRIDGES:
        match_name = {'盛村坞石拱桥':'夏村村盛村自然村坞石拱桥', '曹家石拱桥':'曹家村石拱桥', '童婆桥':'双塔村童婆桥', '里王家永庆桥':'里王家村永久桥', '白石岩石拱桥':'鱼潭村石拱桥'}.get(name, name)
        hits = [r for r in rows if r['dist']=='临安区' and r['town']==town and r['name']==match_name]
        note = f'形制、尺寸等据《临安印记（下）》第{page}页，现状以书中调查时期为准'
        if name == '白石岩石拱桥': note += '；书中称白石岩石拱桥，位置与鱼潭村石拱桥一致，暂按同桥处理'
        if name == '三珠桥': note += '；与同村历史建筑挺生桥是否为同一桥待核'
        if name == '里王家永庆桥': note += '；书名为里王家永庆桥，与历史建筑档案的里王家村永久桥位置、长度及纪年一致，暂按同桥处理，名称差异待核'
        if name == '梁成桥': note += '；书中为单孔石拱桥，而既有资料称双孔石梁桥，记载不一致待核'
        if name == '董家石梁桥': note += '；书中标题及照片为石梁桥，正文误写石拱桥，结构待核'
        if name == '紫垅坞石拱桥': note += '；桥名第二字扫描不清，字形待核'
        if name == '寿宁桥':
            note += '；书中记桥长2.8米、净跨4米，数据相互矛盾，长度待核'
            length = '—'
        if hits:
            assert len(hits)==1, (town, name, len(hits))
            r = hits[0]
            if name == '宝善桥': r.update(era=era, loc=loc)
            if name == '金笠庵石拱桥': r['loc']=loc
            for key, value in [('struct',struct), ('len',length)]:
                if r.get(key) in (None, '', '—'): r[key] = value
            if note not in (r.get('note') or ''): r['note'] = (r.get('note')+'；' if r.get('note') else '') + note
            if SOURCE not in r.setdefault('srcs', []): r['srcs'].append(SOURCE)
        else:
            add(rows, town, name, struct, length, era, loc, note)
            r = next(r for r in rows if r['dist']=='临安区' and r['town']==town and r['name']==name)
        # 独立条目来自不可移动文物调查实录；已有更高保护级别或四普等级不变。
        if (r.get('level') or '').startswith('尚未定级'):
            r['level'] = '一般不可移动文物（三普调查实录）'
            basis = '按《临安印记（下）》独立条目归入一般不可移动文物，名录及调查资料截至2009年9月30日；现状和此后保护等级变化待核'
            if basis not in (r.get('note') or ''):
                r['note'] = (r.get('note')+'；' if r.get('note') else '') + basis
    # 古道概述与独立条目均载涂家永安桥。
    r = next(r for r in rows if r['dist']=='临安区' and r['town']=='清凉峰镇' and r['name']=='涂家永安桥')
    r.update(struct='石拱桥（单孔）', len='5.5米', era='清同治十一年（1872）碑记', loc='原马啸乡湖门村山边自然村东南部涂家，古川公路转弯处')
    if (r.get('level') or '').startswith('尚未定级'):
        r['level']='一般不可移动文物（三普调查实录）'
        r['note'] += '；按《临安印记（下）》独立条目归入一般不可移动文物，名录及调查资料截至2009年9月30日；现状和此后保护等级变化待核'
    extra = '第350页另有独立条目，桥宽3米；书中碑记日期与具体建桥年份的关系待核'
    if extra not in r['note']: r['note'] += '；' + extra
    r = next(r for r in rows if r['dist']=='临安区' and r['town']=='潜川镇' and r['name']=='仙人桥')
    if r.get('struct') in (None, '', '—'): r['struct']='石梁桥（单孔）'
    for town, name, note in [
        ('潜川镇', '仙人桥', '《临安印记（下）》第232页记白龙寺遗址内有五座石拱桥及一座石梁平桥，并引县志记仙人桥；与现存档案中仙人桥及其他桥的对应关系待核，不据此重复计数'),
        ('河桥镇', '石室寺南石拱桥', '《临安印记（下）》第230页记石室寺前100米有一石拱桥；与石室寺南、北石拱桥是否对应尚待核实'),
    ]:
        hits = [r for r in rows if r['dist']=='临安区' and r['town']==town and r['name']==name]
        assert len(hits)==1, (town, name, len(hits))
        row = hits[0]
        if note not in (row.get('note') or ''):
            row['note'] = (row.get('note')+'；' if row.get('note') else '') + note
        if SOURCE not in row.setdefault('srcs', []): row['srcs'].append(SOURCE)
    return rows


def add(rows, town, name, struct, length, era, loc, note):
    if any(r['dist']=='临安区' and r['town']==town and r['name']==name for r in rows): return
    rows.append(dict(dist='临安区', town=town, name=name, struct=struct, len=length,
                     era=era, loc=loc, level='尚未定级（待核实）', doc='—',
                     src=SOURCE, srcs=[SOURCE], commons=None, note=note))
