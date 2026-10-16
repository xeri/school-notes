# Vectors, transformations and matrices

## Vector notation

A vector has magnitude **and** direction, written as a column:

$$\mathbf{a} = \begin{pmatrix} x \\ y \end{pmatrix}$$

meaning $x$ across and $y$ up. It can also be written $\overrightarrow{AB}$ or $\mathbf{a}$.

**In handwritten answers you must mark a vector clearly** — underline it ($\underline{a}$) or use an arrow ($\overrightarrow{AB}$). An unmarked letter loses the mark.

Magnitude uses modulus signs:

$$|\mathbf{a}| = \sqrt{x^2+y^2}$$

$$\left|\begin{pmatrix}5\\-12\end{pmatrix}\right| = \sqrt{25+144} = 13$$

## Vector arithmetic

Add and subtract component by component; multiply each component by a scalar.

$$\begin{pmatrix}3\\-1\end{pmatrix}+\begin{pmatrix}2\\5\end{pmatrix} = \begin{pmatrix}5\\4\end{pmatrix} \qquad 3\begin{pmatrix}2\\-4\end{pmatrix} = \begin{pmatrix}6\\-12\end{pmatrix}$$

$-\mathbf{a}$ has the same magnitude as $\mathbf{a}$ but the opposite direction, so $\overrightarrow{BA} = -\overrightarrow{AB}$.

Parallel vectors are scalar multiples of each other: $\begin{pmatrix}2\\3\end{pmatrix}$ and $\begin{pmatrix}6\\9\end{pmatrix}$ are parallel, the second being three times the first.

## Vector geometry

**Route-finding.** To express a vector in terms of others, travel along the available arrows:

$$\overrightarrow{AC} = \overrightarrow{AB} + \overrightarrow{BC}$$

Going against an arrow makes it negative: $\overrightarrow{AC} = \overrightarrow{AB} - \overrightarrow{CB}$.

**Position vectors** are measured from the origin: $\overrightarrow{OA} = \mathbf{a}$. Then

$$\overrightarrow{AB} = \mathbf{b}-\mathbf{a}$$

(destination minus start — in that order).

The midpoint $M$ of $AB$ has position vector $\tfrac12(\mathbf{a}+\mathbf{b})$.

*Example.* $OABC$ is a parallelogram with $\overrightarrow{OA} = \mathbf{a}$ and $\overrightarrow{OC} = \mathbf{c}$. Then $\overrightarrow{OB} = \mathbf{a}+\mathbf{c}$, and $\overrightarrow{AC} = \mathbf{c}-\mathbf{a}$.

To **prove two lines are parallel**, show one vector is a scalar multiple of the other. To prove three points are **collinear**, show two vectors between them are parallel *and* share a point.

## Transformations

Transformation is a Term 3 topic in its own right, and the 2022 and 2025 finals both had a full question on it: describe three transformations, draw an image, and combine two transformations.

![Six transformation examples on grids: reflection in x equals minus 1; rotation 90 degrees clockwise about (1, minus 1); translation by the vector (minus 5, minus 4); enlargement with scale factor 2 and centre (minus 4, minus 4); enlargement with scale factor minus 2 and centre (1, 0); and a reflection in the x-axis followed by a rotation of 90 degrees anticlockwise about the origin, which equals a reflection in y equals x with invariant point (1, 1)](math-transformations.svg)

### Describing a single transformation fully

Name the transformation **in one word**, then give every piece of information it needs. Each piece is a separate mark.

| Transformation | Must state | Example answer |
|---|---|---|
| **Reflection** (M) | the equation of the mirror line | Reflection in the line $x = -1$ |
| **Rotation** (R) | the angle, the direction (clockwise or anticlockwise) **and** the centre | Rotation 90° clockwise about $(1,-1)$ |
| **Translation** (T) | the column vector | Translation by $\begin{pmatrix}-5 \\ -4\end{pmatrix}$ |
| **Enlargement** (E) | the scale factor **and** the centre | Enlargement, scale factor 2, centre $(-4,-4)$ |

A rotation of 180° needs no direction. A rotation of 90° clockwise is the same as 270° anticlockwise; either is accepted.

### Finding the missing information

