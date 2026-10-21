from pathlib import Path
R = Path(__file__).resolve().parents[2]
t = (R / 'tools/c3/c3_build.py').read_text(encoding='utf-8')
a = t.index('# ===================== 조직'); b = t.index('# ===================== 보강')
sw = lambda s: s.replace('C3', 'C6').replace('c3_', 'c6_').replace('china-brands/c3', 'china-brands/c6').replace('에코백스', '하이센스·마이디어·하이얼·모바')
body = (R / 'tools/c6/c6_body.py').read_text(encoding='utf-8')
(R / 'tools/c6/c6_build.py').write_text(sw(t[:a]) + body + sw(t[b:]), encoding='utf-8')
print('ok')
