/* MathCraft Landing – Interactions */
(function () {
  "use strict";

  /* ── Nav scroll shadow ── */
  var nav = document.getElementById("nav");
  if (nav) {
    window.addEventListener("scroll", function () {
      nav.classList.toggle("scrolled", window.scrollY > 10);
    }, { passive: true });
  }

  /* ── Showcase tab switching ── */
  var demos = {
    theorem:
'<span class="cm">%% 定理编号 — Card 风格</span>\n' +
'<span class="cm">&gt; [!theorem]</span> <span class="kw">定理 1.1</span> (Cauchy 积分公式)\n' +
'<span class="cm">&gt;</span> 设 $f$ 在单连通域 $D$ 上全纯，$\\gamma$ 为\n' +
'<span class="cm">&gt;</span> $D$ 内的简单闭曲线，则对 $\\gamma$ 内部\n' +
'<span class="cm">&gt;</span> 任意点 $z_0$,\n' +
'<span class="cm">&gt;</span>\n' +
'<span class="cm">&gt;</span> $$f(z_0) = \\frac{<span class="num">1</span>}{<span class="num">2</span>\\pi i}\\oint_\\gamma \\frac{f(z)}{z-z_0}\\,dz$$\n' +
'\n' +
'<span class="cm">&gt; [!corollary]</span> <span class="kw">推论 1.2</span>\n' +
'<span class="cm">&gt;</span> 全纯函数是无穷次可微的。\n' +
'\n' +
'<span class="cm">&gt; [!definition]</span> <span class="kw">定义 1.3</span> (Laurent 级数)\n' +
'<span class="cm">&gt;</span> 设 $f$ 在环域 $r &lt; |z-a| &lt; R$ 上全纯...',

    tikz:
'<span class="cm">```tikz</span>\n' +
'<span class="fn">\\begin</span><span class="str">{tikzpicture}</span>\n' +
'  <span class="cm">% 坐标轴</span>\n' +
'  <span class="fn">\\draw</span>[<span class="num">thick</span>, ->] (-3,0) -- (3,0)\n' +
'    node[right] {$x$};\n' +
'  <span class="fn">\\draw</span>[<span class="num">thick</span>, ->] (0,-2) -- (0,3)\n' +
'    node[above] {$y$};\n' +
'\n' +
'  <span class="cm">% 函数曲线</span>\n' +
'  <span class="fn">\\draw</span>[<span class="kw">domain=-2:2</span>, smooth,\n' +
'    <span class="kw">variable=\\x</span>, <span class="str">blue!70</span>]\n' +
'    plot ({\\x}, {\\x*\\x - 1});\n' +
'\n' +
'  <span class="cm">% 标注</span>\n' +
'  <span class="fn">\\node</span>[<span class="str">blue!70</span>] at (2, 2.5)\n' +
'    {$y = x^2 - 1$};\n' +
'<span class="fn">\\end</span><span class="str">{tikzpicture}</span>\n' +
'<span class="cm">```</span>',

    geogebra:
'<span class="cm">%% GeoGebra 嵌入 (.mcg 文件)</span>\n' +
'<span class="cm">![[my-construction.mcg]]</span>\n' +
'\n' +
'<span class="cm">%% 在 GeoGebra 画布中绘制后</span>\n' +
'<span class="cm">%% 右键菜单 → 导出 TikZ</span>\n' +
'\n' +
'<span class="cm">```tikz</span>\n' +
'<span class="fn">\\begin</span><span class="str">{tikzpicture}</span>[scale=0.8]\n' +
'  <span class="fn">\\coordinate</span> (A) at (0, 0);\n' +
'  <span class="fn">\\coordinate</span> (B) at (4, 0);\n' +
'  <span class="fn">\\coordinate</span> (C) at (1, 3);\n' +
'  <span class="fn">\\draw</span> (A) -- (B) -- (C) -- cycle;\n' +
'  <span class="fn">\\draw</span>[<span class="kw">dashed</span>] (C)\n' +
'    -- ($(A)!(C)!(B)$) node[below]\n' +
'    {$H$};\n' +
'<span class="fn">\\end</span><span class="str">{tikzpicture}</span>\n' +
'<span class="cm">```</span>',

    cd:
'<span class="cm">%% 交换图 — tikzcd</span>\n' +
'<span class="cm">```tikz-cd</span>\n' +
'<span class="fn">\\begin</span><span class="str">{tikzcd}</span>\n' +
'  A <span class="fn">\\arrow</span>[r, "<span class="str">f</span>"]\n' +
'    <span class="fn">\\arrow</span>[d, "<span class="str">g</span>"\']\n' +
'  &amp; B <span class="fn">\\arrow</span>[d, "<span class="str">h</span>"] \\\\\n' +
'  C <span class="fn">\\arrow</span>[r, "<span class="str">k</span>"\']\n' +
'  &amp; D\n' +
'<span class="fn">\\end</span><span class="str">{tikzcd}</span>\n' +
'<span class="cm">```</span>\n' +
'\n' +
'<span class="cm">%% 或使用可视化编辑器：</span>\n' +
'<span class="cm">%% 命令面板 →</span>\n' +
'<span class="cm">%%   <span class="kw">MathCraft: Open CD editor</span></span>'
  };

  var tabs = document.querySelectorAll(".showcase-tab");
  var codeDemo = document.getElementById("codeDemo");

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      tabs.forEach(function (t) { t.classList.remove("active"); });
      tab.classList.add("active");
      var key = tab.getAttribute("data-demo");
      if (demos[key] && codeDemo) {
        codeDemo.innerHTML = demos[key];
      }
    });
  });

  /* ── Smooth scroll for anchor links ── */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) {
      var target = document.querySelector(a.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
})();
