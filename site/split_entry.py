"""진입 페이지(artifact_index.html)를 작은 껍데기 + 분리 파일로 나눈다.

목적: 포털 재게시마다 약 200KB 진입 페이지를 통째로 읽고 다시 보내는 비용을 줄인다.
  artifact_index.html   껍데기(작고 거의 바뀌지 않음): 글꼴, 스타일 링크, 본문 조각을 받아 넣고 스크립트를 순서대로 불러온다
  portal_body.html      본문 조각(신호 보드, 최근 사건, 임박 계획, 메뉴): 기록이 바뀌는 날 이 파일이 바뀐다
  assets/portal.css     스타일(거의 바뀌지 않음)
  assets/portal.js      스크립트(포털 동작, AI Chat, 메뉴): 거의 바뀌지 않음
기록만 바뀐 날은 portal_body.html 과 바뀐 아티클 페이지만 올리면 된다(껍데기·assets는 해시가 같으면 생략).
build_site.py 끝에서 실행한다.
"""
import hashlib, json, re
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"
s = (DIST / "artifact_index.html").read_text(encoding="utf-8")

head_keep = "".join(re.findall(r"<title>.*?</title>|<link rel=\"(?:preconnect|stylesheet)\"[^>]*>", s, re.S))
s = re.sub(r"<title>.*?</title>|<link rel=\"(?:preconnect|stylesheet)\"[^>]*>", "", s, flags=re.S)
css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", s, re.S))
s = re.sub(r"<style[^>]*>.*?</style>", "", s, flags=re.S)
ext = re.findall(r"<script src=\"([^\"]+)\"[^>]*></script>", s)
s = re.sub(r"<script src=\"[^\"]+\"[^>]*></script>", "", s)
js = "\n;\n".join(re.findall(r"<script>(.*?)</script>", s, re.S))
s = re.sub(r"<script>.*?</script>", "", s, flags=re.S)
body = s.strip()

(DIST / "assets").mkdir(exist_ok=True)
(DIST / "assets" / "portal.css").write_text(css, encoding="utf-8")
(DIST / "assets" / "portal.js").write_text(js, encoding="utf-8")
(DIST / "portal_body.html").write_text(body, encoding="utf-8")

# 파일이 바뀌면 주소 뒤 버전이 바뀌어 브라우저 캐시가 새 파일을 받는다
def h(p):
    return hashlib.sha1((DIST / p).read_bytes()).hexdigest()[:8]

shell = f"""{head_keep}
<link rel="stylesheet" href="assets/portal.css?v={h('assets/portal.css')}">
<div id="app" aria-live="polite"></div>
<noscript><p style="padding:24px">이 페이지는 스크립트가 필요합니다.</p></noscript>
<script>
(function () {{
  var app = document.getElementById("app");
  var libs = {json.dumps(ext)}.concat(["assets/portal.js?v={h('assets/portal.js')}"]);
  function load(i) {{
    if (i >= libs.length) return;
    var el = document.createElement("script");
    el.src = libs[i];
    el.onload = function () {{ load(i + 1); }};
    el.onerror = function () {{ load(i + 1); }};
    document.body.appendChild(el);
  }}
  fetch("portal_body.html?v=" + Date.now(), {{ cache: "no-store" }})
    .then(function (r) {{ if (!r.ok) throw new Error(r.status); return r.text(); }})
    .then(function (html) {{ app.innerHTML = html; load(0); }})
    .catch(function (e) {{ app.textContent = "포털 본문을 불러오지 못했습니다. 새로고침해 주세요. (" + e.message + ")"; }});
}})();
</script>
"""
(DIST / "artifact_index.html").write_text(shell, encoding="utf-8")
# 다른 페이지의 '홈' 링크(index.html)도 같은 껍데기를 쓰게 한다(문서 골격을 씌운 독립 페이지)
(DIST / "index.html").write_text('<!doctype html>\n<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body style="margin:0">' + shell + "</body></html>", encoding="utf-8")
man = json.loads((DIST / "manifest.json").read_text(encoding="utf-8")) if (DIST / "manifest.json").exists() else {}
man["shell_files"] = ["portal_body.html", "assets/portal.css", "assets/portal.js"]
(DIST / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"진입 분리: 껍데기 {len(shell.encode())//1024}KB · 본문 {len(body.encode())//1024}KB · css {len(css.encode())//1024}KB · js {len(js.encode())//1024}KB")
