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

$$\frac{2x^2-x-1}{x^2-1} = \frac{(2x+1)(x-1)}{(x+1)(x-1)} = \frac{2x+1}{x+1}$$

**Subtracting** — put the second numerator in a bracket so the minus sign reaches every term:

$$\frac{2}{x-1}-\frac{1}{x+2} = \frac{2(x+2)-(x-1)}{(x-1)(x+2)} = \frac{x+5}{(x-1)(x+2)}$$

**Solving an equation with algebraic fractions** — multiply every term by the common denominator to clear the fractions:

$$\frac{3}{x+1}+\frac{2}{x-2} = 1$$
$$3(x-2)+2(x+1) = (x+1)(x-2)$$
$$5x-4 = x^2-x-2 \Rightarrow x^2-6x+2 = 0$$
$$x = \frac{6\pm\sqrt{36-8}}{2} = 3\pm\sqrt7, \text{ so } x = 5.65 \text{ or } 0.354$$

**Mark-losing errors:** cancelling terms instead of factors ($\tfrac{x+2}{x}$ is not $2$); $-(x-1)$ written as $-x-1$; multiplying only some terms by the common denominator, especially the right-hand side.

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

Add: $19x = 58$, so $x = \tfrac{58}{19}$. Substitute into (1): $2y = 16-\tfrac{174}{19} = \tfrac{130}{19}$, so $y = \tfrac{65}{19}$.

Non-integer answers are legitimate — do not assume you have gone wrong. Substitute back into **the equation you did not use for the second unknown** to check.

A pair with whole-number roots, for comparison:

$$3x+2y = 16 \quad (1)$$
$$5x-2y = 16 \quad (2)$$

Add (the $y$ terms already cancel): $8x = 32$, so $x = 4$. From (1): $12+2y = 16$, so $y = 2$. Check in (2): $20-4 = 16$ ✓

**Substitution.** Make one unknown the subject and substitute.

$$y = 2x-1,\quad 3x+y = 9 \Rightarrow 3x+2x-1 = 9 \Rightarrow x = 2,\ y = 3$$

Graphically, the solution is the point where the two lines cross.

**A line and a curve.** Substitute the line into the curve to get a quadratic. Each root gives one intersection point.

$$y = x+1,\quad y = x^2-5 \Rightarrow x^2-5 = x+1 \Rightarrow x^2-x-6 = 0 \Rightarrow (x-3)(x+2) = 0$$

So $x = 3$ or $x = -2$, and the points are $(3, 4)$ and $(-2, -1)$.

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

**Turning points from the completed square.** $y = a(x+p)^2+q$ has its turning point at $(-p,\ q)$ and line of symmetry $x = -p$. It is a **minimum** if $a > 0$ and a **maximum** if $a < 0$.

*Worked example (2025 type).* $2x^2-8x+3 = 2(x^2-4x)+3 = 2\left[(x-2)^2-4\right]+3 = 2(x-2)^2-5$. Minimum point $(2, -5)$; the $y$-intercept is $3$. Sketch a U through $(0,3)$ with vertex $(2,-5)$.

*Worked example.* $3x^2-12x+5 = 3\left[(x-2)^2-4\right]+5 = 3(x-2)^2-7$, minimum $(2,-7)$.

*Worked example — a maximum.* $y = -x^2+6x-4 = -(x^2-6x)-4 = -\left[(x-3)^2-9\right]-4 = -(x-3)^2+5$. Maximum point $(3, 5)$.

**Mark-losing errors:** the sign of the $x$-coordinate — $(x+3)^2-10$ turns at $x = -3$, not $+3$; forgetting to multiply the $-\tfrac{b^2}{4}$ term by $a$ when $a \neq 1$; stating "turning point" without saying whether it is a maximum or minimum when asked.

**3. The formula** (always works):

$$x = \frac{-b\pm\sqrt{b^2-4ac}}{2a}$$

