# Algebra

## Expanding and factorising

$$3x(2x-4y) = 6x^2 - 12xy$$
$$(x+4)(x-7) = x^2 - 3x - 28$$
$$(2x-3)^2 = 4x^2 - 12x + 9$$

Four factorising patterns you must recognise:

| Form | Method | Example |
|---|---|---|
| Common factor | take it out | $9x^2+15xy = 3x(3x+5y)$ |
| Grouping $ax+bx+kay+kby$ | pair up | $2x+6y+ax+3ay = 2(x+3y)+a(x+3y) = (2+a)(x+3y)$ |
| Difference of two squares $a^2x^2-b^2y^2$ | $(ax+by)(ax-by)$ | $9x^2-25y^2 = (3x+5y)(3x-5y)$ |
| Perfect square $a^2+2ab+b^2$ | $(a+b)^2$ | $x^2+10x+25 = (x+5)^2$ |
| Quadratic $ax^2+bx+c$ | find factors | see below |

**Factorising $x^2+bx+c$.** Find two numbers multiplying to $c$ and adding to $b$:

$$x^2+2x-15 = (x+5)(x-3)$$

**Factorising $ax^2+bx+c$ with $a \neq 1$.** Find two numbers multiplying to $ac$ and adding to $b$, then split the middle term:

$$6x^2+11x-10:\quad ac = -60,\ \text{need } +15 \text{ and } -4$$
$$= 6x^2+15x-4x-10 = 3x(2x+5)-2(2x+5) = (3x-2)(2x+5)$$

## Algebraic fractions

Same rules as numerical fractions — common denominator to add, multiply by the reciprocal to divide.

$$\frac{x}{3}+\frac{x-4}{2} = \frac{2x+3(x-4)}{6} = \frac{5x-12}{6}$$

$$\frac{3x}{4}\times\frac{9x}{10} = \frac{27x^2}{40} \qquad \frac{2x}{3}\div\frac{4x}{9} = \frac{2x}{3}\times\frac{9}{4x} = \frac32$$

**Simplifying rational expressions** — factorise top and bottom, then cancel common **factors** (never individual terms):

$$\frac{x^2+2x}{x^2+4x+4} = \frac{x(x+2)}{(x+2)^2} = \frac{x}{x+2}$$

## Indices in algebra

$$\left(\frac{2x^5}{3}\right)^3 = \frac{8x^{15}}{27}$$

Index equations: write both sides to the same base.

$$32^x = 2 \Rightarrow (2^5)^x = 2^1 \Rightarrow 5x = 1 \Rightarrow x = \tfrac15$$

## Rearranging formulae

Do the same operation to both sides, aiming to isolate the subject.

**When the subject appears twice**, gather its terms on one side and factorise:

$$y = \frac{ax+b}{x-c}$$
$$y(x-c) = ax+b \Rightarrow yx - yc = ax + b \Rightarrow yx - ax = b + yc$$
$$x(y-a) = b+yc \Rightarrow x = \frac{b+yc}{y-a}$$

## Linear equations and inequalities

$$\frac{3x-1}{4} = \frac{x+5}{3} \Rightarrow 3(3x-1) = 4(x+5) \Rightarrow 9x-3 = 4x+20 \Rightarrow x = \tfrac{23}{5}$$

**Inequalities** work the same way, with one rule: multiplying or dividing by a **negative** number reverses the sign.

$$-3x + 2 \leqslant 11 \Rightarrow -3x \leqslant 9 \Rightarrow x \geqslant -3$$

Show the solution on a number line with a filled circle for $\leqslant$ or $\geqslant$ and an open circle for $<$ or $>$.

## Simultaneous equations

**Elimination.** Match the coefficients of one unknown, then add or subtract.

$$3x+2y = 16 \quad (1)$$
$$5x-3y = 5 \quad (2)$$

Match the $y$ coefficients: $(1)\times3$ gives $9x+6y = 48$, and $(2)\times2$ gives $10x-6y = 10$.

Add: $19x = 58$, so $x = \tfrac{58}{19}$.

Non-integer answers are legitimate — do not assume you have gone wrong. Substitute back into **the equation you did not use for the second unknown** to check.

A pair with whole-number roots, for comparison:

