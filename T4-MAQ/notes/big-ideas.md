# Big ideas: how the whole course fits together

The final paper looks like twelve separate questions, but the same few ideas run through all of them. This page shows the paper's shape over 2022–2025, then nine ideas that unlock most of its marks. Each idea has **spot it** (how to recognise it), **do it** (the method) and **check it** (how to catch a mistake), with a short example.

## Map of the paper

One paper, 3 hours, 180 marks (178 in 2024). The order of questions has been very stable. Marks below are counted from the final mark schemes.

| Question type | 2022 | 2023 | 2024 | 2025 | Notes |
|---|---|---|---|---|---|
| Number and finance — percentages, ratio, reverse %, compound interest | Q1: 14 | Q1: 12 | Q1: 13 | Q1: 12 | [Number](../notes/number.md) |
| Complete the square → sketch → $f'(x)$ → tangent | Q2(e): 13 | Q2(d): 12 | Q3(d): 12 | Q3(c): 13 | [Algebra](../notes/algebra.md), [Calculus](../notes/calculus.md) |
| Plot a curve from a table, then draw a line to solve an equation | Q4: 13; Q10 (cubic): 22 | Q4: 15 | Q4: 17 | Q4: 16 | [Graphs](../notes/graphs.md) |
| Quadratic from a context, reject a root | Q2(c): 6 (show-that from a fraction equation) | Q3: 11 (area) | Q2: 12 (area); Q3(c): 4 (Pythagoras); Q8: 9 (time) | Q2: 9 (area); Q8: 9 (time) | [Algebra](../notes/algebra.md) |
| Sine rule, cosine rule, $\tfrac12ab\sin C$, sectors | Q11: 13 | Q11: 17 | Q11: 17 | Q11: 16 | [Trigonometry](../notes/trigonometry.md), [Mensuration](../notes/mensuration.md) |
| Solids — cones, spheres, pyramids, cylinders | Q12: 12 | Q12: 14 | Q12: 13 | Q12: 13 | [Mensuration](../notes/mensuration.md) |
| Statistics — grouped mean, histogram, cumulative frequency | Q7: 15 | Q7: 14 | Q7: 14 | Q5: 9 (mean, median, mode) | [Statistics](../notes/statistics.md) |
| Probability — tree diagrams, two-way tables | Q5: 8 | Q5: 7 | Q5: 7 | — | [Statistics](../notes/statistics.md) |
| Calculus — differentiate, integrate with $+C$, find $C$ | Q6: 12 | Q6: 9 | Q6: 11 | Q6: 12 | plus 3 for $f'(x)$ in the completing-square question |
| Functions — evaluate, inverse, composite, solve | — | Q6(a): 9 | Q6(a): 7 | Q6(a): 7 | [Algebra](../notes/algebra.md) |
| Vectors — paths, simplify, magnitude, collinear | Q8(b): 6 | Q10(a): 8 | Q10(a): 8 | Q10(a)–(b): 7 | [Vectors](../notes/vectors-matrices.md) |
| Circle theorems and similar figures | Q8(c), Q9(b) | Q9: 10 | Q9(a)–(b): 6 | Q3(a): 6; Q9: 7 | [Geometry](../notes/geometry.md) |
| Transformations — describe, draw, combine | Q3: 12 | — | — | Q7: 10 | [Vectors and transformations](../notes/vectors-matrices.md) |
| Smaller parts — variation, surds, simultaneous equations, bounds, bearings, speed–time area, trig graphs | yes | yes | yes | yes | 2–4 marks each |

**What this tells you.** About half the paper (80–100 marks) is the same six question types every year: number and finance, the completing-square chain, the graph with a line to draw, quadratics from a context, triangle trigonometry, and solids. Calculus adds about 12 marks every year. No matrix questions appeared in 2022–2025.

## 1. Rewrite into standard form first

Most methods only work once the expression is in one standard shape. Rewriting it is usually the method mark.

| Before you… | Get it into this form |
|---|---|
| Differentiate or integrate | a sum of $ax^n$: expand brackets, split fractions, $\sqrt x = x^{1/2}$, $\tfrac{4}{x^2} = 4x^{-2}$ |
| Solve a quadratic | $ax^2+bx+c = 0$ |
| Read a gradient or intercept | $y = mx+c$ |
| Find a turning point | $a(x+p)^2+q$ |
| Find an inverse | $y = \ldots$, swap, make $y$ the subject |

- **Spot it:** brackets, fractions or roots next to a calculus sign; a line written as $2y-x-2 = 0$; "find the turning point".
- **Do it:** rewrite first, as its own line of working.
- **Check it:** expand your rewritten form back — it should match the original.