$$2x^2+5x-3 = 0:\quad x = \frac{-5\pm\sqrt{25+24}}{4} = \frac{-5\pm7}{4} = \tfrac12 \text{ or } -3$$

The **discriminant** $b^2-4ac$ tells you the number of roots: positive → two, zero → one repeated, negative → none.

**Quadratic inequalities.** Rearrange to $ax^2+bx+c$ compared with 0 (with $a>0$), solve the equation, then picture the U-shaped graph. "$\leqslant 0$" is **between** the roots; "$> 0$" is **outside** them.

$$x^2 \leqslant 9 \Rightarrow x^2-9 \leqslant 0 \Rightarrow -3 \leqslant x \leqslant 3 \qquad x^2-x-6 > 0 \Rightarrow x < -2 \text{ or } x > 3$$

## Forming quadratics from a context

The 2023, 2024 and 2025 finals each had 11–25 marks of quadratics built from a context. The steps are always the same:

1. **Write the fact in words**, then substitute the expressions.
2. **Expand and rearrange** to $ax^2+bx+c = 0$ (often a "show that" — see below).
3. **Solve**, giving both roots.
4. **Reject** the root that is impossible in the context, **with a reason**.
5. **Answer the question asked** — usually a length or a time, not $x$ — with units.

| Context | Fact to write | Final |
|---|---|---|
| Area of a rectangle or parallelogram | area $=$ base × height | 2023 Q3: $(x+4)(x+3) = 156$; 2024 Q2: $x(x-1.5) = 52$ |
| Area of a triangle | area $= \tfrac12$ base × height | 2025 Q2: $300 = \tfrac12\cdot6(x+2)\cdot4(x+2)$ |
| Right-angled triangle | $a^2+b^2 = c^2$ | 2024 Q3(c) |
| Two parts of a journey | time $= \dfrac{\text{distance}}{\text{speed}}$, times add to the total | 2024 Q8; 2025 Q8 |

*Worked example (2024 Q3(c)) — Pythagoras.* A right-angled triangle has sides $x+1$, $x+3$ and hypotenuse $x+5$.

$$(x+1)^2+(x+3)^2 = (x+5)^2$$
$$x^2+2x+1+x^2+6x+9 = x^2+10x+25$$
$$x^2-2x-15 = 0$$
$$(x-5)(x+3) = 0 \Rightarrow x = 5 \text{ or } x = -3$$

Reject $x = -3$: the side $x+1$ would be $-2$, and a length cannot be negative. So $x = 5$ and the sides are 6, 8 and 10 cm.

*Worked example (2024 Q2) — area.* A shape has base $x$ m and perpendicular height $(x-1.5)$ m, and its area is 52 m².

$$x(x-1.5) = 52 \Rightarrow x^2-1.5x-52 = 0 \Rightarrow 2x^2-3x-104 = 0$$
$$(x-8)(2x+13) = 0 \Rightarrow x = 8 \text{ or } x = -6.5$$

Reject $-6.5$ (a negative length). The base is 8 m and the height 6.5 m. Doubling to clear the decimal made it easier to factorise.

*Worked example (2024 Q8 equation) — times.* The times $\dfrac{12}{x}$ hours and $\dfrac{26}{x+10}$ hours add to 2 hours 48 minutes. Convert first: 48 min $= 0.8$ h, so the total is 2.8 h.

$$\frac{12}{x}+\frac{26}{x+10} = 2.8$$

Multiply **every** term by the common denominator $x(x+10)$:

$$12(x+10)+26x = 2.8(x^2+10x)$$
$$38x+120 = 2.8x^2+28x$$
$$2.8x^2-10x-120 = 0 \Rightarrow 7x^2-25x-300 = 0$$
$$x = \frac{25\pm\sqrt{25^2-4(7)(-300)}}{2(7)} = \frac{25\pm95}{14} \Rightarrow x = 8.57 \text{ or } x = -5$$

Reject $-5$: a speed cannot be negative. The first part takes $\dfrac{12}{8.571\ldots} = 1.40$ hours (2 d.p.), which is 84 minutes.

