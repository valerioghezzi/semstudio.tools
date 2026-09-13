from pathlib import Path

root = Path('.')

def rep(s, old, new, label, count=None):
    n = s.count(old)
    if count is not None and n != count:
        raise SystemExit(f'{label}: expected {count}, found {n}')
    if n == 0:
        raise SystemExit(f'{label}: pattern not found')
    return s.replace(old, new)

# Diagnostic catalogue entries are stored under `txt`, not `text`.
for p in root.glob('*.html'):
    s = p.read_text(encoding='utf-8')
    s2 = s.replace('esc(bits[i].text)', 'esc(bits[i].txt || "")')
    s2 = s2.replace('esc(a[i].text)', 'esc(a[i].txt || "")')
    if s2 != s:
        p.write_text(s2, encoding='utf-8')

# Math formulas in table headers are scrollable in CSS; include them in the
# keyboard-accessible scrollbox selector on pages that actually contain them.
sel_old = 'var SEL = ".table-wrap, pre.syntax, .eq, .scroller, p math, li math, td math";'
sel_new = 'var SEL = ".table-wrap, pre.syntax, .eq, .scroller, p math, li math, td math, th math";'
for name in ['bifactor.html','chi-square-difference.html','parceling.html','reliability.html']:
    p = root / name
    s = p.read_text(encoding='utf-8')
    s = rep(s, sel_old, sel_new, f'{name} scroll selector', 1)
    p.write_text(s, encoding='utf-8')

# LST safeguards.
p = root / 'lst.html'
s = p.read_text(encoding='utf-8')
s = rep(s,
'''    var traitVar = r.vars[trait] ? r.vars[trait].est : null;
    if (traitVar === null) return { error: "trait variance", structure: s };''',
'''    var traitEntry = r.vars[trait] || null;
    if (traitEntry && traitEntry.residual) return { error: "trait residual variance", structure: s };
    var traitVar = traitEntry ? traitEntry.est : null;
    if (traitVar === null) return { error: "trait variance", structure: s };''',
'lst trait variance', 1)
s = rep(s,
'''      var y = mt + i * 42, c = states[i].con === null ? 0 : states[i].con;''',
'''      var y = mt + i * 42, rawC = states[i].con === null ? 0 : states[i].con;
      var c = Math.max(0, Math.min(1, rawC));''',
'lst chart clamp', 1)
s = rep(s,
'''    if (has) html += '<p class="hint">The reliability computed here departs from the R-square the file prints for the same variable by at most ' + f3(worst) +
      ", which is the rounding of the printed estimates: the two are the same quantity, and the columns before it say where that reliability comes from.</p>";
    var neg = false;
    for (i = 0; i < d.states.length; i++)
      for (j = 0; j < d.states[i].items.length; j++)
        if (d.states[i].items[j].error !== null && d.states[i].items[j].error < 0) neg = true;
    if (neg) html += statusBlock("warn", "An error variance is negative.",
      "At least one measured variable has a negative error variance, so the shares for it do not describe a decomposition of a variance. A negative variance estimate indicates that the model is not admissible as specified; the problem should be resolved before these coefficients are interpreted.");''',
'''    if (has) {
      if (worst <= 0.005) html += '<p class="hint">The reliability computed here differs from the R-square printed for the same variable by at most ' + f3(worst) +
        ", a difference compatible with rounding of the printed estimates. The columns before it show the components of that reliability.</p>";
      else html += '<p class="hint">The reliability computed here differs from the R-square printed for the same variable by as much as ' + f3(worst) +
        ". This is larger than expected from ordinary rounding, so the discrepancy should be checked before the decomposition is interpreted.</p>";
    }
    var neg = d.traitVariance !== null && d.traitVariance < 0;
    for (i = 0; i < d.states.length; i++) {
      if (d.states[i].zeta !== null && d.states[i].zeta < 0) neg = true;
      for (j = 0; j < d.states[i].items.length; j++)
        if (d.states[i].items[j].error !== null && d.states[i].items[j].error < 0) neg = true;
    }
    if (neg) html += statusBlock("warn", "A variance estimate is negative.",
      "At least one trait, occasion-residual, or measurement-error variance is negative. The resulting shares do not form an admissible variance decomposition and should not be interpreted until the source of the improper estimate has been resolved.");''',
'lst discrepancy and negative variances', 1)
s = rep(s,
'''  function handleFile(file) {
    readTextFile(file, function (text) {''',
'''  function handleFile(file) {
    $("file-name").textContent = file.name || "";
    readTextFile(file, function (text) {''',
'lst filename early', 1)
s = rep(s,
'''          "The file does not carry " + (d.error === "trait variance" ? "the variance of the trait" :
            (d.error === "state residual" ? "the residual variance of " + esc(d.which || "an occasion") :
              "a place in the trait for " + esc(d.which || "one of the factors"))) +''',
'''          "The file does not carry " + (d.error === "trait variance" ? "the variance of the trait" :
            (d.error === "trait residual variance" ? "a free trait variance in the Variances section; the trait is printed with a residual variance instead" :
              (d.error === "state residual" ? "the residual variance of " + esc(d.which || "an occasion") :
                "a place in the trait for " + esc(d.which || "one of the factors")))) +''',
'lst residual trait message', 1)
s = rep(s,
'''      STATE.rsq = LST.readRSquare(text);
      $("file-name").textContent = file.name || "";''',
'''      STATE.rsq = LST.readRSquare(text);''',
'lst remove late filename', 1)
s = rep(s,
'''  ok("a file without the variance of the trait is refused", LST.decompose(noVar).error, "trait variance");
  okTrue("a multiple-group output is recognised",''',
'''  ok("a file without the variance of the trait is refused", LST.decompose(noVar).error, "trait variance");
  var residualTrait = txt.replace(" Variances\\n    XI                 0.800      0.080     10.000      0.000\\n\\n Residual Variances",
                                  " Residual Variances\\n    XI                 0.800      0.080     10.000      0.000");
  ok("a trait printed with a residual variance is refused", LST.decompose(residualTrait).error, "trait residual variance");
  okTrue("a multiple-group output is recognised",''',
'lst residual trait self-test', 1)
p.write_text(s, encoding='utf-8')

