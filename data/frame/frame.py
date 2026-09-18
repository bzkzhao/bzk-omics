import json, time, urllib.request, urllib.parse, collections, csv

BASE = "https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects"
MODIFIER = ["ISG15","ISGylation","ISGylated","ISGylome","interferon-stimulated gene 15"]
MACHINERY = ["UBA7","UBE1L","UBE2L6","UbcH8","HERC5","HERC6","TRIM25","ARIH1","HHARI"]
REMOVAL = ["USP18","UBP43","deISGylase","deISGylating","deISGylation"]
CONDITIONAL = ["USP16","USP24","USP36"]
TERMS = MODIFIER + MACHINERY + REMOVAL + CONDITIONAL
FIELDS = ["title","projectDescription","keywords","sampleProcessingProtocol"]

def fetch(term, page, size=100):
    q = urllib.parse.urlencode({"keyword": term, "pageSize": size, "page": page})
    with urllib.request.urlopen(f"{BASE}?{q}", timeout=60) as r:
        return json.loads(r.read().decode())

projects, by_term = {}, {}
for t in TERMS:
    got, page = [], 0
    while True:
        try:
            batch = fetch(t, page)
        except Exception as e:
            print(f"!! {t} page {page}: {e}"); break
        if not isinstance(batch, list) or not batch: break
        got += batch
        if len(batch) < 100: break
        page += 1; time.sleep(0.4)
    by_term[t] = len(got)
    for p in got: projects.setdefault(p["accession"], p)
    print(f"{t:<32} {len(got):>4}   cumulative {len(projects)}")
    time.sleep(0.4)

def text(p, f):
    v = p.get(f, "")
    return " ".join(map(str, v)) if isinstance(v, list) else str(v or "")

rows = []
for acc, p in sorted(projects.items()):
    blob = {f: text(p, f).lower() for f in FIELDS}
    hits = {t: [f for f in FIELDS if t.lower() in blob[f]] for t in TERMS}
    hits = {t: f for t, f in hits.items() if f}
    mod = any(t in hits for t in MODIFIER + MACHINERY + REMOVAL)
    if not mod and not any(t in hits for t in CONDITIONAL): continue
    if not mod: continue                      # conditional terms need a modifier too
    rows.append({
        "accession": acc,
        "title": text(p, "title"),
        "terms": ";".join(sorted(hits)),
        "fields": ";".join(sorted({f for fs in hits.values() for f in fs})),
        "organisms": text(p, "organisms"),
        "submissionDate": p.get("submissionDate", ""),
        "publicationDate": p.get("publicationDate", ""),
        "submissionType": p.get("submissionType", ""),
        "n_files": len(p.get("projectFileNames") or []),
        "sdrf": "Y" if (p.get("sdrf") or "").strip() else "N",
        "software": text(p, "softwares"),
        "dataProcessing": text(p, "dataProcessingProtocol"),
        "projectDescription": text(p, "projectDescription"),
        "sampleProcessing": text(p, "sampleProcessingProtocol"),
        "references": text(p, "references")[:200],
    })

with open("frame_raw.tsv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t")
    w.writeheader(); w.writerows(rows)

print(f"\nunique projects returned: {len(projects)}   locally confirmed: {len(rows)}")
print("\nper-term API hits:")
for t, n in sorted(by_term.items(), key=lambda x: -x[1]): print(f"  {t:<32} {n}")
print("\nfield that matched, across confirmed rows:")
c = collections.Counter(f for r in rows for f in r["fields"].split(";"))
for f, n in c.most_common(): print(f"  {f:<28} {n}")
print("\nPOSITIVE CONTROLS")
for a in ["PXD018299","PXD055843","PXD065158","PXD071724"]:
    r = next((x for x in rows if x["accession"] == a), None)
    print(f"  {a}: {'OK  ' + r['fields'] if r else 'MISSING — frame is wrong, do not use'}")
