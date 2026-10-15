# Thermal physics

## States of matter

| | Solid | Liquid | Gas |
|---|---|---|---|
| Shape | fixed | takes container's | fills container |
| Volume | fixed | fixed | fills container |
| Compressible | almost not | almost not | easily |
| Arrangement | regular, touching | close, disordered | far apart, random |
| Separation | ~1 diameter | ~1 diameter | ~10 diameters |
| Motion | vibrate about fixed positions | move and slide past each other | fast, random, straight lines between collisions |
| Forces between | strong | moderate | negligible |

Draw a solid as a neat touching lattice, a liquid as touching but disordered, a gas as a few widely spaced particles with motion arrows.

## Kinetic model and temperature

Temperature measures the **average kinetic energy** of the molecules — faster molecules mean a higher temperature. **Internal energy** is the total of molecular kinetic *and* potential energy.

The **Kelvin** scale is the scientific temperature scale because it is proportional to molecular kinetic energy. **0 K** (absolute zero) is the lowest possible temperature: molecular motion stops.

$$T/\mathrm{K} = T/^\circ\mathrm{C} + 273$$

So 27 °C = 300 K. Note that a *change* of 20 °C equals a *change* of 20 K — the interval is identical, only the zero differs.

## Gas pressure

Gas molecules collide with the container walls. Each collision reverses the molecule's momentum, so the wall exerts a force on it and (by reaction) it exerts a force on the wall. Pressure is the total of these forces divided by the wall area.

Collisions lose no kinetic energy — molecules do not slow down and stop even after millions of collisions.

**Brownian motion** is evidence for the model: smoke particles viewed under a microscope jitter randomly, because they are being bombarded unevenly by invisible, fast-moving air molecules. A massive particle can be visibly moved by light, fast molecules.

## Gas laws

| Law | Held constant | Relationship |
|---|---|---|
| Boyle | temperature | $pV = \text{constant}$ |
| Gay-Lussac | volume | $P/T = \text{constant}$ |
| Charles | pressure | $V/T = \text{constant}$ |

Combined, for a fixed mass of gas:

$$\frac{P_1V_1}{T_1} = \frac{P_2V_2}{T_2}$$

**Temperatures must be in kelvin.** Always.

*Molecular explanations.* Reducing the volume at constant temperature packs the same molecules into less space, so they hit the walls more often per second and the pressure rises. Raising the temperature at constant volume makes the molecules faster, so they hit harder and more often, and the pressure rises.

**Worked example.** 250 cm³ of gas at 100 kPa and 27 °C is compressed to 150 cm³ at 57 °C.

$T_1 = 300$ K, $T_2 = 330$ K.

$$P_2 = \frac{P_1V_1T_2}{T_1V_2} = \frac{100\times250\times330}{300\times150} = 183\ \text{kPa}$$

## Evaporation

Molecules at a liquid's surface have a spread of speeds. The **fastest** ones escape. Losing the fastest molecules lowers the average kinetic energy of those left behind, so the liquid **cools**.

Evaporation is faster with:
- higher temperature (more molecules fast enough to escape)
- larger surface area (more molecules at the surface)
- a draught over the surface (escaped molecules are carried away before returning)

A body in contact with an evaporating liquid loses energy to it and cools — sweating, a damp cloth on a forehead, the chill of spilled alcohol.

**Evaporation vs boiling:** evaporation happens at the surface only, at any temperature; boiling happens throughout the liquid, at a fixed boiling point.

## Thermal expansion

Heating increases molecular vibration and average separation, so solids, liquids and gases all expand at constant pressure. The order of magnitude is:

$$\text{gases} \gg \text{liquids} > \text{solids}$$

because the weaker the forces between molecules, the more freely the separation can grow.

Applications and consequences: expansion gaps in bridges and railway lines, a bimetallic strip in a thermostat, the liquid column rising in a thermometer, a tight metal lid loosened by hot water, overhead power lines sagging in summer.

## Measuring temperature

Any physical property that varies with temperature can measure it: the length of a liquid column, electrical resistance, gas pressure, thermoelectric e.m.f., colour of a hot body.

**Fixed points** are needed to define a scale — conventionally the melting point of pure ice (0 °C) and the boiling point of pure water at atmospheric pressure (100 °C).