**Mirror line.** Join a point to its image; the mirror line is the perpendicular bisector of that segment. In the first panel, $(1,2)$ and its image $(-3,2)$ have midpoint $(-1,2)$, and the line is vertical, so the mirror is $x = -1$.

Coordinate rules: in $y = x$, $(a,b)\mapsto(b,a)$; in $y = -x$, $(a,b)\mapsto(-b,-a)$; in the $x$-axis, $(a,b)\mapsto(a,-b)$; in the $y$-axis, $(a,b)\mapsto(-a,b)$; in $x = k$, $(a,b)\mapsto(2k-a,\ b)$.

**Centre of rotation.** Draw the perpendicular bisectors of two segments joining points to their images; the centre is where they cross. Or try likely centres with tracing paper. The **angle** is the angle between a line and its image — compare the direction of one edge before and after.

*Example.* The triangle $(1,1)$, $(3,1)$, $(1,2)$ maps to $(3,-1)$, $(3,-3)$, $(4,-1)$. The edge from $(1,1)$ to $(3,1)$ pointed right; its image from $(3,-1)$ to $(3,-3)$ points down — a quarter-turn clockwise. The perpendicular bisector of $(1,1)$ to $(3,-1)$ is $y = x-2$. The perpendicular bisector of $(3,1)$ to $(3,-3)$ is $y = -1$. They cross at $(1,-1)$, which is 2 units from both $(1,1)$ and $(3,-1)$. **Rotation 90° clockwise about $(1,-1)$.** (Pick pairs whose bisectors are not the same line — here $(1,2)\mapsto(4,-1)$ also gives $y = x-2$, which does not help.)

About the origin: 90° anticlockwise $(a,b)\mapsto(-b,a)$; 180° $(a,b)\mapsto(-a,-b)$; 90° clockwise $(a,b)\mapsto(b,-a)$.

**Translation vector.** Pick any point and count across, then up: $(1,1)\mapsto(-4,-3)$ is $\begin{pmatrix}-5 \\ -4\end{pmatrix}$. The top number is horizontal.

**Centre and scale factor of an enlargement.** Draw straight lines through each point and its image; they meet at the centre. Then

$$\text{scale factor} = \frac{\text{image length}}{\text{object length}}$$

with a **negative** sign if the image is on the opposite side of the centre and upside down.

- $k>1$ — larger
- $0<k<1$ — smaller (still called an enlargement; the 2025 mark scheme accepted "reduction")
- $k<0$ — the image is on the **opposite side of the centre** and inverted

*Example.* The triangle $(2,1)$, $(3,1)$, $(2,2)$ maps to $(-1,-2)$, $(-3,-2)$, $(-1,-4)$. The lines through corresponding points all pass through $(1,0)$. The edge of length 1 becomes length 2, and the image is on the far side of the centre, so this is an **enlargement, scale factor $-2$, centre $(1,0)$**. Check: $(1,0)+(-2)\big((2,1)-(1,0)\big) = (1,0)+(-2,-2) = (-1,-2)$ ✓

To **draw** an enlargement, multiply each point's vector from the centre by $k$: image $=$ centre $+\ k\times$(point $-$ centre). Enlarge $(5,3)$ by scale factor $-2$ about the origin: the image is $(-10,-6)$.

An enlargement of scale factor $k$ multiplies lengths by $k$ and **areas by $k^2$**.

### Combined transformations

$EF(A)$ means do $F$ **first**, then $E$ — the transformation nearest the shape acts first. The 2022 final marked "correct order: F then E" separately.

*Worked example.* $A$ has vertices $(1,1)$, $(3,1)$, $(1,2)$. $F$ is a reflection in the $x$-axis and $E$ is a rotation of 90° anticlockwise about the origin.

1. $F(A)$: $(a,b)\mapsto(a,-b)$ gives $(1,-1)$, $(3,-1)$, $(1,-2)$.
2. $EF(A)$: $(a,b)\mapsto(-b,a)$ gives $(1,1)$, $(1,3)$, $(2,1)$.
3. Compare with $A$: every $(a,b)$ has become $(b,a)$. So $EF$ is the **single transformation: reflection in the line $y = x$** (the 2025 final asked for exactly this kind of single equivalent).

With matrices the same result is $\begin{pmatrix}0&-1\\1&0\end{pmatrix}\begin{pmatrix}1&0\\0&-1\end{pmatrix} = \begin{pmatrix}0&1\\1&0\end{pmatrix}$, the matrix for reflection in $y = x$.

