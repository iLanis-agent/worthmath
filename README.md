# Worth Math

Inflation and purchasing power arithmetic. At 3% a year, 100 later buys only what 74.41 buys today.

## What it computes

- **The shrink truth** - what a sum later buys in today's terms after steady yearly price rises, what the same basket would cost, and the total price change.
- **The raise truth** - a pay raise against inflation, worked out exactly (1 + raise) / (1 + inflation) - 1, next to the subtraction shortcut.
- **The savings truth** - a sum growing at a yearly rate, then the same sum in today's money, with the real yearly rate.

Amounts are 0 to 999999999999 with up to 2 decimals. Rates are percents from -50 to 100 with up to 2 decimals. Years are whole numbers from 0 to 100. Rates are applied as the same percent every year and results are rounded half up to 2 decimals.

## Boundary

Arithmetic only. It does not forecast inflation or returns, does not know actual prices, taxes or fees, and gives no financial advice. Every rate is the owner's own entry.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (BigInt fractions, no floating point).
- `oracle.py` - the Python mirror (fractions.Fraction) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (68 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/worthmath/
Repo: https://github.com/iLanis-agent/worthmath
