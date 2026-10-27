"""C9-M1g A03+ indirect precedent effect (follow-up of C9-P1)."""
import json
JUDGES = [("yoon", "Judge Yoon Jeong-hee, retired teacher. The year the empty lot outside her classroom became a parking lot, the children lost their playground. Believes rules are only as legitimate as the majority that made them. Put up with the piano downstairs for ten years."),
          ("kang", "Judge Kang Tae-o, ER nurse with a working spouse. After night shifts spends 30 minutes looking for parking. Relies on the playground CCTV because there is nobody to watch the kids. Trusts records over talk."),
          ("park", "Judge Park Bok-rye, runs the laundromat in the shopping arcade. Lost regular customers to parking enforcement in front of her shop. Has done business with the management company for 20 years. Hates neighbors fighting.")]
CASES = {
 "final": ("Residents claim the management company cannot turn the complex playground into a parking lot without residents' consent.",
           "the playground was designated a shared facility at construction; 30+ cars double-park every night; the company held one public hearing on a weekday afternoon."),
 "kia": ("Kia (101-201) claims residents may run a Saturday shared-childcare group on the playground.",
         "it meets every Saturday; there were 2 noise complaints; the management company did not give prior permission."),
 "eunbi": ("Eunbi (101-1001), whose child was hurt on the playground, claims the playground safety repairs must be paid from the management fees.",
           "a repair quote has been obtained; the management company says demolition is cheaper; residents signed a petition against demolition."),
}
PREC = {
 "direct": ["Precedent #1: the committee ruled the management company may not close the rooftop garden without a residents' vote.",
            "Precedent #2: the committee ordered the management company to keep the playground lights on at night for children's safety.",
            "Precedent #3: the committee ruled that a single weekday-afternoon hearing does not count as consulting residents."],
 "indirect": ["Precedent #1 (Noah, 101-702): the committee ruled that daytime piano lessons are ordinary living noise that neighbors must tolerate.",
              "Precedent #2 (Serin, 101-1102): the committee allowed rooftop vegetable boxes as a legitimate use of shared space.",
              "Precedent #3 (Mi-seon, 102-904): the committee allowed the custom of leaving children with the security guard for short periods."],
 "irrelevant": ["Precedent #1: the committee ruled that moving vans may hold the elevator for at most two hours.",
                "Precedent #2: the committee moved the recycling collection day from Monday to Tuesday.",
                "Precedent #3: the committee ruled that notice-board posters must be removed after 30 days."],
}
CR = {"grant_claim": "the claim is granted", "partial": "the claim is partly granted", "deny_claim": "the claim is denied"}
def st(case, cond, in_facts=False):
    claim, facts = CASES[case]
    s = "Apartment complex dispute committee. Three judges rule independently.\n" + "\n".join(p for _, p in JUDGES)
    if cond != "base" and not in_facts:
        s += "\nPrecedent book of this committee:\n" + "\n".join(PREC[cond])
    s += f"\nCase: {claim} Facts: {facts}"
    if in_facts:
        s += " Earlier rulings of this committee: " + " ".join(p.split(": ", 1)[1] for p in PREC[cond])
    return s
Q = {j: {"type": "choice", "instructions": f"How does Judge {n.split(',')[0].split('Judge ')[1]} rule on the claim?", "criteria": CR} for j, n in JUDGES}
items = []
for rep in range(2):
    for case in CASES:
        for cond in ["base", "direct", "indirect", "irrelevant"]:
            items.append({"id": f"J-{case}-{cond}" + ("#rep" if rep else ""), "cond": cond, "state": st(case, cond), "questions": Q})
for case in CASES:
    items.append({"id": f"J-{case}-indirect_facts", "cond": "indirect_facts", "state": st(case, "indirect", True), "questions": Q})
json.dump(items, open("2026-10-27_C9-M1x_a03.items.json", "w"), indent=1); print(len(items))