$FE$ is usually different from $EF$ — always check the order.

### Invariant points

An **invariant point** does not move under the transformation.

| Transformation | Invariant points |
|---|---|
| Reflection | every point on the mirror line |
| Rotation | only the centre |
| Enlargement ($k\neq1$) | only the centre |
| Translation (non-zero) | none |

In the combined example, the vertex $(1,1)$ lies on $y = x$, so it is invariant: it is in the same place in $A$ and $EF(A)$.

**Mark-losing errors:** giving two transformations ("a reflection and then a translation") when the question asks for a single transformation; using informal words ("flip", "turn", "move", "shrink") — use reflection, rotation, translation, enlargement; omitting the centre of a rotation or enlargement; writing a translation as coordinates $(-5,-4)$ instead of a column vector; doing $EF$ in the order $E$ then $F$.

## Matrices

A matrix is an array of numbers; its **order** is rows × columns.

**Addition and subtraction** need the same order, element by element.

**Scalar multiplication** multiplies every element.

**Multiplication.** $(m\times n)$ by $(n\times p)$ gives $(m\times p)$ — the inner dimensions must match. Each entry is a row of the first times a column of the second:

$$\begin{pmatrix}1&2\\3&4\end{pmatrix}\begin{pmatrix}5&6\\7&8\end{pmatrix} = \begin{pmatrix}1(5)+2(7) & 1(6)+2(8)\\3(5)+4(7) & 3(6)+4(8)\end{pmatrix} = \begin{pmatrix}19&22\\43&50\end{pmatrix}$$

Matrix multiplication is **not** commutative: $AB \neq BA$ in general.

**Special $2\times2$ matrices:**

$$\text{zero } \begin{pmatrix}0&0\\0&0\end{pmatrix} \qquad \text{identity } I = \begin{pmatrix}1&0\\0&1\end{pmatrix}$$

$AI = IA = A$.

**Determinant** of $A = \begin{pmatrix}a&b\\c&d\end{pmatrix}$:

$$|A| = ad-bc$$

**Inverse:**

$$A^{-1} = \frac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$$

Swap $a$ and $d$, negate $b$ and $c$, divide by the determinant. If $|A| = 0$ the matrix is **singular** and has no inverse.

*Example.* $A = \begin{pmatrix}3&1\\5&2\end{pmatrix}$, $|A| = 6-5 = 1$, so

$$A^{-1} = \begin{pmatrix}2&-1\\-5&3\end{pmatrix}$$

Check: $AA^{-1} = I$ ✓

## Transformation matrices

A $2\times2$ matrix acting on $\begin{pmatrix}x\\y\end{pmatrix}$ performs a transformation about the **origin**.

| Transformation | Matrix |
|---|---|
| Reflection in the $x$-axis | $\begin{pmatrix}1&0\\0&-1\end{pmatrix}$ |
| Reflection in the $y$-axis | $\begin{pmatrix}-1&0\\0&1\end{pmatrix}$ |
| Reflection in $y = x$ | $\begin{pmatrix}0&1\\1&0\end{pmatrix}$ |
| Reflection in $y = -x$ | $\begin{pmatrix}0&-1\\-1&0\end{pmatrix}$ |
| Rotation 90° anticlockwise | $\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ |
| Rotation 180° | $\begin{pmatrix}-1&0\\0&-1\end{pmatrix}$ |
| Rotation 90° clockwise | $\begin{pmatrix}0&1\\-1&0\end{pmatrix}$ |
| Enlargement, scale factor $k$ | $\begin{pmatrix}k&0\\0&k\end{pmatrix}$ |

**Finding the matrix of a transformation:** apply it to $\begin{pmatrix}1\\0\end{pmatrix}$ and $\begin{pmatrix}0\\1\end{pmatrix}$; the images become the first and second **columns**.

**Combined transformations.** $RM(a) = c$ means apply $M$ **first**, then $R$. As matrices, that is the product $RM$ — written in the opposite order to the sequence of operations. Singular matrices are excluded.

**Determinant and area.** The area of a shape is multiplied by $|{\det}|$ under the transformation. A reflection has determinant $-1$ (area preserved, orientation flipped); an enlargement by $k$ has determinant $k^2$.