$$3x+2y = 16 \quad (1)$$
$$5x-2y = 16 \quad (2)$$

Add (the $y$ terms already cancel): $8x = 32$, so $x = 4$. From (1): $12+2y = 16$, so $y = 2$. Check in (2): $20-4 = 16$ ✓

**Substitution.** Make one unknown the subject and substitute.

$$y = 2x-1,\quad 3x+y = 9 \Rightarrow 3x+2x-1 = 9 \Rightarrow x = 2,\ y = 3$$

Graphically, the solution is the point where the two lines cross.

## Quadratic equations

**Three methods — pick the right one.**

**1. Factorising** (when it factorises neatly):

$$x^2-7x+12 = 0 \Rightarrow (x-3)(x-4) = 0 \Rightarrow x = 3 \text{ or } 4$$

**2. Completing the square** (also gives the turning point):

$$x^2+bx+c = \left(x+\frac b2\right)^2 - \frac{b^2}{4} + c$$

$$x^2+6x-1 = (x+3)^2 - 9 - 1 = (x+3)^2 - 10$$
$$(x+3)^2 = 10 \Rightarrow x = -3\pm\sqrt{10}$$

The minimum of $y = (x+3)^2-10$ is at $(-3, -10)$ — read the turning point straight off the completed square.

If $a \neq 1$, factor it out first: $2x^2+8x+3 = 2\left[(x+2)^2-4\right]+3 = 2(x+2)^2 - 5$.

**3. The formula** (always works):

$$x = \frac{-b\pm\sqrt{b^2-4ac}}{2a}$$

$$2x^2+5x-3 = 0:\quad x = \frac{-5\pm\sqrt{25+24}}{4} = \frac{-5\pm7}{4} = \tfrac12 \text{ or } -3$$

The **discriminant** $b^2-4ac$ tells you the number of roots: positive → two, zero → one repeated, negative → none.

## Sequences

**Linear (arithmetic).** Constant first difference $d$:

$$n\text{th term} = dn + (a_1 - d)$$

For 5, 9, 13, 17, …: $d = 4$, so $4n+1$.

**Quadratic.** Constant **second** difference. The $n^2$ coefficient is half the second difference.

For 3, 8, 15, 24, …: first differences 5, 7, 9; second difference 2, so the $n^2$ coefficient is 1. Subtract $n^2$ (1, 4, 9, 16) to leave 2, 4, 6, 8 — which is $2n$. So the $n$th term is $n^2+2n$.

**Cubic.** Constant third difference; the $n^3$ coefficient is the third difference ÷ 6.

**Exponential (geometric).** Constant ratio $r$: $n$th term $= ar^{n-1}$. For 3, 6, 12, 24, …: $3\times2^{n-1}$.

**Combinations** can mix these, e.g. $2^n + n$.

## Variation

Write the proportion, find $k$, then use it.

| Statement | Equation |
|---|---|
| $y$ is directly proportional to $x$ | $y = kx$ |
| $y$ is proportional to the square of $x$ | $y = kx^2$ |
| $y$ is inversely proportional to $x$ | $y = \tfrac kx$ |
| $y$ is inversely proportional to $x^2$ | $y = \tfrac{k}{x^2}$ |

*Example.* $y$ is inversely proportional to $\sqrt{x}$, and $y = 4$ when $x = 9$. Then $k = 4\times3 = 12$, so $y = \tfrac{12}{\sqrt x}$ and when $x = 36$, $y = 2$.

## Functions

Notation: $f(x) = 3x-5$, or $f: x \mapsto 3x-5$. Then $f(4) = 7$.

**Inverse function** $f^{-1}(x)$ — swap and rearrange. Write $y = 3x-5$, solve for $x$: $x = \tfrac{y+5}{3}$, so

$$f^{-1}(x) = \frac{x+5}{3}$$

Check: $f^{-1}(7) = 4$ ✓ — the inverse undoes the function.

**Composite function** $gf(x) = g[f(x)]$ — apply $f$ **first**, then $g$.

With $f(x) = 3x-5$ and $g(x) = x^2$:

$$gf(x) = (3x-5)^2 \qquad fg(x) = 3x^2-5$$

These differ — the order matters. $gf(2) = 1$ while $fg(2) = 7$.