*Same method, 2025 Q8.* $\dfrac{12}{x-40}+\dfrac{50}{x} = \dfrac{11}{5}$ gave $11x^2-750x+10\,000 = 0$, so $x = 50$ or $18.18\ldots$. The scheme rejects 18.18 — it makes the speed $x-40$ negative. Then the time is $\dfrac{12}{50-40} = 1.2$ hours (1 hour 12 minutes).

**Mark-losing errors:** mixing hours and minutes (2 h 48 min is 2.8 h, not 2.48 h); multiplying only the fractions, not the right-hand side, by the common denominator; giving only the positive root without showing the other was rejected; stopping at $x = 5$ when the question asks for the sides.

## "Show that" technique

When the answer is printed in the question, every mark is for the working, and the last mark is usually an S mark for reaching the result.

1. Start from the information in the question, **never** from the answer.
2. Write one step per line: substitute, multiply out, collect.
3. End on a line that matches the printed result **exactly**, then write "as required" or "shown".
4. For a decimal result, show the unrounded value first, then round to the printed value.
5. If you cannot show it, use the printed result in the next parts anyway.

*Worked example (2025 Q2(b)(i)).* A triangle has base $6(x+2)$ m, perpendicular height $4(x+2)$ m and area 300 m². Show that $x^2+4x-21 = 0$.

$$300 = \tfrac12\times6(x+2)\times4(x+2) \qquad \text{(M)}$$
$$600 = 24(x+2)^2 \qquad \text{(M)}$$
$$25 = x^2+4x+4$$
$$x^2+4x-21 = 0 \quad \text{as required} \qquad \text{(S)}$$

Then (b)(ii): $(x+7)(x-3) = 0$, so $x = 3$ or $x = -7$ — the scheme wanted **both**. In (b)(iii), $x = 3$ gives base 30 m and height 20 m.

*Worked example (2022 Q2(c)(i)) — clearing a fraction.* Show that $3x-\dfrac5x = x-1$ gives $2x^2+x-5 = 0$.

$$x\times\left(3x-\frac5x\right) = x\times(x-1) \qquad \text{(multiply)}$$
$$3x^2-5 = x^2-x \qquad \text{(expand)}$$
$$2x^2+x-5 = 0 \qquad \text{(simplify)}$$

*Worked example (2025 Q11(a)(i)) — a decimal.* Show that $AC = 15.0$ cm to 1 d.p.

$$\frac{AC}{\sin54°} = \frac{17.2}{\sin68°} \Rightarrow AC = \frac{17.2\sin54°}{\sin68°} = 15.0079\ldots = 15.0 \text{ cm (1 d.p.)}$$

Writing only "$= 15.0$" would not show anything — the unrounded value is the evidence.

**Mark-losing errors:** working backwards from the printed answer; jumping from the substitution straight to the result; rounding before the last line; no final statement.

## Sequences

**Linear (arithmetic).** Constant first difference $d$:

$$n\text{th term} = dn + (a_1 - d)$$

For 5, 9, 13, 17, …: $d = 4$, so $4n+1$.

**Quadratic.** Constant **second** difference. The $n^2$ coefficient is half the second difference.

For 3, 8, 15, 24, …: first differences 5, 7, 9; second difference 2, so the $n^2$ coefficient is 1. Subtract $n^2$ (1, 4, 9, 16) to leave 2, 4, 6, 8 — which is $2n$. So the $n$th term is $n^2+2n$.

*Quadratic with $a \neq 1$.* 2, 9, 20, 35, …: first differences 7, 11, 15; second difference 4, so the $n^2$ coefficient is 2. Subtract $2n^2$ (2, 8, 18, 32) to leave 0, 1, 2, 3, which is $n-1$. So the $n$th term is $2n^2+n-1$. Check: $n = 4$ gives $32+4-1 = 35$ ✓

**Cubic.** Constant third difference; the $n^3$ coefficient is the third difference ÷ 6.