**Liquid-in-glass thermometer.** A bulb of mercury or alcohol connected to a narrow capillary in a glass stem with a scale. The liquid expands much more than the glass, so it rises up the capillary.

| Change | Effect |
|---|---|
| Larger bulb | more sensitive (greater movement per degree) |
| Narrower capillary | more sensitive |
| Narrower capillary | smaller range |
| Uniform capillary bore | more linear scale |

**Thermocouple.** Two different metal wires joined at two junctions; a temperature difference between the junctions generates an e.m.f. read by a voltmeter. It has a very small junction, so it responds to **rapidly varying** temperatures, and works at **high** temperatures where liquids boil away.

## Heat capacity and latent heat

Raising a body's temperature increases its internal energy: the molecules vibrate or move faster.

**Thermal capacity** of a whole object: $Q = mc$ per kelvin, in J/K.

**Specific heat capacity** $c$ is the energy needed to raise **1 kg** of a substance by **1 K**:

$$Q = mc\Delta T$$

*Experiment.* Mass a metal block, insert an electric immersion heater and a thermometer into drilled holes, lag the block, record the starting temperature. Run the heater at known $V$ and $I$ for time $t$, so $Q = VIt$. Record the final temperature and calculate $c = Q/(m\Delta T)$. Lagging reduces heat loss, the main source of error, which makes the measured $c$ too high.

**Worked example.** Heating 0.50 kg of water ($c = 4200$ J/kg·K) by 20 K needs $0.50\times4200\times20 = 42\,000$ J.

**Latent heat.** During melting or boiling, energy input changes the molecular *arrangement* rather than the temperature, so the temperature stays constant. Breaking molecular bonds requires energy; forming them releases it.

- **Latent heat of fusion** — solid ↔ liquid
- **Latent heat of vaporisation** — liquid ↔ gas

**Specific latent heat** $l$ is the energy per kilogram to change state:

$$Q = ml$$

*Experiment (ice).* Put crushed melting ice in a funnel with an immersion heater; collect and mass the water that drips in a known time, with a second unheated funnel as a control for room-temperature melting. Subtract the control mass. Then $l = VIt/m$.

*Experiment (steam).* Boil water with a heater of known power, mass the water lost in a measured time once boiling is steady, and use $l = VIt/m$.

A cooling curve for a pure substance shows flat plateaus at the melting and boiling points — temperature constant while energy leaves.

## Thermal transfer

**Conduction** — energy passes through matter without bulk movement. Molecules at the hot end vibrate more and jostle their neighbours. In metals there are also **free (delocalised) electrons** that travel through the lattice carrying kinetic energy, which is why metals conduct far better than non-metals. Gases are the worst conductors (molecules are far apart).

*Experiment.* Rods of copper, aluminium, glass and wood of the same dimensions, each with a drawing pin stuck on the far end with wax, heated at one end in a water bath. The pins fall in order of conductivity — copper first, wood last.

**Convection** — bulk movement in a fluid. Heating a fluid makes its particles move faster, so its volume increases and its **density decreases**. The less dense hot fluid rises through the denser cold fluid, which sinks to replace it, forming a **convection current**.

*Experiment.* Drop a crystal of potassium permanganate into a beaker of water and heat one spot at the bottom: the coloured streak traces the circulating current.

**Radiation** — energy carried by infrared electromagnetic waves. It needs **no medium**, so it crosses a vacuum (this is how the Sun's energy reaches us).

| Surface | Emitter | Absorber | Reflector |
|---|---|---|---|
| Dull black | good | good | poor |
| Shiny silver | poor | poor | good |

Emission also rises with surface **temperature** and surface **area**.

*Experiment (Leslie's cube).* A metal cube with faces of different finishes, filled with hot water. A thermopile or infrared detector at equal distances from each face reads the greatest emission from the dull black face and the least from the shiny face.

**Everyday consequences.** A vacuum flask blocks all three: a vacuum stops conduction and convection, silvered walls reduce radiation, a stopper stops evaporation. A cooker uses conduction through the pan base, convection in the water, and radiation from the grill. Loft insulation traps air to stop convection; a shiny foil behind a radiator reflects radiation back into the room.
