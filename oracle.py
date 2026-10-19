#!/usr/bin/env python3
# Worth Math oracle - mirrors engine.js with fractions.Fraction and plain integer rounding (round half up).
import json, re
from fractions import Fraction
from math import floor

AMT_ERR = "amount must be a number from 0 to 999999999999 with at most 2 decimals"
RATE_ERR = "rate must be a percent from -50 to 100 with at most 2 decimals"
YEARS_ERR = "years must be a whole number from 0 to 100"

def pl(n, w): return f"{n} {w}" + ("" if n == 1 else "s")

def amount(t):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"[0-9]{1,12}(\.[0-9]{1,2})?", t):
        raise ValueError(AMT_ERR)
    return Fraction(t)

def rate(t):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"-?[0-9]{1,3}(\.[0-9]{1,2})?", t):
        raise ValueError(RATE_ERR)
    p = Fraction(t)
    if p < -50 or p > 100:
        raise ValueError(RATE_ERR)
    return p

def years(t):
    t = t.strip() if isinstance(t, str) else ""
    if not re.fullmatch(r"[0-9]{1,3}", t) or int(t) > 100:
        raise ValueError(YEARS_ERR)
    return int(t)

def fx(v, k):
    scaled = floor(abs(v) * 10**k + Fraction(1, 2))
    s = str(scaled).rjust(k + 1, "0")
    out = s[:-k] + "." + s[-k:] if k else s
    return ("-" if v < 0 and scaled != 0 else "") + out

def rt(p):
    s = fx(p, 2)
    return s.rstrip("0").rstrip(".") if "." in s else s

def pc(v): return fx(v * 100, 2) + "%"

def shrink_truth(a, r, y):
    a = amount(a); r = rate(r); n = years(y)
    f = (1 + r / 100) ** n
    return (f"At {rt(r)}% a year for {pl(n, 'year')}, {fx(a, 2)} later buys what {fx(a / f, 2)} buys today, "
            f"and what costs {fx(a, 2)} today would cost {fx(a * f, 2)} then. Prices change by {pc(f - 1)} in total.")

def raise_truth(g, i):
    g = rate(g); i = rate(i)
    real = (1 + g / 100) / (1 + i / 100) - 1
    return (f"With a raise of {rt(g)}% and inflation of {rt(i)}%, buying power changes by {pc(real)} "
            f"(subtracting the percents would give {pc((g - i) / 100)}). Matching inflation of {rt(i)}% takes a raise of {rt(i)}%.")

def savings_truth(a, s, i, y):
    a = amount(a); s = rate(s); i = rate(i); n = years(y)
    nominal = a * (1 + s / 100) ** n
    rf = (1 + s / 100) / (1 + i / 100)
    return (f"{fx(a, 2)} growing at a yearly rate of {rt(s)}% for {pl(n, 'year')} becomes {fx(nominal, 2)}. "
            f"With inflation of {rt(i)}% a year, that is worth {fx(a * rf ** n, 2)} in today's money, a real yearly rate of {pc(rf - 1)}.")

FNS = {"shrinkTruth": shrink_truth, "raiseTruth": raise_truth, "savingsTruth": savings_truth}
CASES = [
    ("shrinkTruth", ["100", "3", "10"]), ("shrinkTruth", ["100", "0", "10"]), ("shrinkTruth", ["100", "3", "0"]), ("shrinkTruth", ["100", "3", "1"]),
    ("shrinkTruth", ["1000", "2.5", "20"]), ("shrinkTruth", ["0", "3", "10"]), ("shrinkTruth", ["0.01", "7.25", "30"]), ("shrinkTruth", ["999999999999", "100", "100"]),
    ("shrinkTruth", ["100", "-2", "10"]), ("shrinkTruth", ["100", "-50", "5"]), ("shrinkTruth", ["100", "100", "1"]), ("shrinkTruth", ["250.50", "4", "25"]),
    ("shrinkTruth", ["100", "3.00", "10"]), ("shrinkTruth", [" 100 ", " 3 ", " 10 "]), ("shrinkTruth", ["100", "6", "12"]), ("shrinkTruth", ["20000", "8", "40"]),
    ("shrinkTruth", ["100", "-0", "3"]), ("shrinkTruth", ["100", "0.5", "100"]), ("shrinkTruth", ["100", "3", "100"]), ("shrinkTruth", ["1", "10", "7"]),
    ("shrinkTruth", ["-5", "3", "10"]), ("shrinkTruth", ["100.123", "3", "10"]), ("shrinkTruth", ["abc", "3", "10"]), ("shrinkTruth", ["1000000000000", "3", "10"]),
    ("shrinkTruth", ["100", "101", "10"]), ("shrinkTruth", ["100", "-51", "10"]), ("shrinkTruth", ["100", "3.125", "10"]), ("shrinkTruth", ["100", "x", "10"]),
    ("shrinkTruth", ["100", "3", "101"]), ("shrinkTruth", ["100", "3", "2.5"]), ("shrinkTruth", ["100", "3", "-1"]), ("shrinkTruth", ["100", "3", ""]),
    ("raiseTruth", ["3", "5"]), ("raiseTruth", ["5", "5"]), ("raiseTruth", ["8", "3"]), ("raiseTruth", ["0", "3"]),
    ("raiseTruth", ["3", "0"]), ("raiseTruth", ["10", "10"]), ("raiseTruth", ["2.5", "7.25"]), ("raiseTruth", ["-5", "4"]),
    ("raiseTruth", ["100", "-50"]), ("raiseTruth", ["-50", "100"]), ("raiseTruth", ["1", "18"]), ("raiseTruth", ["4.5", "4.5"]),
    ("raiseTruth", ["3", "abc"]), ("raiseTruth", ["101", "3"]), ("raiseTruth", ["3", "-51"]), ("raiseTruth", ["3.001", "3"]),
    ("savingsTruth", ["100", "4", "3", "10"]), ("savingsTruth", ["100", "3", "3", "10"]), ("savingsTruth", ["100", "2", "5", "10"]), ("savingsTruth", ["100", "4", "3", "0"]),
    ("savingsTruth", ["10000", "5", "2.5", "30"]), ("savingsTruth", ["500", "0", "3", "20"]), ("savingsTruth", ["500", "3", "0", "20"]), ("savingsTruth", ["1", "100", "100", "5"]),
    ("savingsTruth", ["1234.56", "6.5", "3.2", "17"]), ("savingsTruth", ["100", "-5", "2", "10"]), ("savingsTruth", ["999999999999", "10", "3", "100"]), ("savingsTruth", ["0", "4", "3", "10"]),
    ("savingsTruth", ["100", "4", "3", "1"]), ("savingsTruth", ["2000", "1.5", "4", "12"]), ("savingsTruth", ["x", "4", "3", "10"]), ("savingsTruth", ["100", "x", "3", "10"]),
    ("savingsTruth", ["100", "4", "x", "10"]), ("savingsTruth", ["100", "4", "3", "x"]), ("savingsTruth", ["100", "4", "101", "10"]), ("savingsTruth", ["100", "4", "3", "101"]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
