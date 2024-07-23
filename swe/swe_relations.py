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
    'alltefter': 'Cau', # Quo?
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

    'jämförd': 'Cmp',
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
    'oberoende': 'Ign',
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
    
    'via': 'Pro',
    'vid': 'Loc',

    'à': 'Dis',

    'än': 'Cmp',

    'å': 'Ade', 
    'åt': 'Ben',

    'över': 'Spx',

    'på grund av': 'Cau',
    
    'vid sida av': 'Apu',
    'med hjälp av': 'Ins',
    'till följd av': 'Cau',
    'i och med': 'Cau',
    'i form av': 'Sem',
    'i ställe för': 'Sbs',
    'i motsats till': 'Dsm',
    'för sedan': 'Tem',
    'i förhållande till': 'Cmp',
    'till skillnad från': 'Dsm',
    'i linje med': 'Rpl',
    
    '–': '',
    'fara': '',
    'den': '',
    'de': '',
    'vad': '',

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
case_feat_map = {k: (v if v else k) for k,v in case_feat_map.items()}

marker_feat_map = {
    'all': 'Inc',
    'allt': 'Inc',
    'alltefter': 'Cau', 
    'allteftersom': 'Cau',
    'antingen': 'Disj',
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
    
    'i': 'Ine',
    'ifall': 'Cnd',
    'ifråga': 'The',
    'ifrån': 'Abl',
    'innan': 'Tan',

    'liksom': 'Sem',

    'med': 'Com',
    'medan': 'Add',
    'mellan': 'Int',
    'mot': 'Adv',

    'när': 'Tem',

    'oavsedd': 'Ign',
    'oavsett': 'Ign',
    'oberoende': 'Ign',
    'om': 'The', # Cnd

    'på': 'Ade', # beror på, bevis på, 

    'samtidig': 'Dur', # Com
    'samtidigt': 'Dur', # Com

    'sedan': 'Tps', 
    'snart': 'Tps',
    'som': 'Rpl', # Sem, Equ
    'så': 'Pur',
    'såsom': 'Sem',
    'såvida': 'Cnd',
    'såvitt': 'Cnd',

    'till': 'Lat',
    'tills': 'Ttr',
    'trots': 'Ign',
    
    'under': 'Cnd', # Under förutsättningen
    'uppå': 'Ade',
    'utan': 'Abe',
    'utom': 'Exc',
    'utöver': 'Add',
    
    'var': 'Loc',
    'vare': 'Disj',
    'varför': 'Cau',
    'varigenom': 'Cau',
    'vart': 'Lat',
    'vid': 'Apu',
    
    'än': 'Cmp',
    'även': 'Add',
    
    'åt': 'Ori',
    
    'över': 'The', # Funderar över, Glädjas över

    'för att': 'Cau',
    'som om': 'Rpl',
    'allt eftersom': 'Cau',
    'till dess': 'Ttr',
    'så att': 'Pur',
    'efter att': 'Tps',
    'även om': 'Ccs',
    'trotts att': 'Ccs',

    'att': '',
    'hur': '',
    'huruvida': '',
    'vad': '',
    'inte': '', # Vet inte om denna bör vara mark??
    'where': '',
    'If': '',
}
marker_feat_map = {k: (v if v else k) for k,v in marker_feat_map.items()}

conjtype_feat_map = {
    '&': 'Conj',
    '+': 'Conj',
    '-': '',
    '/': 'Disj',
    'a': '',
    'antingen': 'Disj',
    'både': 'Conj',
    'det_vill_säga': '',
    'el': 'Disj',
    'eller': 'Disj',
    'fast': 'Advs',
    'fastän': 'Advs',
    'för': 'Reas',
    'liksom': 'Sem',
    'mellan': 'Int',
    'men': 'Advs',
    'och': 'Conj',
    'plus': 'Conj',
    'respektive': 'Conj',
    'samt': 'Conj',
    'som': 'Conj',
    'så': 'Cnsq',
    'såväl': 'Conj',
    'ty': 'Reas',
    'utan': 'Advs',
    'utom': 'Advs',
    'vare': 'Disj',
    'varken': 'Nnor',

    'and': '',
    'And': '',

}

conjtype_feat_map = {k: (v if v else k) for k,v in conjtype_feat_map.items()}

if __name__ == '__main__':
    print(set(case_feat_map.keys()))
    print(set(conjtype_feat_map.keys()))
    print(set(marker_feat_map.keys()))
    print(set(case_feat_map.keys()) & set(conjtype_feat_map.keys()))
    print(set(case_feat_map.keys()) & set(marker_feat_map.keys()))
    print(set(conjtype_feat_map.keys()) & set(marker_feat_map.keys()))

