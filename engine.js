// Worth Math engine: exact inflation and purchasing power arithmetic on BigInt fractions. No floating point.
var AMT_ERR = "amount must be a number from 0 to 999999999999 with at most 2 decimals";
var RATE_ERR = "rate must be a percent from -50 to 100 with at most 2 decimals";
var YEARS_ERR = "years must be a whole number from 0 to 100";

function _pl(n, w) { return n + " " + w + (n === 1 ? "" : "s"); }
function _dec(text, re, err) {
  var t = typeof text === "string" ? text.trim() : "";
  if (!re.test(t)) throw new Error(err);
  var neg = t.charAt(0) === "-";
  if (neg) t = t.slice(1);
  var parts = t.split(".");
  var frac = parts.length > 1 ? parts[1] : "";
  var n = BigInt(parts[0] + frac);
  return { n: neg ? -n : n, d: 10n ** BigInt(frac.length) };
}
function _mul(a, b) { return { n: a.n * b.n, d: a.d * b.d }; }
function _div(a, b) { return b.n < 0n ? { n: -a.n * b.d, d: -a.d * b.n } : { n: a.n * b.d, d: a.d * b.n }; }
function _sub1(a) { return { n: a.n - a.d, d: a.d }; }
function _pow(a, k) { var r = { n: 1n, d: 1n }; for (var i = 0; i < k; i++) r = _mul(r, a); return r; }
function _cmp(a, b) { var x = a.n * b.d, y = b.n * a.d; return x < y ? -1 : x > y ? 1 : 0; }
function _fmt(v, k) {
  var neg = v.n < 0n, n = neg ? -v.n : v.n, p = 10n ** BigInt(k);
  var scaled = (2n * n * p + v.d) / (2n * v.d);
  var s = scaled.toString();
  while (s.length < k + 1) s = "0" + s;
  var out = k ? s.slice(0, s.length - k) + "." + s.slice(s.length - k) : s;
  return (neg && scaled !== 0n ? "-" : "") + out;
}
function _money(text) {
  var v = _dec(text, /^[0-9]{1,12}(\.[0-9]{1,2})?$/, AMT_ERR);
  return v;
}
function _factor(text) {
  var r = _dec(text, /^-?[0-9]{1,3}(\.[0-9]{1,2})?$/, RATE_ERR);
  if (_cmp(r, { n: -50n, d: 1n }) < 0 || _cmp(r, { n: 100n, d: 1n }) > 0) throw new Error(RATE_ERR);
  return { pct: r, f: { n: r.n + 100n * r.d, d: 100n * r.d } };
}
function _years(text) {
  var t = typeof text === "string" ? text.trim() : "";
  if (!/^[0-9]{1,3}$/.test(t) || parseInt(t, 10) > 100) throw new Error(YEARS_ERR);
  return parseInt(t, 10);
}
function _rate(r) {
  var s = _fmt(r, 2);
  return s.indexOf(".") >= 0 ? s.replace(/0+$/, "").replace(/\.$/, "") : s;
}
function _pct(v) { return _fmt({ n: v.n * 100n, d: v.d }, 2) + "%"; }

// The shrink truth: what a sum buys, and what the same basket costs, after some years of steady price rises.
function shrinkTruth(amount, rate, years) {
  var a = _money(amount), r = _factor(rate), n = _years(years);
  var f = _pow(r.f, n);
  return "At " + _rate(r.pct) + "% a year for " + _pl(n, "year") + ", " + _fmt(a, 2) + " later buys what " + _fmt(_div(a, f), 2) +
    " buys today, and what costs " + _fmt(a, 2) + " today would cost " + _fmt(_mul(a, f), 2) + " then. Prices change by " +
    _pct(_sub1(f)) + " in total.";
}

// The raise truth: a pay raise against inflation, compounded rather than subtracted.
function raiseTruth(raise, inflation) {
  var g = _factor(raise), i = _factor(inflation);
  var real = _sub1(_div(g.f, i.f));
  var shortcut = { n: g.pct.n * i.pct.d - i.pct.n * g.pct.d, d: g.pct.d * i.pct.d * 100n };
  return "With a raise of " + _rate(g.pct) + "% and inflation of " + _rate(i.pct) + "%, buying power changes by " + _pct(real) +
    " (subtracting the percents would give " + _pct(shortcut) + "). Matching inflation of " + _rate(i.pct) + "% takes a raise of " +
    _rate(i.pct) + "%.";
}

// The savings truth: growth at a yearly rate, then the same sum in today's money.
function savingsTruth(amount, interest, inflation, years) {
  var a = _money(amount), s = _factor(interest), i = _factor(inflation), n = _years(years);
  var nominal = _mul(a, _pow(s.f, n));
  var realF = _div(s.f, i.f);
  var real = _mul(a, _pow(realF, n));
  return _fmt(a, 2) + " growing at a yearly rate of " + _rate(s.pct) + "% for " + _pl(n, "year") + " becomes " + _fmt(nominal, 2) +
    ". With inflation of " + _rate(i.pct) + "% a year, that is worth " + _fmt(real, 2) + " in today's money, a real yearly rate of " +
    _pct(_sub1(realF)) + ".";
}
