import json, math, statistics as stt
V = {json.loads(l)["id"]: json.loads(l)["answers"]["needle"]["noul"] for l in open("2026-10-27_C9-M1x_needle.jsonl")}
meta = json.load(open("2026-10-27_C9-M1x_needle.meta.json"))["scenes"]
lg = lambda p: math.log(min(.99, max(.01, p)) / (1 - min(.99, max(.01, p)))); sg = lambda x: 1/(1+math.exp(-x))
steps = vis = dirn = dirok = zero = zerook = ctx = 0; ctxd = []; finals = 0
for s, cards in meta.items():
    cum = [V[f"N-{s}-cum{k}"] for k in range(7)]
    single = [V[f"N-{s}-single{k+1}"] for k in range(6)]
    print(f"{s}: cum " + " ".join(f"{x:.2f}" for x in cum) + f" | rev {V[f'N-{s}-rev']:.2f} | rep base {V[f'N-{s}-cum0#rep']:.2f} full {V[f'N-{s}-cum6#rep']:.2f}")
    pred = sg(lg(cum[0]) + sum(lg(x) - lg(cum[0]) for x in single))
    print(f"   logit-additive pred of full from singles {pred:.2f} vs actual {(cum[6]+V[f'N-{s}-cum6#rep'])/2:.2f}")
    finals += 0.1 <= cum[6] <= 0.9
    for k, (c, e) in enumerate(cards):
        d = cum[k+1] - cum[k]; ds = single[k] - cum[0]; steps += 1
        v = abs(d) >= .08; vis += v
        if e in "+-":
            if v: dirn += 1; dirok += (d > 0) == (e == "+")
        else:
            zero += 1; zerook += abs(d) < .08
        ctxd.append(abs(d - ds)); ctx += abs(d - ds) >= .10
        print(f"   [{e}] {c[:48]:48s} ctx {d:+.2f} single {ds:+.2f}")
print(f"N-a visible steps {vis}/{steps} = {vis/steps:.2f}")
print(f"N-b direction ok {dirok}/{dirn}; zero-cards small {zerook}/{zero}")
print(f"N-c finals in [0.1,0.9] {finals}/3")
print(f"N-e ctx vs single |diff|>=0.10: {ctx}/{steps}; mean {stt.mean(ctxd):.3f}")
