# Statistics and probability

## Probability basics

$$P(\text{event}) = \frac{\text{number of favourable outcomes}}{\text{total number of outcomes}}$$

Probability runs on a scale from **0** (impossible) to **1** (certain) and can be given as a fraction, decimal or percentage. Probabilities of all possible outcomes sum to 1.

$$P(\text{not } A) = 1 - P(A)$$

If $P(\text{rain}) = 0.35$ then $P(\text{no rain}) = 0.65$.

**Relative frequency** estimates probability from experimental data:

$$\text{relative frequency} = \frac{\text{number of times the event happened}}{\text{number of trials}}$$

The more trials, the closer it tends to the theoretical probability. In 200 spins a spinner lands on red 46 times, so $P(\text{red}) \approx 0.23$.

**Expected frequency** $=$ probability × number of trials. With $P = 0.23$ over 500 spins, expect about 115 reds.

## Combined events

**Possibility diagrams** — a grid of all outcomes, with each outcome a point. Two dice give a 6×6 grid of 36 equally likely outcomes. $P(\text{total} = 7) = \tfrac{6}{36} = \tfrac16$.

**Tree diagrams** — outcomes at the end of branches, probabilities beside them.

- **Along** the branches, **multiply** (AND)
- **Between** different complete paths, **add** (OR)
- The probabilities on each set of branches from a point sum to 1

*Without replacement* the second set of probabilities changes — the denominator drops by one.

*Example.* A bag holds 5 red and 3 blue counters; two are drawn without replacement.

$$P(\text{both red}) = \frac58\times\frac47 = \frac{20}{56} = \frac{5}{14}$$
$$P(\text{one of each}) = \frac58\times\frac37 + \frac38\times\frac57 = \frac{15}{56}+\frac{15}{56} = \frac{15}{28}$$

Checking that all path probabilities sum to 1 catches most errors.

## Collecting and displaying data

**Discrete** data takes separate values (shoe sizes, number of pets). **Continuous** data can take any value in a range (height, time).

| Diagram | Use |
|---|---|
| Bar chart | compare discrete categories; equal bar widths, gaps between bars |
| Pie chart | show proportions of a whole |
| Pictogram | counts with a stated key |
| Histogram | continuous data in class intervals; **no gaps** |
| Scatter diagram | relationship between two variables |
| Cumulative frequency curve | medians, quartiles, percentiles |

**Pie chart angles:**

$$\text{angle} = \frac{\text{frequency}}{\text{total}}\times360°$$

With a total of 72 and a category of 18: $\tfrac{18}{72}\times360 = 90°$. The angles must sum to 360°.

## Histograms with unequal intervals

When class widths differ, the **area** of each bar represents the frequency, and the vertical axis is **frequency density**:

$$\text{frequency density} = \frac{\text{frequency}}{\text{class width}}$$

| Height (cm) | Frequency | Width | Frequency density |
|---|---|---|---|
| $0 < h \leqslant 10$ | 8 | 10 | 0.8 |
| $10 < h \leqslant 20$ | 22 | 10 | 2.2 |
| $20 < h \leqslant 50$ | 30 | 30 | 1.0 |

Going the other way, frequency = frequency density × class width. Label the axis "Frequency density" — "Frequency" loses the mark.

## Averages and range

| Measure | Definition | Best when |
|---|---|---|
| **Mean** | $\dfrac{\sum x}{n}$ | data is fairly symmetric; uses every value |
| **Median** | the middle value when ordered | there are extreme values (outliers) |
| **Mode** | the most frequent value | data is categorical, or you want the most common |
| **Range** | highest − lowest | a quick measure of spread; distorted by outliers |

The mean is affected by every value, so one extreme result pulls it; the median is not. For 2, 3, 3, 4, 88 the mean is 20 but the median is 3 — the median describes this data better.

For an even number of values, the median is the mean of the middle two.

**From a frequency table:**

$$\text{mean} = \frac{\sum fx}{\sum f}$$

| $x$ | $f$ | $fx$ |
|---|---|---|
| 1 | 4 | 4 |
| 2 | 7 | 14 |
| 3 | 9 | 27 |
| | 20 | 45 |

Mean $= 45/20 = 2.25$.

## Grouped data

With grouped data you do not know the individual values, so you **estimate** the mean using the **midpoint** of each class:

$$\text{estimated mean} = \frac{\sum f\times\text{midpoint}}{\sum f}$$

| Class | Midpoint | $f$ | $f\times$mid |
|---|---|---|---|
| $0<x\leqslant10$ | 5 | 6 | 30 |
| $10<x\leqslant20$ | 15 | 14 | 210 |
| $20<x\leqslant30$ | 25 | 10 | 250 |
| | | 30 | 490 |

Estimated mean $= 490/30 = 16.3$.

The **modal class** is the class with the highest frequency — here $10<x\leqslant20$. With unequal widths, it is the class with the highest **frequency density**.

## Cumulative frequency

Add the frequencies as you go, and plot against the **upper class boundary**. Join with a smooth curve (an S-shape).

From a curve with $n$ values, read across at:

| Position | Read at |
|---|---|
| Median ($Q_2$) | $\tfrac{n}{2}$ |
| Lower quartile ($Q_1$) | $\tfrac{n}{4}$ |
| Upper quartile ($Q_3$) | $\tfrac{3n}{4}$ |
| $p$th percentile | $\tfrac{p}{100}n$ |

$$\text{interquartile range} = Q_3 - Q_1$$

The IQR measures the spread of the middle half of the data, so unlike the range it is unaffected by extreme values. A smaller IQR means more consistent data.

**Box plot.** Draw a box from $Q_1$ to $Q_3$ with a line at the median, and whiskers out to the minimum and maximum. Compare two box plots by their medians (typical value) and their IQRs (spread).

To read "how many scored more than 60", read **up** from 60 to the curve, across to the cumulative frequency, and subtract from $n$.

## Correlation and lines of best fit

A scatter diagram shows the relationship between two variables:

- **Positive correlation** — as one increases, so does the other (points slope up)
- **Negative correlation** — as one increases, the other decreases (points slope down)
- **Zero / no correlation** — no pattern

Describe the **strength** too: strong correlation means the points lie close to a line.

**Line of best fit**, drawn by eye: follow the trend of the points with roughly equal numbers either side, passing through the mean point. Use it to estimate a value, but note that estimating well outside the plotted range is unreliable.

Correlation does not prove that one variable **causes** the other.
