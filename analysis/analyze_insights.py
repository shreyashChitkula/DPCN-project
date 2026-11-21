import pandas as pd, numpy as np, networkx as nx, community as cl, json, random, math
from collections import Counter, defaultdict
R = '/home/shreyashchitkula/Downloads/DPCN/'
random.seed(7); np.random.seed(7)
d = pd.read_csv(R+'group30_data.csv'); d['nauth'] = d.author.fillna('').str.count(';')+1
a = pd.read_csv(R+'authorship_network.csv')
c = pd.read_csv(R+'citation_network.csv')
ind = pd.read_csv(R+'indian_connections.csv')
INST = ['BARC', 'IGCAR', 'RRCAT', 'NISER']
MEGA = 100
out = {}

def gini(x):
    x = np.sort(np.array(x, float)); n = len(x)
    return float((2*np.arange(1, n+1)-n-1).dot(x)/(n*x.sum()))

# ---------- papers ----------
tot = d.citations.sum()
out['totals'] = dict(rows=len(d), citations=int(tot), mega=int((d.nauth >= MEGA).sum()),
                     mega_cit_share=float(d[d.nauth >= MEGA].citations.sum()/tot),
                     top1=float(d.citations.nlargest(len(d)//100).sum()/tot),
                     top10=float(d.citations.nlargest(len(d)//10).sum()/tot), gini=gini(d.citations))
inst_stats = {}
for k in INST:
    g = d[d.institution == k]; n = g[g.nauth < MEGA]
    rk = g[g.quartile.isin(['Q1', 'Q2', 'Q3', 'Q4'])]
    inst_stats[k] = dict(papers=len(g), cites=int(g.citations.sum()), mean=float(g.citations.mean()),
        median=float(g.citations.median()), mean_nomega=float(n.citations.mean()), median_nomega=float(n.citations.median()),
        mega_papers=int((g.nauth >= MEGA).sum()), mega_share=float((g.nauth >= MEGA).mean()),
        mega_cit_share=float(g[g.nauth >= MEGA].citations.sum()/g.citations.sum()),
        q1=float((rk.quartile == 'Q1').mean()), gini=gini(g.citations), median_team=float(g[g.nauth < MEGA].nauth.median()),
        in_cites_indian=float((g.cites_indian_inst == True).sum()/g.cites_indian_inst.notna().sum()),
        in_cited_by_indian=float((g.cited_by_indian_inst == True).sum()/g.cited_by_indian_inst.notna().sum()),
        by_year={int(y): int(v) for y, v in g.groupby('year').size().items()},
        cites_by_pubyear={int(y): float(v) for y, v in g.groupby('year').citations.mean().items()})
out['inst'] = inst_stats
# lorenz
srt = np.sort(d.citations.values)[::-1]; cum = np.cumsum(srt)/srt.sum()
idx = np.unique(np.round(np.linspace(0, len(srt)-1, 60)).astype(int))
out['lorenz'] = [[float((i+1)/len(srt)), float(cum[i])] for i in idx]
# team size by year
yr = {}
for y, g in d.groupby('year'):
    yr[int(y)] = dict(mean_team=float(g[g.nauth < MEGA].nauth.mean()), mega=float((g.nauth >= MEGA).mean()),
                      solo=float((g.nauth == 1).mean()), papers=len(g))
out['years'] = yr
# citation by team size bucket (among same-year-normalised: use median)
bk = pd.cut(d.nauth, [0, 1, 3, 5, 8, 20, 99, 1e9], labels=['1', '2–3', '4–5', '6–8', '9–20', '21–99', '100+'])
out['team_cit'] = [dict(b=str(k), n=int(len(g)), med=float(g.citations.median()), mean=float(g.citations.mean())) for k, g in d.groupby(bk, observed=True)]
# quartile vs citations
out['quart'] = [dict(q=q, n=int((d.quartile == q).sum()), med=float(d[d.quartile == q].citations.median())) for q in ['Q1', 'Q2', 'Q3', 'Q4']]
# top cited papers
tp = d.sort_values('citations', ascending=False).drop_duplicates('doi').head(8)
out['topcited'] = [dict(t=r.title[:110], inst=r.institution, y=int(r.year), c=int(r.citations), n=int(r.nauth)) for r in tp.itertuples()]
# mega top groups
mg = d[d.nauth >= MEGA].copy()
def tag(t):
    t = t.lower()
    for k, v in [('planck', 'Planck'), ('higgs', 'LHC / Higgs'), ('lhc', 'LHC / Higgs'), ('alice', 'ALICE'), ('cms', 'CMS'), ('atlas', 'ATLAS'), ('collision', 'Heavy-ion / pp collisions'), ('ligo', 'LIGO/Virgo'), ('gravitational', 'LIGO/Virgo'), ('vesicle', 'Community guidelines')]:
        if k in t: return v
    return 'Other'
mg['grp'] = mg.title.map(tag)
out['mega_groups'] = [dict(g=k, n=int(len(x)), c=int(x.citations.sum())) for k, x in mg.groupby('grp')]

# ---------- faculty network ----------
nauth_by_doi = d.drop_duplicates('doi').set_index('doi').nauth.to_dict()
a['nauth'] = a.paper_doi.map(nauth_by_doi)
a['mega'] = a.nauth >= MEGA
out['pair_events'] = dict(total=len(a), mega=int(a.mega.sum()))
inst = {}
for r in a.itertuples():
    inst[r.author_a] = r.inst_a; inst[r.author_b] = r.inst_b
def build(df):
    G = nx.Graph()
    for r in df.itertuples():
        if G.has_edge(r.author_a, r.author_b): G[r.author_a][r.author_b]['w'] += 1
        else: G.add_edge(r.author_a, r.author_b, w=1)
    return G
G = build(a)
Gn = build(a[~a.mega])   # without hyper-authored papers
nx.set_node_attributes(G, inst, 'inst')
cross_all = sum(1 for u, v in G.edges if inst[u] != inst[v])
cross_nomega = sum(1 for u, v in Gn.edges if inst[u] != inst[v])
out['cross'] = dict(pairs=G.number_of_edges(), cross=cross_all, pairs_nomega=Gn.number_of_edges(), cross_nomega=cross_nomega,
                    nodes_nomega=Gn.number_of_nodes())
def stats(H, label):
    L = H.subgraph(max(nx.connected_components(H), key=len))
    return dict(label=label, n=H.number_of_nodes(), m=H.number_of_edges(), k=2*H.number_of_edges()/H.number_of_nodes(),
                k2=float(np.mean([x**2 for _, x in H.degree()])), C=nx.average_clustering(H), T=nx.transitivity(H),
                lcc=len(L), L=nx.average_shortest_path_length(L), D=nx.diameter(L), comps=nx.number_connected_components(H),
                assort=nx.degree_assortativity_coefficient(H))
S = stats(G, 'real')
n, m = G.number_of_nodes(), G.number_of_edges(); kbar = 2*m/n
def lcc_graph(H): return H.subgraph(max(nx.connected_components(H), key=len))
ers = [stats(nx.gnm_random_graph(n, m, seed=s), 'er') for s in range(5)]
bas = [stats(nx.barabasi_albert_graph(n, max(1, round(kbar/2)), seed=s), 'ba') for s in range(5)]
ws = [stats(nx.watts_strogatz_graph(n, max(2, int(round(kbar/2))*2), 0.1, seed=s), 'ws') for s in range(3)]
def avg(L): return {k: float(np.mean([x[k] for x in L])) for k in ['C', 'T', 'L', 'D', 'lcc', 'k2', 'assort']}
cfgs = []
for s in range(5):
    H = nx.Graph(G); nx.double_edge_swap(H, nswap=m*10, max_tries=m*200, seed=s); cfgs.append(stats(H, 'cfg'))
out['models'] = dict(real=S, er=avg(ers), ba=avg(bas), ws=avg(ws), cfg=avg(cfgs), sigma=float((S['C']/avg(ers)['C'])/(S['L']/avg(ers)['L'])))
deg = dict(G.degree())
out['degdist'] = dict(real=sorted(Counter(deg.values()).items()),
                      er=sorted(Counter(dict(nx.gnm_random_graph(n, m, seed=1).degree()).values()).items()),
                      ba=sorted(Counter(dict(nx.barabasi_albert_graph(n, max(1, round(kbar/2)), seed=1).degree()).values()).items()))
# communities
p = cl.best_partition(G, weight='w', random_state=3)
Q = cl.modularity(p, G, weight='w')
ncom = Counter(p.values())
order = [k for k, _ in ncom.most_common()]
remap = {k: i for i, k in enumerate(order)}
p = {k: remap[v] for k, v in p.items()}
comm_info = []
for cid in range(len(order)):
    mem = [x for x in p if p[x] == cid]
    ci = Counter(inst[x] for x in mem)
    comm_info.append(dict(id=cid, n=len(mem), insts=dict(ci), purity=max(ci.values())/len(mem)))
out['comm'] = dict(Q=Q, k=len(order), info=comm_info,
                   inst_nmi=None)
from sklearn.metrics import normalized_mutual_info_score as nmi
nodes_l = list(G.nodes)
out['comm']['inst_nmi'] = float(nmi([inst[x] for x in nodes_l], [p[x] for x in nodes_l]))
out['comm']['weighted_purity'] = float(sum(max(ci['insts'].values()) for ci in comm_info)/n)
# betweenness, articulation
bc = nx.betweenness_centrality(G)
art = set(nx.articulation_points(G))
# layout
LCCn = max(nx.connected_components(G), key=len)
GW = nx.Graph()
for u, v in G.edges:
    w_ = 3.0 if p[u] == p[v] else (0.25 if inst[u] != inst[v] else 0.6)
    GW.add_edge(u, v, weight=w_)
LW = GW.subgraph(LCCn)
pos = nx.spring_layout(LW, k=0.55/np.sqrt(len(LW)), iterations=600, seed=4, weight='weight')
arr = np.array(list(pos.values())); lo, hi = arr.min(0), arr.max(0)
for x in list(pos): pos[x] = (pos[x]-lo)/(hi-lo)*np.array([1, 0.86])
rest = [x for x in G.nodes if x not in pos]
comps_ = [c for c in nx.connected_components(G) if c is not LCCn and not (LCCn >= c)]
j = 0; nco = max(1, len(comps_))
for ci_, comp in enumerate(comps_):
    cx = (ci_+0.5)/nco
    for t_, x in enumerate(sorted(comp)): pos[x] = np.array([cx+(t_-(len(comp)-1)/2)*0.012, 0.95])
xs = np.array([pos[x] for x in G.nodes])
ids = {x: i for i, x in enumerate(G.nodes)}
name = lambda s: ' '.join(s.replace('Dr.', '').replace('Prof.', '').split())
# papers per faculty (in network)
pc = Counter()
for r in a.itertuples(): pc[r.author_a] += 1; pc[r.author_b] += 1
# degree in non-mega graph
fy = {}
for r in a.itertuples():
    k = frozenset((r.author_a, r.author_b)); fy[k] = min(fy.get(k, 9999), r.year)
nfy = {}
for k, y_ in fy.items():
    for u in k: nfy[u] = min(nfy.get(u, 9999), y_)
out['nodes'] = [dict(id=ids[x], name=name(x), inst=inst[x], deg=deg[x], wdeg=int(G.degree(x, weight='w')), bc=round(bc[x], 4), comm=p[x],
                     art=int(x in art), x=round(float(xs[ids[x]][0]), 4), py=round(float(xs[ids[x]][1]), 4), dn=(Gn.degree(x) if x in Gn else 0), y=nfy[x]) for x in G.nodes]
out['edges'] = [dict(s=ids[u], t=ids[v], w=G[u][v]['w'], x=int(inst[u] != inst[v]), m=int(not Gn.has_edge(u, v)), y=fy[frozenset((u, v))]) for u, v in G.edges]
out['inst_nodes']=dict(Counter(inst.values()))
out['top_bc'] = sorted([dict(name=name(x), inst=inst[x], bc=round(v, 4), deg=deg[x]) for x, v in bc.items()], key=lambda z: -z['bc'])[:10]
out['top_deg'] = sorted([dict(name=name(x), inst=inst[x], deg=v) for x, v in deg.items()], key=lambda z: -z['deg'])[:10]
out['art_n'] = len(art)
# distance distribution
L = lcc_graph(G)
dd = Counter()
for s, dist in nx.all_pairs_shortest_path_length(L):
    for t, v in dist.items():
        if v > 0: dd[v] += 1
tt = sum(dd.values())
out['dist'] = [[k, v/tt] for k, v in sorted(dd.items())]
# within-inst vs cross distances
# growth
yrs = list(range(2016, 2027)); gro = []
Gc = nx.Graph(); seen = set()
for y in yrs:
    for r in a[a.year == y].itertuples(): Gc.add_edge(r.author_a, r.author_b)
    Lc = max(nx.connected_components(Gc), key=len)
    gro.append(dict(y=y, n=Gc.number_of_nodes(), m=Gc.number_of_edges(), lcc=len(Lc)/Gc.number_of_nodes(), C=nx.average_clustering(Gc)))
out['growth'] = gro
# preferential attachment test: degree at end of year y -> new links in y+1
pa = defaultdict(list)
Gp = nx.Graph()
for y in yrs[:-1]:
    for r in a[a.year == y].itertuples(): Gp.add_edge(r.author_a, r.author_b)
    nxt = set()
    new = Counter()
    for r in a[a.year == y+1].itertuples():
        if not Gp.has_edge(r.author_a, r.author_b):
            nxt.add(frozenset((r.author_a, r.author_b)))
    for e in nxt:
        for u in e:
            if u in Gp: new[u] += 1
    for u in Gp.nodes: pa[Gp.degree(u)].append(new[u])
pts = [(k, float(np.mean(v)), len(v)) for k, v in sorted(pa.items()) if k > 0 and len(v) >= 5]
# log-bins
bins = [1, 2, 3, 4, 6, 9, 14, 22, 35, 100]
pab = []
for lo, hi in zip(bins[:-1], bins[1:]):
    xs_, ys_, ns = [], [], 0
    for k, v in pa.items():
        if lo <= k < hi: xs_ += [k]*len(v); ys_ += v; ns += len(v)
    if ns >= 8: pab.append([float(np.mean(xs_)), float(np.mean(ys_)), ns])
lx = np.log([q[0] for q in pab]); ly = np.log([max(q[1], 1e-3) for q in pab])
slope = float(np.polyfit(lx, ly, 1)[0])
out['pa'] = dict(pts=pab, slope=slope)
# robustness
def lcc_frac(H, n0): return len(max(nx.connected_components(H), key=len))/n0 if H.number_of_nodes() else 0
def attack(order_fn, adaptive=False, steps=40):
    H = nx.Graph(G); n0 = H.number_of_nodes(); res = [[0, lcc_frac(H, n0)]]
    per = n0//steps
    if not adaptive: order = order_fn(H)
    for i in range(1, steps+1):
        if adaptive: order = order_fn(H)
        for v in order[:per]: H.remove_node(v)
        if not adaptive: order = order[per:]
        res.append([i*per/n0, lcc_frac(H, n0)])
        if H.number_of_nodes() == 0: break
    return res
def deg_order(H): return [v for v, _ in sorted(H.degree, key=lambda z: -z[1])]
def bc_order(H): return [v for v, _ in sorted(nx.betweenness_centrality(H, k=min(120,len(H)), seed=1).items(), key=lambda z: -z[1])]
def rand_order(H): l = list(H.nodes); random.shuffle(l); return l
rr = np.mean([[q[1] for q in attack(rand_order)] for _ in range(10)], axis=0)
tmp = attack(rand_order)
out['robust'] = dict(random=[[tmp[i][0], float(rr[i])] for i in range(len(tmp))], degree=attack(deg_order, True), between=attack(bc_order, True, steps=30))
# robustness on ER with same N,m for comparison
Ger = nx.gnm_random_graph(n, m, seed=2)
def attack_g(G0, order_fn, steps=40):
    H = nx.Graph(G0); n0 = H.number_of_nodes(); res = [[0, lcc_frac(H, n0)]]; per = n0//steps
    for i in range(1, steps+1):
        order = order_fn(H)
        for v in order[:per]: H.remove_node(v)
        res.append([i*per/n0, lcc_frac(H, n0)])
        if H.number_of_nodes() == 0: break
    return res
out['robust']['er_degree'] = attack_g(Ger, deg_order)
# molloy-reed estimate
k_, k2_ = kbar, S['k2']
out['robust']['kappa'] = k2_/k_
out['robust']['fc_random'] = 1-1/(k2_/k_-1)
# SIR thresholds & final sizes
def sir(H, beta, gamma, seeds, reps=1):
    sizes = []
    nodes = list(H.nodes)
    for _ in range(reps):
        inf = set(seeds); rec = set();
        while inf:
            new = set()
            for u in inf:
                for v in H[u]:
                    if v not in inf and v not in rec and v not in new and random.random() < beta: new.add(v)
            rec |= {u for u in inf if random.random() < gamma}
            inf = (inf-rec) | new
            rec |= set()
        sizes.append(len(rec)+len(inf))
    return float(np.mean(sizes))/H.number_of_nodes()
# final size vs beta (gamma=1: independent cascade per-link prob T)
Hc = nx.Graph(G)
cfgG = nx.Graph(G); nx.double_edge_swap(cfgG, nswap=m*10, max_tries=m*200, seed=1)
def cascade(H, T, seeds):
    act = set(seeds); fr = set(seeds)
    while fr:
        nf = set()
        for u in fr:
            for v in H[u]:
                if v not in act and random.random() < T: act.add(v); nf.add(v)
        fr = nf
    return len(act)/H.number_of_nodes()
Ts = [i/40 for i in range(1, 25)]
nodes_list = list(G.nodes)
def curve(H, reps=60):
    nl = list(H.nodes)
    return [[T, float(np.mean([cascade(H, T, [random.choice(nl)]) for _ in range(reps)]))] for T in Ts]
out['sir'] = dict(real=curve(G), er=curve(Ger), cfg=curve(cfgG), Tc_real=k_/(k2_-k_), Tc_er=1/(avg(ers)['k2']/k_-1))
# seed type @ T=0.15: spreading from hub vs random vs bridge vs periphery; and time courses
def timecourse(H, seed, T=0.2, reps=80):
    tcs = []
    for _ in range(reps):
        act = {seed}; fr = {seed}; tc = [1]
        while fr or len(tc) < 14:
            nf = set()
            for u in fr:
                for v in H[u]:
                    if v not in act and random.random() < T: act.add(v); nf.add(v)
            fr = nf; tc.append(len(act))
            if len(tc) > 14: break
        tcs.append(tc[:14])
    return [float(x) for x in np.mean(tcs, axis=0)]
L0 = list(L.nodes)
hub = max(deg, key=deg.get); bridge = max(bc, key=bc.get)
byd = sorted(L0, key=lambda x: deg[x])
periph = byd[len(byd)//20]
out['seedtc'] = dict(hub=timecourse(G, hub), bridge=timecourse(G, bridge), periphery=timecourse(G, periph), rand=[float(np.mean(x)) for x in zip(*[timecourse(G, random.choice(L0), reps=1) for _ in range(150)])])
out['seedtc']['names'] = dict(hub=name(hub), bridge=name(bridge))
# expected reach by inst of seed (T=.2)
out['seed_inst'] = {k: float(np.mean([cascade(G, 0.2, [random.choice([x for x in L0 if inst[x] == k])]) for _ in range(150)])) for k in INST}
# reach crossing: fraction of infected in other institutions
def cross_reach(T=0.2, reps=150):
    res = {}
    for k in INST:
        pool = [x for x in L0 if inst[x] == k]; fr_in = []
        for _ in range(reps):
            s = random.choice(pool); act = {s}; fr = {s}
            while fr:
                nf = set()
                for u in fr:
                    for v in G[u]:
                        if v not in act and random.random() < T: act.add(v); nf.add(v)
                fr = nf
            fr_in.append(np.mean([inst[x] == k for x in act]) if len(act) > 1 else 1)
        res[k] = float(np.mean(fr_in))
    return res
out['stay_home'] = cross_reach()

# ---------- link prediction backtest ----------
cut = 2021
Gtr = nx.Graph();
for r in a[a.year <= cut].itertuples():
    Gtr.add_edge(r.author_a, r.author_b)
new = set()
for r in a[a.year > cut].itertuples():
    if r.author_a in Gtr and r.author_b in Gtr and not Gtr.has_edge(r.author_a, r.author_b): new.add(tuple(sorted((r.author_a, r.author_b))))
cand = [(u, v) for u, v in nx.non_edges(Gtr)]
random.shuffle(cand)
negs = [e for e in cand if tuple(sorted(e)) not in new][:20000]
from sklearn.metrics import roc_auc_score
def score(fn, es): return [s for _, _, s in fn(Gtr, es)]
y = [1]*len(new)+[0]*len(negs); pairs = list(new)+negs
def auc(fn):
    return float(roc_auc_score(y, [s for _, _, s in fn(Gtr, pairs)]))
cn = lambda g, es: [(u, v, len(list(nx.common_neighbors(g, u, v)))) for u, v in es]
res = dict(common_neighbors=auc(cn), adamic_adar=auc(nx.adamic_adar_index), jaccard=auc(nx.jaccard_coefficient),
           pref_attach=auc(nx.preferential_attachment), random=0.5, n_new=len(new))
same_inst = lambda g, es: [(u, v, float(inst[u] == inst[v])) for u, v in es]
res['same_institute'] = auc(same_inst)
out['linkpred'] = res
# new ties: share that had common neighbour
out['linkpred']['new_with_cn'] = float(np.mean([len(list(nx.common_neighbors(Gtr, u, v))) > 0 for u, v in new]))
out['linkpred']['new_same_inst'] = float(np.mean([inst[u] == inst[v] for u, v in new]))
# missed collaborations in full graph: same institute, never co-authored, highest AA, in same LCC
cands = [(u, v) for u, v in nx.non_edges(G) if inst[u] == inst[v] and nx.has_path(G, u, v) and len(list(nx.common_neighbors(G, u, v))) >= 4]
sc = sorted([(u, v, len(list(nx.common_neighbors(G, u, v))), s) for (u, v), s in zip(cands, [x[2] for x in nx.adamic_adar_index(G, cands)])], key=lambda z: -z[3])[:12]
out['missed'] = [dict(a=name(u), b=name(v), inst=inst[u], cn=cn_, aa=round(s, 2)) for u, v, cn_, s in sc]

# ---------- citation network ----------
CG = nx.DiGraph(); CG.add_edges_from(zip(c.source_doi, c.target_doi))
ind_ = pd.Series(dict(CG.in_degree())); outd_ = pd.Series(dict(CG.out_degree()))
vals = ind_[ind_ > 0].values
xmin = 3
tail = vals[vals >= xmin]; alpha = 1+len(tail)/np.sum(np.log(tail/(xmin-0.5)))
cc_ = Counter(vals)
xsx = sorted(cc_); ccdf = []; s_ = len(vals); run = s_
for x in xsx: ccdf.append([int(x), run/s_]); run -= cc_[x]
out['cit'] = dict(nodes=CG.number_of_nodes(), edges=CG.number_of_edges(), alpha=float(alpha), ccdf=ccdf[::max(1, len(ccdf)//80)],
                  zero_in=float((ind_ == 0).mean()), maxin=int(ind_.max()), top1_in_share=float(ind_.nlargest(len(ind_)//100).sum()/ind_.sum()),
                  top10_in_share=float(ind_.nlargest(len(ind_)//10).sum()/ind_.sum()))
pr = nx.pagerank(CG)
t2 = d.drop_duplicates('doi').set_index('doi')
out['pr_top'] = [dict(t=t2.title.get(k, '?')[:100], inst=t2.institution.get(k, '?'), y=int(t2.year.get(k, 0)), pr=round(v*1000, 2), ind=int(ind_[k])) for k, v in sorted(pr.items(), key=lambda z: -z[1])[:8]]
# inst matrix (unique pairs: use c rows)
M = c.groupby(['source_inst', 'target_inst']).size().unstack(fill_value=0).reindex(index=INST, columns=INST, fill_value=0)
out['cit_matrix'] = M.values.tolist()
# age: pub year of target vs in-degree
tt = c.drop_duplicates(['source_doi', 'target_doi'])
ty = t2.year
indeg_by_year = pd.Series(dict(CG.in_degree())).to_frame('indeg'); indeg_by_year['year'] = indeg_by_year.index.map(ty)
out['indeg_year'] = {int(k): float(v) for k, v in indeg_by_year.groupby('year').indeg.mean().items() if not math.isnan(k)}
# citations lag: source year - target year
tt = tt.assign(ty=tt.target_doi.map(ty))
lag = (tt.year-tt.ty).dropna()
out['lag'] = {int(k): int(v) for k, v in lag.value_counts().sort_index().items() if 0 <= k <= 10}
out['lag_mean'] = float(lag[lag >= 0].mean())
# reciprocity
Mx = np.array(out['cit_matrix'], float)
# ---------- Indian partners ----------
ind['cpp'] = ind.total_citations/ind.shared_papers
ptot = ind.groupby('partner_inst').agg(sp=('shared_papers', 'sum'), tc=('total_citations', 'sum'), n=('your_inst', 'nunique')).sort_values('sp', ascending=False)
out['partners'] = [dict(p=k, sp=int(r.sp), tc=int(r.tc), n=int(r.n)) for k, r in ptot.head(15).iterrows()]
out['partners_by_inst'] = {k: [dict(p=r.partner_inst, sp=int(r.shared_papers), cpp=round(r.cpp, 1)) for r in ind[ind.your_inst == k].sort_values('shared_papers', ascending=False).head(6).itertuples()] for k in INST}
out['partner_conc'] = {k: dict(n=int(len(g)), top10=float(g.shared_papers.nlargest(10).sum()/g.shared_papers.sum()), single=float((g.shared_papers == 1).mean())) for k, g in ind.groupby('your_inst')}
out['shared_partners'] = int((ptot.n >= 2).sum()); out['partners_n'] = len(ptot); out['all3'] = int((ptot.n >= 3).sum())
# type of partner
def ptype(s):
    s = s.lower()
    if 'indian institute of technology' in s or 'iit' in s.split(): return 'IIT'
    if 'national institute of technology' in s: return 'NIT'
    if 'university' in s or 'college' in s or 'vidyapeeth' in s: return 'University'
    if 'indian institute of science' in s or 'iiser' in s or 'iiit' in s: return 'IISc/IISER/IIIT'
    if 'tata' in s or 'council' in s or 'bhabha' in s or 'research' in s or 'laboratory' in s or 'centre' in s or 'center' in s: return 'Research institute / lab'
    return 'Other'
ind['ptype'] = ind.partner_inst.map(ptype)
out['ptype'] = [dict(t=k, sp=int(g.shared_papers.sum()), n=int(len(g)), cpp=float(g.total_citations.sum()/g.shared_papers.sum())) for k, g in ind.groupby('ptype')]
# international coauthors
ci = d.coauthor_institutes.fillna('')
out['coauth_cov'] = float((ci != '').mean())

def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [clean(x) for x in o]
    if isinstance(o, (np.floating, float)): return None if (isinstance(o, float) and math.isnan(o)) else float(o)
    if isinstance(o, np.integer): return int(o)
    return o
json.dump(clean(out), open('/tmp/claude-1000/-home-shreyashchitkula--claude-spares-spare-6ooXbW/cbd42c69-e9be-4d65-89d6-eae34d752ce2/scratchpad/data.json', 'w'))
print('done')
