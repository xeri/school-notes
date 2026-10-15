# Vectors, matrices and transformations

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

Describing a transformation fully is worth as much as performing it. Each needs specific information:

| Transformation | Must state |
|---|---|
| **Reflection** (M) | the equation of the mirror line, e.g. $y = x$ |
| **Rotation** (R) | the angle, the direction (clockwise/anticlockwise), **and** the centre |
| **Translation** (T) | the column vector |
| **Enlargement** (E) | the scale factor **and** the centre |

**Reflection.** In $y = x$, the point $(a,b) \mapsto (b,a)$. In $y = -x$, $(a,b) \mapsto (-b,-a)$. In the $x$-axis, $(a,b)\mapsto(a,-b)$.

**Rotation.** About the origin:
- 90° anticlockwise: $(a,b)\mapsto(-b,a)$
- 180°: $(a,b)\mapsto(-a,-b)$
- 90° clockwise: $(a,b)\mapsto(b,-a)$

For a rotation about another centre, use tracing paper or find the centre by constructing the perpendicular bisectors of two lines joining corresponding points.

**Enlargement.** Each point moves along the line from the centre so that its distance from the centre is multiplied by the scale factor $k$.

- $k>1$ — larger
- $0<k<1$ — smaller (still called an enlargement)
- $k<0$ — the image is on the **opposite side of the centre** and inverted

An enlargement of scale factor $k$ multiplies lengths by $k$ and **areas by $k^2$**.

*Example.* Enlarge $(5,3)$ by scale factor $-2$ about the origin: the image is $(-10,-6)$.

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