*Example.* 2, 9, 28, 65, …: differences 7, 19, 37; then 12, 18; then 6. So the $n^3$ coefficient is $6\div6 = 1$. Subtract $n^3$ (1, 8, 27, 64) to leave 1, 1, 1, 1, so the $n$th term is $n^3+1$.

**Is a number in the sequence?** Set the $n$th term equal to it and solve. For $4n+1 = 100$, $n = 24.75$ — not a whole number, so 100 is not a term.

**Exponential (geometric).** Constant ratio $r$: $n$th term $= ar^{n-1}$. For 3, 6, 12, 24, …: $3\times2^{n-1}$.

**Combinations** can mix these, e.g. $2^n + n$.

**Mark-losing errors:** writing $n+4$ for a sequence going up in 4s (the difference is the coefficient of $n$: $4n+\ldots$); using the first difference as the $n^2$ coefficient instead of half the second difference; not checking the formula against a given term.

## Variation

Write the proportion, find $k$, then use it.

| Statement | Equation |
|---|---|
| $y$ is directly proportional to $x$ | $y = kx$ |
| $y$ is proportional to the square of $x$ | $y = kx^2$ |
| $y$ is inversely proportional to $x$ | $y = \tfrac kx$ |
| $y$ is inversely proportional to $x^2$ | $y = \tfrac{k}{x^2}$ |

*Example.* $y$ is inversely proportional to $\sqrt{x}$, and $y = 4$ when $x = 9$. Then $k = 4\times3 = 12$, so $y = \tfrac{12}{\sqrt x}$ and when $x = 36$, $y = 2$.

More variation examples and errors are in [Number](../notes/number.md).

**Graphical inequalities and regions** (Inequalities: regions in the course skills) are in [Coordinate geometry and graphs](../notes/graphs.md), because they need straight-line equations.

## Functions

Notation: $f(x) = 3x-5$, or $f: x \mapsto 3x-5$. Then $f(4) = 7$.

**Inverse function** $f^{-1}(x)$ — swap and rearrange. Write $y = 3x-5$, solve for $x$: $x = \tfrac{y+5}{3}$, so

$$f^{-1}(x) = \frac{x+5}{3}$$

Check: $f^{-1}(7) = 4$ ✓ — the inverse undoes the function.

**Composite function** $gf(x) = g[f(x)]$ — apply $f$ **first**, then $g$.

With $f(x) = 3x-5$ and $g(x) = x^2$:

$$gf(x) = (3x-5)^2 \qquad fg(x) = 3x^2-5$$

These differ — the order matters. $gf(2) = 1$ while $fg(2) = 7$.

**Inverse when $x$ appears twice.** For $f(x) = \dfrac{2x+1}{x-3}$, write $y = \dfrac{2x+1}{x-3}$ and make $x$ the subject:

$$y(x-3) = 2x+1 \Rightarrow xy-2x = 3y+1 \Rightarrow x(y-2) = 3y+1 \Rightarrow f^{-1}(x) = \frac{3x+1}{x-2}$$

*Worked example (2023 type).* $g(x) = 4-2x^2$ and $h(x) = \dfrac{x+6}{2}$.

- $h^{-1}(x)$: $y = \tfrac{x+6}{2} \Rightarrow x = 2y-6$, so $h^{-1}(x) = 2x-6$
- $hg(x) = h(4-2x^2) = \dfrac{4-2x^2+6}{2} = 5-x^2$
- Solve $hg(x) = -7$: $5-x^2 = -7$, so $x^2 = 12$ and $x = \pm2\sqrt3$

**Undoing:** $f^{-1}f(x) = x$ and $ff^{-1}(x) = x$.

**Mark-losing errors:** $f^{-1}(x)$ is the inverse function, **not** $\dfrac{1}{f(x)}$; doing $gf$ in the wrong order ($f$ is applied first, because it is nearest to $x$); leaving the inverse in terms of $y$.