*Example (2022 Q10(d)(i)).* $2y-x-2 = 0 \Rightarrow 2y = x+2 \Rightarrow y = \tfrac12x+1$: gradient $\tfrac12$, $y$-intercept 1, so the line can now be drawn.

*Example.* $\dfrac{d}{dx}\left(\dfrac{4}{x^2}\right)$: rewrite as $4x^{-2}$, then differentiate to $-8x^{-3}$.

## 2. Words → equation → solve → check against the context

Every year has at least one context that becomes a quadratic: an area, a Pythagoras triangle, or two journey times.

- **Spot it:** lengths written as $x+3$ or $6(x+2)$; "the total time was…"; "show that $x^2+\ldots = 0$".
- **Do it:** write the fact in words (area $= \tfrac12$ base × height; time $= \tfrac{\text{distance}}{\text{speed}}$; $a^2+b^2 = c^2$), substitute the expressions, then expand and rearrange to $= 0$. Solve and give **both** roots.
- **Check it:** reject the root that makes a length, speed or time negative, **with a reason**, then answer the actual question (the length, the time) with units.

*Example (2024 Q3(c)).* The sides of a right-angled triangle are $x+1$, $x+3$ and $x+5$.
$(x+1)^2+(x+3)^2 = (x+5)^2 \Rightarrow x^2-2x-15 = 0 \Rightarrow (x-5)(x+3) = 0$.
$x = -3$ makes $x+1$ negative, so reject it. $x = 5$, and the sides are 6, 8 and 10.

Full method: [Forming quadratics from a context](../notes/algebra.md).

## 3. A graph intersection is a solution

Where two graphs cross, both equations are true at once. So the $x$-values of the crossing points solve the equation "first graph = second graph".

- **Spot it:** "use your graph to solve…", "by drawing a suitable straight line…", "find the points of intersection".
- **Do it:** rearrange the new equation so one side is exactly the function already drawn. The other side is the line to draw. Draw it, then read the $x$-values to 1 d.p.
- **Check it:** substitute a read-off value into the original equation — it should come out close to 0. A cubic and a line usually give three answers.

*Example (2023 Q4(d)).* The curve $y = x^3-4x^2+4x+1$ is drawn. Solve $x^3-4x^2+2x = 0$.
Add $2x+1$ to both sides: $x^3-4x^2+4x+1 = 2x+1$. Draw $y = 2x+1$ and read $x = 0$, $0.6$, $3.4$.

The algebra version is the same idea: substitute the line into the curve and solve ([Algebra](../notes/algebra.md), "A line and a curve"). Full method: [Rearranging to find the line to draw](../notes/graphs.md).

## 4. Gradient = rate of change = derivative

One idea, three places on the paper.

| Where | Gradient means | Area under means |
|---|---|---|
| Distance–time graph | speed | — |
| Speed–time graph | acceleration | distance |
| Curve $y = f(x)$ | $f'(x)$, the gradient of the tangent | — |

- **Spot it:** "gradient at", "tangent", "rate", "acceleration", "how far did it travel".
- **Do it:** for a formula, differentiate and substitute $x$; for a drawn graph, use rise ÷ run (or draw a tangent); for distance, add the areas of the triangles and rectangles under the speed–time graph.
- **Check it:** the sign matches the picture (going down means negative); the gradient is 0 at a turning point; the tangent touches without crossing.

*Example (2025 Q3(c)).* $f(x) = 2x^2-8x+3$. $f'(x) = 4x-8$, so $f'(3) = 4$. The point is $(3, f(3)) = (3,-3)$. Tangent: $y+3 = 4(x-3)$, so $y = 4x-15$.

*Example (2024 Q3(d)(iv)).* For $-2(x-2)^2+3$, $f'(2) = 0$ — the gradient is zero at the vertex.

## 5. Scale factor: $k$ for lengths, $k^2$ for areas, $k^3$ for volumes

- **Spot it:** "similar", two shapes or solids of the same shape, map scales, "surface area of the larger…".
- **Do it:** find $k$ from a pair of matching lengths ($k = \tfrac{\text{new}}{\text{old}}$). Area ratio $k^2$, volume, mass and capacity ratio $k^3$. Given an area ratio, square-root it to get $k$; given a volume ratio, cube-root it.
- **Check it:** bigger shape, bigger answer; keep $k$ unrounded.

*Example (2025 Q3(a)).* Length scale factor 4, so volume $= 4^3\times125 = 8000$ cm³. Surface areas $60\,000$ and $150$: $k^2 = 400$, so $k = 20$.

*Example (2023 Q9(c)).* From surface areas, $k = \sqrt{226/94}$; then $V_{\text{small}} = 680 \div k^3 = 182$ cm³.