# Ryu & West level-specific RMSEA: within-level effective sample size is N - J.
p = root / 'multilevel.html'
s = p.read_text(encoding='utf-8')
s = rep(s,
'''<mrow><msub><mi>df</mi><mrow><mi>PS</mi><mo>&#x2212;</mo><mi>W</mi></mrow></msub><mi>N</mi></mrow>''',
'''<mrow><msub><mi>df</mi><mrow><mi>PS</mi><mo>&#x2212;</mo><mi>W</mi></mrow></msub><mrow><mo>(</mo><mi>N</mi><mo>&#x2212;</mo><mi>J</mi><mo>)</mo></mrow></mrow>''',
'multilevel RMSEA formula', 1)
s = rep(s,
'''the between-level index is divided by the number of clusters and the within-level index by the total number of observations, which are the divisors of Equations 17 and 19 of Ryu and West (2009).''',
'''the between-level index is divided by <var>J</var> and the within-level index by <var>N</var> − <var>J</var>, the effective sample-size terms in the level-specific decomposition of Ryu and West (2009).''',
'multilevel RMSEA explanation', 1)
s = rep(s,
'''        rmsea: ML.rmseaPS(byKey["PS-W"].chi2, byKey["PS-W"].df, N), size: N, sizeName: "observations" });''',
'''        rmsea: ML.rmseaPS(byKey["PS-W"].chi2, byKey["PS-W"].df, N - J), size: N - J, sizeName: "N − J" });''',
'multilevel RMSEA calculation', 1)
s = rep(s,
'''  ok("the within row uses the total number of observations, as in Equation 19 of Ryu and West (2009)", tbl.rows[1].size, 250);''',
'''  ok("the within row uses N minus J", tbl.rows[1].size, 220);
  ok("the within row RMSEA uses N minus J", tbl.rows[1].rmsea, ML.rmseaPS(60, 25, 220), 1e-12);''',
'multilevel integration self-test', 1)
p.write_text(s, encoding='utf-8')
