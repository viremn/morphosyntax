'''
Mappings from prepositions and conjunctions to relation features.
Either arg-pred relation, i.e. case, or pred-pred relation, i.e. marker.
The final list should be updated according to the mapping done by Dan Zeman in this link: https://docs.google.com/spreadsheets/d/1--AkGor1-yQLv_BGnnXYQfekBQvMq7u7/edit?gid=1264268804#gid=1264268804
Whatever adposition or conjunction that can't be mapped to anything on the list, should appear as is as the value of the
relevant feature, transliterated to Latin letter if not already.
'''

case_feat_map = {
    '+': 'Conj',
    '-': 'Lat',
    '/': 'Dis',
    ':': 'The',
    
    'a': 'Dis',
    'all': 'Inc',
    'alltefter': 'Cnd', # Quo?
    'alltifrån': 'Add',
    'angående': 'The',
    'apropå': 'The',
    'av': 'Agt', # ?
    'bak': 'Pst',
    'bakom': 'Pst',
    'beroende': 'Cnd',
    'beträffande': 'The',
    'bland': 'Ces',
    'bortanför': 'Psl',
    'bortom': 'Psl',
    'bortsedd': 'Exc',
    'bredvid': 'Apu',
    'efter': 'Tps',
    'emellan': 'Int',
    'emot': 'Adv',
    'enl': 'Quo',
    'enligt': 'Quo',
    'exkl': 'Exc',
    'fastän': 'Ccs',
    'framemot': 'Tpx',
    'framför': 'Ant',
    'från': 'Abl',
    'från_och_med': 'Abl',
    'för': 'Ben',
    'förbi': 'Pst',
    'före': 'Tan',
    'förrän': 'Tan',
    'förutan': 'Add',
    'förutom': 'Add',
    'genom': 'Per',
    'gentemot': 'Lat',
    'gällande': 'The',
    'hos': 'Loc',
    'härifrån': 'Abl',
    'i': 'Ine',
    'ifråga': 'The',
    'ifrån': 'Ela',
    'igenom': 'Cau',
    'in': 'Ill',
    'inför': 'Ant',
    'inifrån': 'Ela',
    'inklusive': 'Inc',
    'innanför': 'Ine',
    'inom': 'Ine',
    'inpå': 'Apu',
    'intill': 'Apu',
    'inåt': 'Inx',
    'istället': 'Sbs',
    'jämförd': '',
    'jämte': 'Com',
    'kontra': 'Adv',
    'kring': 'Cir',
    'liksom': 'Sem',
    'likt': 'Sem',
    'längs': 'Lng',
    'med': 'Com',
    'medan': 'Cmt',
    'mellan': 'Int',
    'mot': 'Adv',
    'nedanför': 'Sub',
    'nedför': 'Dsc',
    'nedom': 'Sub',
    'när': 'Cnd',
    'nära': 'Prx',
    'oavsett': 'Ign',
    'oberoende': '',
    'om': 'The', # Dis, Cir
    'omkring': 'Cir',
    'ovan': 'Sup',
    'ovanför': 'Sup',
    'ovanpå': 'Sup',
    'per': 'Dis',
    'plus': 'Inc',
    'på': 'Ade',
    'runt': 'Cir',
    'runtomkring': 'Cir',
    'rörande': 'The',
    'sedan': 'Teg',
    'sen': 'Teg',
    'senast': 'Lim',
    'som': 'Rpl',
    'tack': 'Cau',
    'till': 'Lat',
    'till_och_med': 'Lat',
    'tills': 'Ttr',
    'trots': 'Ccs',
    'tvärsigenom': 'Crs',
    'tvärsöver': 'Crs',
    'tvärtemot': 'Dsm',
    'undan': 'Abl',
    'under': 'Sub',
    'uppför': 'Asc',
    'uppåt': 'Asc',
    'ur': 'Ela',
    'utan': 'Abe',
    'utanför': 'Ext',
    'utanpå': 'Ade',
    'utefter': 'Lng',
    'utför': 'Dsc',
    'utifrån': 'Exe',
    'utmed': 'Lng',
    'utom': 'Ext', # Add
    'utåt': 'Ext',
    'utöver': 'Add',
    'vad': '',
    'via': 'Pro',
    'vid': 'Loc',
    'à': 'Dis',
    'än': 'Cmp',
    'å': 'Ben', # The
    'åt': 'Ben',
    'över': 'Spx',
    
    '–': '',
    'fara': '',
    'den': '',
    'de': '',
    'from': '',
    'over': '',
    'of': '',
    'to': '',
    'for': '',
    'De': '',
    'I': '',
    'In': '',
    'Of': '',
    'On': '',
}
case_feat_map = {k: v if v else k for k,v in case_feat_map.items()}




marker_feat_map = {
    'all': 'Inc',
    'allt': 'Inc',
    'alltefter': 'Cnd', 
    'allteftersom': 'Cnd',
    'antingen': '',
    'att': '',
    'av': 'Gen', # ?
    'bakom': 'Pst',
    'beroende': 'Cnd',
    'bortsedd': 'Exc',
    'där': 'Loc',
    'därför': 'Cau',
    'däri': 'Ine',
    'därigenom': 'Ins',
    'då': 'Tps', # Cau
    'efter': 'Pst', # 
    'eftersom': 'Cau',
    'ehuruväl': 'Ccs', # Concessive?
    'emedan': 'Cau',
    'emot': 'Adv',
    'fast': 'Ccs',
    'fastän': 'Ccs',
    'från': 'Abl', 
    'för': 'Pur',
    'förrän': 'Tan',
    'förutom': 'Exc',
    'förutsatt': 'Cnd',
    'genom': 'Ins', # Per
    'hur': '',
    'huruvida': '',
    'i': '',
    'ifall': '',
    'ifråga': '',
    'ifrån': '',
    'innan': '',
    'inte': '',
    'liksom': '',
    'med': '',
    'medan': '',
    'mellan': '',
    'mot': '',
    'när': '',
    'oavsedd': '',
    'oavsett': '',
    'oberoende': '',
    'om': '',
    'på': '',
    'samtidig': '',
    'samtidigt': '',
    'sedan': '',
    'snart': '',
    'som': '',
    'så': '',
    'såsom': '',
    'såvida': '',
    'såvitt': '',
    'till': '',
    'tills': '',
    'trots': '',
    'under': '',
    'uppå': '',
    'utan': '',
    'utom': '',
    'utöver': '',
    'vad': '',
    'var': '',
    'vare': '',
    'varför': '',
    'varigenom': '',
    'vart': '',
    'vid': '',
    'where': '',
    'än': '',
    'även': '',
    'åt': '',
    'över': '',

    'If': '',
}
marker_feat_map = {k: v if v else k for k,v in marker_feat_map.items()}

conjtype_feat_map = {


}

conjtype_feat_map = {k: v if v else k for k,v in conjtype_feat_map.items()}

if __name__ == '__main__':
    print(set(case_feat_map.keys()))
    print(set(conjtype_feat_map.keys()))
    print(set(marker_feat_map.keys()))
    print(set(case_feat_map.keys()) & set(conjtype_feat_map.keys()))
    print(set(case_feat_map.keys()) & set(marker_feat_map.keys()))
    print(set(conjtype_feat_map.keys()) & set(marker_feat_map.keys()))