## 6. Work backwards with inverse operations

Many questions give you the result and ask for the start. Undo each step in reverse order.

| Forward | Backward |
|---|---|
| $\times 1.15$ (add 15% GST) | $\div 1.15$ |
| $f(x)$ | $f^{-1}(x)$: swap $x$ and $y$, make $y$ the subject |
| Differentiate | Integrate, then use the given point to find $C$ |
| $P\left(1+\tfrac{r}{100}\right)^n$ | divide by $P$, take the $n$th root, subtract 1, × 100 |
| Volume from $r$ | rearrange, then square-root or cube-root |

- **Spot it:** "original price", "before the increase", "find $f(x)$ given $f'(x)$", "find the rate", "find the radius".
- **Do it:** write the forward equation with the unknown, then undo it.
- **Check it:** put your answer forward through the original — you should get the given value.

*Example (2023 Q1(a)).* \$2400 is the price after a 15% increase: $x = 2400\div1.15 = \$2086.96$, not $2400\times0.85$.

*Example (2024 Q1(f)).* $560\left(1+\tfrac{r}{100}\right)^6 = 630.65 \Rightarrow r = \left(\sqrt[6]{\tfrac{630.65}{560}}-1\right)\times100 = 2\%$.

*Example (2025 Q6(f)).* $V'(x) = 4x-3$ and $V(0) = 2$: $V(x) = 2x^2-3x+C$, so $C = 2$.

## 7. Choose the right tool

Most of the time is lost deciding which formula to use, not using it.

| You know | You want | Use |
|---|---|---|
| Right angle | side or angle | Pythagoras, SOH CAH TOA |
| Two sides and the angle between them | third side | cosine rule |
| Three sides | an angle | cosine rule (rearranged) |
| A side and its opposite angle, plus one more | side or angle | sine rule |
| Two sides and the angle between them | area | $\tfrac12ab\sin C$ |
| Angle at the centre | arc or sector | $\tfrac{\theta}{360}\times2\pi r$ or $\tfrac{\theta}{360}\times\pi r^2$ |

| Quadratic | Best method |
|---|---|
| Factorises easily | factorise |
| Asked for 3 s.f. or "use the formula" | quadratic formula |
| Asked for the turning point, or surd form | complete the square |

- **Spot it:** label the diagram with what you know, then look at the table.
- **Do it:** write the formula with letters first, then substitute.
- **Check it:** the largest side faces the largest angle; angles in a triangle add to 180°.

*Example (2025 Q6(g)).* Three sides known, so use the cosine rule for the angle: $\cos A = \dfrac{20.2^2+16^2-18.5^2}{2\times20.2\times16}$, $A = 60.14°$. Then area $= \tfrac12\times20.2\times16\times\sin60.14° = 140$ km².

## 8. Later parts reuse earlier answers

Questions are built as chains. "Hence" and "using your answer to (a)" mean the work is already done.

- **Spot it:** "hence", "using part (b)", a value you have just found appearing in the diagram.
- **Do it:** carry the full calculator value forward. If you couldn't do the earlier part, use a given value, or your own answer — follow-through marks are still available.
- **Check it:** the chain makes sense end to end (the tangent you draw goes through the vertex you found, and so on).

*Examples.* 2025 Q1(b)(iii) is "(b)(ii) × 2.75". 2023 Q12(a)(iii) is "(a)(ii) answer × 0.8". 2024 Q11(a)(iv) uses the side from (a)(i). The completing-square chain (2022–2025) goes: complete the square → sketch using the vertex → $f'(x)$ → gradient at a point → tangent equation → draw the tangent on your sketch.

## 9. Estimate first to catch nonsense

The course asks you to "apply appropriate checks of accuracy" (E1.13). A 5-second estimate catches a calculator slip that would cost every remaining mark in the chain.

- **Spot it:** any calculator answer, especially after a long chain.
- **Do it:** round each number to 1 s.f. and compute roughly; or ask "is this size sensible?".
- **Check it:** probabilities are between 0 and 1; a side of a triangle is shorter than the other two added; an angle in a triangle is under 180°; a percentage of a price is less than the price; the radius of a 1 kg ball is a few cm, not 30 m.

*Example (2022 Q12(b)).* $r^3 = 49.7\ldots$; since $3^3 = 27$ and $4^3 = 64$, $r$ is between 3 and 4. The answer $3.68$ cm fits.

*Example.* $\sqrt{(15.0)^2+(12.8)^2-2(15)(12.8)\cos68°}$ must be less than $15.0+12.8$. The 2025 answer is 15.7 cm.

See also: [Exam errors](../notes/exam-errors.md) · [Study guide](../notes/study-guide.md) · [Formulas](../FORMULAS.md)
