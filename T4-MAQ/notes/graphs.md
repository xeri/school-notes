# Coordinate geometry and graphs

## Straight lines

$$y = mx + c$$

$m$ is the gradient, $c$ the $y$-intercept.

**Gradient from two points:**

$$m = \frac{y_2-y_1}{x_2-x_1}$$

Through $(1,3)$ and $(-2,-9)$: $m = \dfrac{-9-3}{-2-1} = \dfrac{-12}{-3} = 4$.

**Length of a line segment** (Pythagoras):

$$\text{length} = \sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$$

From $(1,3)$ to $(5,6)$: $\sqrt{16+9} = 5$.

**Midpoint** — average the coordinates:

$$\left(\frac{x_1+x_2}{2},\ \frac{y_1+y_2}{2}\right)$$

Midpoint of $(1,3)$ and $(5,6)$ is $(3, 4.5)$.

**Finding the equation.** Get $m$, then substitute one point to find $c$.

Through $(1,3)$ with $m = 4$: $3 = 4(1)+c$, so $c = -1$ and $y = 4x-1$.

Equivalently, use $y-y_1 = m(x-x_1)$: $y-3 = 4(x-1)$, which gives $y = 4x-1$ again.

## Parallel and perpendicular lines

- **Parallel** lines have the **same gradient**.
- **Perpendicular** gradients multiply to $-1$: $m_2 = -\dfrac{1}{m_1}$.

A line parallel to $y = 4x-1$ through $(0,-3)$: same gradient 4, so $y = 4x-3$.

A line perpendicular to $y = 3x+1$ has gradient $-\tfrac13$.

A line perpendicular to the one through $(1,3)$ and $(-2,-9)$: that line has $m = 4$, so the perpendicular has $m = -\tfrac14$.

## Travel and conversion graphs

**Distance–time graph:** gradient = speed. Horizontal = stationary. Steeper = faster.

**Speed–time graph:** gradient = acceleration; **area under the line = distance travelled**.

For a linear speed–time graph, split the area into triangles and rectangles.

*Example.* A car accelerates from rest to 20 m/s in 8 s, holds 20 m/s for 10 s, then decelerates to rest in 4 s.

- Acceleration: $20/8 = 2.5$ m/s²
- Deceleration: $20/4 = 5$ m/s² (the gradient is $-5$)
- Distance: $\tfrac12(8)(20) + 10(20) + \tfrac12(4)(20) = 80+200+40 = 320$ m
- Average speed: $320/22 = 14.5$ m/s

**Conversion graphs** are straight lines through the origin when the quantities are proportional. Read across and down; state the units.

## Curves to recognise

| Function | Shape |
|---|---|
| $y = ax$ | straight line through the origin |
| $y = ax^2$ | parabola; minimum if $a>0$, maximum if $a<0$ |
| $y = ax^3$ | cubic, rotational symmetry about the origin |
| $y = \dfrac{a}{x}$ ($ax^{-1}$) | reciprocal — two branches, asymptotes at both axes |
| $y = \dfrac{a}{x^2}$ ($ax^{-2}$) | both branches above the $x$-axis when $a>0$ |
| $y = a^x$ ($a>1$) | exponential — rises steeply, never reaches zero |
| $y = ax^0$ | horizontal line $y = a$ |

Graphs in the exam are built from $ax^n$ with $n = -2, -1, 0, 1, 2, 3$, and sums of up to **three** such terms — e.g. $y = x^2 + \tfrac{4}{x} - 3$.

**Asymptote** — a line the curve approaches but never meets. For $y = \tfrac ax$, both axes are asymptotes, and there is no value at $x = 0$: leave that cell of the table blank.

## Drawing a curve from a table

1. Substitute each $x$ into the function, including negatives, and record $y$ to 1 d.p.
2. Choose scales that fit the full range of $y$ values.
3. Plot each point; join with a **single smooth curve** — no straight segments, no feathering.

## Solving equations graphically

To solve $f(x) = k$, draw the horizontal line $y = k$ and read the $x$-coordinates where it cuts the curve.

To solve $f(x) = g(x)$, draw both and read the $x$-coordinates of the intersections.

To solve $x^2 - 3x = 2$ from a drawn graph of $y = x^2-3x$, draw $y = 2$ and read off both roots. Give answers to the accuracy your scale supports — usually 1 d.p.

## Gradient of a curve

The gradient changes along a curve, so you estimate it at a point by drawing a **tangent**:

1. Place a ruler touching the curve at that point only, matching the curve's direction.
2. Draw a long tangent line.
3. Take two widely separated points **on the tangent** and compute $\Delta y / \Delta x$.

The tangent gradient at a maximum or minimum is zero.

## Exponential growth and decay

$$y = ka^x \text{ with } a>1 \text{ (growth)} \qquad y = ka^x \text{ with } 0<a<1 \text{ (decay)}$$

$y = a^{-x}$ with $a>1$ is also decay, because $a^{-x} = \left(\tfrac1a\right)^x$.

Growth curves rise slowly then steeply; decay curves fall steeply then flatten towards the $x$-axis without reaching it.

Real contexts: compound interest $P(1.04)^n$, depreciation $P(0.85)^n$, bacterial doubling $N_0 2^t$, radioactive decay.

## Calculus

Calculus is in the Term 3 course and has been in every final exam from 2022 to 2025. No objective list has been issued, so this section follows what those papers asked.

**Differentiation** gives the gradient function $f'(x)$: the gradient of the tangent at any $x$. Multiply by the power, then reduce the power by one.

$$f(x) = ax^n \Rightarrow f'(x) = anx^{n-1}$$

A constant term differentiates to 0. Expand brackets first: $g(x) = (2x+1)^2 = 4x^2+4x+1$, so $g'(x) = 8x+4$. Negative powers follow the same rule: $2x^{-1}$ differentiates to $-2x^{-2}$.

*Worked example.* $f(x) = 2x^2-8x+3$.

- Gradient function: $f'(x) = 4x-8$
- Gradient at $x = 3$: $f'(3) = 12-8 = 4$
- Point on the curve: $f(3) = 18-24+3 = -3$, so $(3,-3)$
- Tangent at that point: $y-(-3) = 4(x-3)$, so $y = 4x-15$
- Turning point where $f'(x) = 0$: $x = 2$, $f(2) = -5$, so the minimum is $(2,-5)$. This matches the completed square $2(x-2)^2-5$.

**Integration** reverses differentiation. Add one to the power, divide by the new power, and always add a constant $C$:

$$\int ax^n\,dx = \frac{ax^{n+1}}{n+1} + C \qquad (n \neq -1)$$

Expand or simplify first, so you integrate a sum of powers of $x$.

*Worked example.* $V'(x) = 4x-3$ and $V(0) = 2$. Integrating gives $V(x) = 2x^2-3x+C$. Substitute the known point: $2 = 0-0+C$, so $C = 2$ and $V(x) = 2x^2-3x+2$.
