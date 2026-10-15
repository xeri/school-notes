# Measurement, units and vectors

## Quantities and units

Every physical measurement is a number **and** a unit. The number alone is meaningless.

The seven SI base quantities and their units:

| Quantity | Unit | Symbol |
|---|---|---|
| Length | metre | m |
| Mass | kilogram | kg |
| Time | second | s |
| Electric current | ampere | A |
| Thermodynamic temperature | kelvin | K |
| Amount of substance | mole | mol |
| Luminous intensity | candela | cd |

Everything else is derived from these: speed m/s, acceleration m/s², force N (= kg·m/s²), pressure Pa (= N/m²), energy J (= N·m), power W (= J/s), potential difference V (= J/C), charge C (= A·s), momentum kg·m/s.

## Standard form and unit conversion

Convert **before** substituting into an equation.

- 72 km/h = 72 × 1000 / 3600 = **20 m/s**
- 1 cm³ = $10^{-6}$ m³ — all three dimensions shrink by 100, so the factor is $100^3$
- 2.7 g/cm³ = 2700 kg/m³
- 5 kJ = 5000 J

Standard form keeps very large and very small numbers manageable: the speed of light is $3.00\times10^8$ m/s, not 300000000 m/s.

## Instruments

Choose an instrument whose **range** covers the quantity and whose **resolution** is fine enough for the precision you need.

| Instrument | Typical precision | Use |
|---|---|---|
| Metre rule | ±1 mm | lengths above a few cm |
| Vernier calliper | ±0.1 mm | small diameters, thicknesses |
| Micrometer screw gauge | ±0.01 mm | wire diameter, thin sheets |
| Measuring cylinder | ±1 cm³ (typical) | liquid volume, displacement |
| Stopwatch (digital) | ±0.01 s display, ~±0.2 s reaction | time intervals |
| Protractor | ±1° | angles of incidence and refraction |

Read a scale with your eye directly in line with the mark to avoid **parallax**. A voltmeter goes **in parallel** across the component; an ammeter goes **in series** with it.

## Averaging and repeats

$$\text{average} = \frac{\text{sum of } n \text{ readings}}{n}$$

Timing a single pendulum swing of about 2 s with a ±0.2 s reaction error gives a 10% error. Time **ten** swings (about 20 s) and divide by ten: the same ±0.2 s is now 1%. The same trick works for any short, repeatable interval.

Repeats expose variation and reduce the effect of **random** error on the mean. They do **not** remove a **systematic** error such as a zero offset — check and correct the zero before you start.

## Graphs

A scatter graph of experimental data should have:

- the independent variable (what you changed) on the horizontal axis
- both axes labelled with quantity **and** unit
- a scale that fills at least half the grid in each direction
- a best-fit line or smooth curve — not dot-to-dot

Gradient, using a large triangle on the best-fit line:

$$\text{gradient} = \frac{\Delta y}{\Delta x}$$

The gradient carries units: a distance–time gradient is a speed in m/s; a speed–time gradient is an acceleration in m/s².

A **normal** is a construction line drawn at 90° to a surface. It is the reference line for every angle of incidence, reflection and refraction.

## Scalars and vectors

A **scalar** has magnitude only. A **vector** has magnitude and direction.

| Scalar | Vector |
|---|---|
| distance | displacement |
| speed | velocity |
| mass | weight |
| time, energy, temperature | force, acceleration, momentum |

Walk 3 m east then 4 m north: the **distance** travelled is 7 m, but the **displacement** is 5 m (by Pythagoras) at 53° east of north.

### Adding vectors by scale diagram

1. Choose and state a scale, e.g. 1 cm represents 10 N.
2. Draw the first vector to scale in the correct direction.
3. Draw the second starting from the **head** of the first (head-to-tail).
4. The **resultant** runs from the tail of the first to the head of the last.
5. Measure its length and convert with your scale; measure its angle with a protractor.

Forces along the same line just add or subtract: 12 N right and 5 N left give 7 N right.

Forces at right angles: 3.0 N east and 4.0 N north give a resultant of magnitude 5.0 N at $\tan^{-1}(3/4) = 37°$ east of north.
