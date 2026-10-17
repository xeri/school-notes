# Which formula when

Physics questions rarely name the equation. They describe a situation, and the wording tells you which equation to use. This page maps the wording to the equation. The full list of equations is in [FORMULAS.md](../FORMULAS.md). Units and rearranging are in [Units, symbols and rearranging](../notes/units-and-rearranging.md).

## The 4-step routine

| Step | Do | Example: "A 1200 kg car accelerates from rest at 2.5 m/s² for 8.0 s. Find its final speed." |
|---|---|---|
| 1 | **List the givens** as symbol = value + SI unit. Translate the words ("from rest" → $u = 0$). Convert units now. | $m = 1200$ kg, $u = 0$, $a = 2.5$ m/s², $t = 8.0$ s |
| 2 | **Name the unknown** with its symbol. | $v = ?$ |
| 3 | **Pick the equation** that contains the unknown and only quantities you have. If none fits, find a missing quantity first (see Two-step chains). | $v$, $u$, $a$, $t$ → $v = u + at$. ($m$ is not needed. Spare data is common.) |
| 4 | **Write the equation, substitute, solve.** Answer with unit and sensible s.f. | $v = u + at = 0 + 2.5 \times 8.0 = 20$ m/s |

## Trigger table

### Motion ([notes](../notes/motion.md))

| Question says or gives | It means | Use |
|---|---|---|
| "from rest", "starts", "released" | $u = 0$ | SUVAT |
| "comes to rest", "stops", "brought to a halt" | $v = 0$ | SUVAT. Slowing down gives a negative $a$. |
| "dropped", "falls freely", "free fall" | $u = 0$ and $a = g = 9.81$ m/s² (the course value; IGCSE uses 9.8; use the value given) | SUVAT, or $mg\Delta h = \tfrac12mv^2$ |
| "constant speed", "steady velocity", "terminal velocity" | $a = 0$ and resultant force $= 0$ (forces balanced; at terminal velocity drag = weight) | $v = s/t$; driving force = resistive force |
| "average speed", a journey with stops or stages | total distance ÷ total time (stops count in the time) | $\text{average speed} = \dfrac{\text{total distance}}{\text{total time}}$ |
| speed, distance, time, no acceleration | | $v = \dfrac{s}{t}$ (or $s = ut$) |
| "acceleration", change in speed over a time | | $a = \dfrac{v-u}{t}$ |
| "decelerates", "slows down", "brakes" | $a$ is negative if the direction of motion is positive | $a = \dfrac{v-u}{t}$ |
| "constant acceleration" with three of $s, u, v, a, t$ | choose the equation that leaves out the quantity you neither have nor want | no $s$: $v = u + at$. No $v$: $s = ut + \tfrac12at^2$. No $t$: $v^2 = u^2 + 2as$ (extension). No $a$: $s = \tfrac12(u+v)t$ (extension). |
| "area under the speed–time graph" | distance travelled | rectangles + triangles ($\tfrac12 \times$ base $\times$ height) |
| "gradient of the speed–time graph" | acceleration | $\dfrac{\Delta v}{\Delta t}$ |
| "gradient of the distance–time graph" | speed | $\dfrac{\Delta s}{\Delta t}$ (tangent if curved) |
| two forces or velocities "at right angles", "resultant" | Pythagoras and trigonometry | $R = \sqrt{a^2 + b^2}$, angle $= \tan^{-1}(a/b)$ |

SUVAT status: the 2024 scheme of work calls $v = u + at$ and $s = ut$ core, $s = ut + \tfrac12at^2$ higher level, and $v^2 = u^2 + 2as$ and $s = \tfrac12(u+v)t$ **extension**. The course topic page lists all four for use, so learn them all.

### Forces and momentum ([notes](../notes/forces.md))

| Question says or gives | It means | Use |
|---|---|---|
| "resultant force", "net force", "unbalanced force" with mass | $F$ is the resultant (driving force − resistive forces) | $F = ma$ |
| "weight", "gravitational force", "on the Moon / Mars" | mass is unchanged; weight changes with $g$ | $W = mg$ |
| "gravitational field strength" | force per kg | $g = \dfrac{W}{m}$ (N/kg) |
| "extension", "spring", "stretched", "spring constant" | extension = new length − original length | $F = kx$ |
| "limit of proportionality" | end of the straight part of the graph; beyond it $F = kx$ no longer applies | $F = kx$ only below it |
| "turning effect", "pivot", "balanced", "beam", "see-saw" | principle of moments about the pivot | moment $= Fd$; $\sum$ clockwise $= \sum$ anticlockwise |
| "uniform beam", "uniform plank" | its own weight acts at its centre | include it as a moment |
| "in equilibrium" | no resultant force **and** no resultant moment | forces up = forces down; moments balance |
| "moves in a circle", "centripetal force" | force towards the centre | $F = \dfrac{mv^2}{r}$ (on the course topic page; the 2024 scheme says not required) |
| "momentum" | | $p = mv$ |
| "collision", "explosion", "recoil", "stick together", "move off together" | conservation of momentum (no external force) | total $mv$ before = total $mv$ after. Stuck together: $(m_1 + m_2)v$. From rest: total = 0. |
| "impulse", "impact time", "force during the collision", "in contact for 0.05 s", "crumple zone", "air bag" | | $Ft = mv - mu$, so $F = \dfrac{\Delta p}{t}$ |
| "rebounds", "bounces back" | velocity changes sign | $\Delta p = m(-v) - mu$ |
| "rate of change of momentum", "thrust", "gas ejected per second" | | $F = \dfrac{\Delta p}{\Delta t}$ |

### Energy, work, power, density, pressure ([notes](../notes/energy-pressure.md))

| Question says or gives | It means | Use |
|---|---|---|
| "lifted", "raised", "climbs", "gains height" | gain in gravitational PE | $\Delta E_p = mg\Delta h$ |
| "moving", "speed" + energy | kinetic energy | $E_k = \tfrac12mv^2$ |
| "falls and converts", "speed at the bottom", "pendulum at its lowest point", "ignore air resistance" | energy is conserved | $mg\Delta h = \tfrac12mv^2$, so $v = \sqrt{2g\Delta h}$ (write both lines) |
| "work done", "force moves through a distance", "pushed along" | distance in the direction of the force | $W = Fd$ |
| "lifted at a steady speed" | force = weight | $W = Fd = mg\Delta h$ |
| "stopped by friction / brakes over a distance" | work done by friction = KE lost | $Fd = \tfrac12mv^2$ |
| "power", "rate", "per second", "how quickly" | energy or work per second | $P = \dfrac{W}{t} = \dfrac{\Delta E}{t}$ |
| "efficiency", "useful", "wasted" | | $\dfrac{\text{useful output}}{\text{total input}} \times 100\%$; wasted = total − useful |
| "density" | | $\rho = \dfrac{m}{V}$ |
| "irregular object", "displacement can", "eureka can", "water level rises" | volume = rise in level, or the overflow volume | then $\rho = \dfrac{m}{V}$ |
| "floats or sinks" | floats if less dense than the liquid (water 1.0 g/cm³) | compare $\rho$ |
| "pressure", "force on an area", "area of contact" | | $p = \dfrac{F}{A}$ ($A$ in m²) |
| "depth", "below the surface", "in a liquid", "manometer height difference", "dam" | | $\Delta p = \rho g \Delta h$ |
| "total pressure" at a depth | liquid pressure + atmospheric pressure | $p_{atm} + \rho g h$ |

### Thermal physics ([notes](../notes/thermal.md))

| Question says or gives | It means | Use |
|---|---|---|
| "sealed", "fixed mass of gas", "constant temperature", "slowly compressed" | Boyle's law | $pV = \text{constant}$, $p_1V_1 = p_2V_2$ |
| "sealed container is heated", "rigid container", "constant volume" | pressure law | $\dfrac{p}{T} = \text{constant}$, $T$ in K |
| "constant pressure", "free piston", "balloon heated" | Charles's law | $\dfrac{V}{T} = \text{constant}$, $T$ in K |
| $p$, $V$ and $T$ all change | combined gas law | $\dfrac{p_1V_1}{T_1} = \dfrac{p_2V_2}{T_2}$, $T$ in K |
| any temperature in a gas law | convert first | $T/\text{K} = \theta/^\circ\text{C} + 273$ |
| "temperature rises / falls", "heated from 20 °C to 80 °C", "specific heat capacity" | | $Q = mc\Delta T$ ($\Delta T$ is the same in K and °C) |
| "thermal capacity" of a whole object | | $C = mc$ (J/K) |
| "melts", "boils", "freezes", "condenses", "at its boiling point", "no temperature change", "specific latent heat" | change of state | $Q = ml$ (the 2024 scheme writes $Q = mL$) |
| "heater", "immersion heater of $V$ and $I$ for $t$" | electrical energy input | $Q = VIt$ (or $E = Pt$) |
| "mixed", "dropped into water", "final temperature" | heat lost by hot = heat gained by cold | $m_1c_1\Delta T_1 = m_2c_2\Delta T_2$ |
| "ice at −10 °C heated to water at 20 °C" | split into stages | $mc\Delta T$ (ice) + $ml$ (melting) + $mc\Delta T$ (water) |

### Waves ([notes](../notes/waves.md))

| Question says or gives | It means | Use |
|---|---|---|
| "wave speed", "frequency", "wavelength" | | $v = f\lambda$ |
| "period", "time for one oscillation" | | $f = \dfrac{1}{T}$ |
| "distance between neighbouring crests / compressions" | wavelength $\lambda$ | |
| "waves per second", "oscillations per second" | frequency (Hz) | |
| "light", "radio", "microwaves", "X-rays", any EM wave in a vacuum or air | $v = c = 3.0\times10^8$ m/s | $c = f\lambda$ |
| "sound in air" | about 330–340 m/s (use the value given) | $v = f\lambda$ |
| "echo", "sonar", "ultrasound pulse returns", "there and back" | the sound travels $2d$ | $v = \dfrac{2d}{t}$, $d = \dfrac{vt}{2}$ |
| "angle of incidence", "angle of refraction", "refractive index" | angle in air goes on top | $n = \dfrac{\sin i}{\sin r}$ |
| "speed of light in glass / water" | | $n = \dfrac{c}{v}$ |
| "critical angle", "total internal reflection", "optical fibre" | inside the denser medium; TIR when $i > c$ | $n = \dfrac{1}{\sin c}$ |
| "angle of reflection" | measured from the normal | $i = r$ |

### Electricity ([notes](../notes/electricity.md))

| Question says or gives | It means | Use |
|---|---|---|
| "charge", "coulombs", current for a time | | $Q = It$ |
| "energy transferred per coulomb", "work done per unit charge" | p.d. (or e.m.f. in the source) | $V = \dfrac{W}{Q}$, $E = \dfrac{W}{Q}$ |
| energy, with charge and p.d. | | $W = QV$ |
| "resistance", "p.d. across", "current through" | | $V = IR$ |
| "in series" | same current; p.d.s add to the supply | $R_T = R_1 + R_2 + \dots$ |
| "in parallel" | same p.d. on each branch; branch currents add | $\dfrac{1}{R_T} = \dfrac{1}{R_1} + \dfrac{1}{R_2}$; for two, $R_T = \dfrac{R_1R_2}{R_1 + R_2}$ |
| "junction", "branch" | current in = current out | $\sum I_{in} = \sum I_{out}$ |
| "cells in series" | e.m.f.s add (a reversed cell subtracts) | |
| "length of wire", "thicker / thinner wire", "cross-sectional area", "resistivity" | | $R = \dfrac{\rho L}{A}$ |
| "power" with current and p.d. | | $P = IV$ |
| "energy" with current, p.d. and time | | $E = IVt$ |
| "power lost in the cables", "transmission", "heating in the wire" | $R$ is the cable's resistance | $P = I^2R$ |
| "cost", "kWh", "units of electricity", "hours" | | $E\,(\text{kWh}) = P\,(\text{kW}) \times t\,(\text{h})$; cost = kWh × price |
| "transformer", "turns", "step-up", "step-down" | | $\dfrac{V_p}{V_s} = \dfrac{N_p}{N_s}$ |
| "100% efficient transformer", "current in the primary" | power in = power out | $V_pI_p = V_sI_s$ |
| "potential divider", "two resistors in series across a supply", "output voltage", thermistor or LDR circuit | p.d. shared in the ratio of the resistances | $\dfrac{V_1}{V_2} = \dfrac{R_1}{R_2}$, $V_{out} = V_{in}\dfrac{R_2}{R_1 + R_2}$ |
| "fuse rating", "which fuse" | normal working current, then the next fuse above it | $I = \dfrac{P}{V}$, then pick the next size up (e.g. 3 A, 5 A, 13 A) |
| power from $V$ and $R$ only | $P = V^2/R$ is **not** on the course list | $I = V/R$, then $P = IV$ (two lines) |

### Atomic physics and space ([notes](../notes/atomic-space.md))

| Question says or gives | It means | Use |
|---|---|---|
| "nucleon number", "proton number", "how many neutrons" | | neutrons $= A - Z$ |
| "alpha decay" | | $A - 4$, $Z - 2$ |
| "beta decay" | | $A$ same, $Z + 1$ |
| "gamma emission" | | no change in $A$ or $Z$ |
| "half-life", "count rate", "activity halves" | count the halvings | each halving = one half-life |
| "background count", "background radiation" | subtract it from **every** reading first, then halve | corrected = measured − background |
| "fraction remaining", "after $n$ half-lives" | | $\left(\tfrac12\right)^n$ |
| "orbit", "orbital speed", "orbital period", "orbital radius" | $T$ in seconds | $v = \dfrac{2\pi r}{T}$ |
| "galaxy receding", "redshift", "recession speed", "Hubble constant" | | $H_0 = \dfrac{v}{d}$ |
| "age of the Universe" | | $\dfrac{d}{v} = \dfrac{1}{H_0}$ |
| "light takes … to reach Earth", "light-year" | | $t = \dfrac{d}{c}$; 1 light-year ≈ $9.5\times10^{15}$ m |

### Measurement and practical ([notes](../notes/measurement.md), [practical](../notes/practical.md))

| Question says or gives | It means | Use |
|---|---|---|
| "repeated readings", "mean" | | average = sum ÷ $n$ |
| "time for 20 oscillations" | divide to get one period | $T = \text{total}/20$ |
| "thickness of one sheet" from a stack | divide by the number of sheets | |
| "gradient of the graph" | large triangle on the best-fit line | $\dfrac{\Delta y}{\Delta x}$, with units |
| "compare two results", "do they agree?" | the June 2026 0625/62 mark scheme accepted values within about 10% of each other as agreeing | quote both values and the % difference |

## Two-step chains

When no single equation links the givens to the unknown, find the missing quantity first.

| Given | Wanted | Step 1 | Step 2 |
|---|---|---|---|
| $P$ (or $I$ and $V$), time | energy | $P = IV$ | $E = Pt$ |
| $I$, $t$, $V$ | energy | $Q = It$ | $W = QV$ |
| height of fall | speed at the bottom | $\Delta E_p = mg\Delta h$ | $\tfrac12mv^2 = \Delta E_p$, solve for $v$ |
| force, mass, time | final speed | $a = F/m$ | $v = u + at$ |
| speeds, time, mass | braking force | $a = (v - u)/t$ | $F = ma$ |
| mass, base dimensions | pressure on the ground | $W = mg$ and $A = l \times w$ (cm² → m²) | $p = F/A$ |
| turns, $V_p$, load resistance | secondary current | $V_s = V_p N_s / N_p$ | $I_s = V_s/R$ |
| turns, $V_p$, secondary current | primary current | $V_s = V_p N_s / N_p$ | $V_pI_p = V_sI_s$ |
| power sent, voltage, cable $R$ | power lost | $I = P/V$ | $P_{loss} = I^2R$ |
| power rating, mains voltage | fuse | $I = P/V$ | next fuse above $I$ |
| density, volume | weight | $m = \rho V$ | $W = mg$ |
| volume of water, temperature rise | energy | $m = \rho V$ | $Q = mc\Delta T$ |
| heater $V$, $I$, $t$, mass, $\Delta T$ | specific heat capacity | $E = VIt$ | $c = E/(m\Delta T)$ |
| mass lifted, height, time | power | $E = mg\Delta h$ | $P = E/t$ |
| two bodies collide and stick | KE lost | momentum conservation gives $v$ | $\tfrac12mv^2$ before − after |
| mass, speeds, contact time | average force | $\Delta p = mv - mu$ | $F = \Delta p/t$ |
| resistors in series, supply p.d. | p.d. across one | $R_T$, then $I = V/R_T$ | $V_1 = IR_1$ |
| gas temperatures in °C | new $p$, $V$ or $T$ | $T = \theta + 273$ | gas law |
| measured counts + background | half-life | subtract background | count the halvings |
| useful output, efficiency | input needed | efficiency as a decimal (25% → 0.25) | input = useful ÷ efficiency |

## Graph meanings

| Graph ($y$ against $x$) | Gradient | Area under | Watch for |
|---|---|---|---|
| distance–time | speed | no meaning | flat = at rest; straight = constant speed; curve = changing speed (use a tangent) |
| speed–time (velocity–time) | acceleration | distance travelled | flat = constant speed; downward slope = deceleration |
| force–extension ($F$ on $y$) | spring constant $k$ | not needed | straight through the origin up to the limit of proportionality |
| extension–load (extension on $y$) | $1/k$ | not needed | the course plots it this way round: check the axes |
| $V$ against $I$ | resistance $R$ (straight line) | | |
| $I$ against $V$ | $1/R$ | | for a curve use $R = V/I$ at that point, not the gradient |
| count rate–time (decay curve) | not used | | half-life = time for the count rate to halve; never reaches zero; levels off at background if not corrected |
| mass–volume | density | | |
| temperature–time (heating or cooling) | | | flat parts = change of state ($Q = ml$); sloping parts = $Q = mc\Delta T$ |
| $p$–$V$ (constant $T$) | | | a curve; $p$ against $1/V$ is a straight line through the origin |
| $p$–$T$ or $V$–$T$ | | | straight through the origin in kelvin; meets the temperature axis at −273 °C |
| $\sin i$–$\sin r$ | refractive index $n$ | | |
| momentum–time | resultant force | | |
| energy–time | power | | |

## Pairs not to confuse

| This | Not this | How to tell |
|---|---|---|
| Mass: kg, scalar, same everywhere | Weight: N, vector, $W = mg$, changes with $g$ | "on the Moon" changes weight only |
| Speed: scalar | Velocity: speed in a direction | "rebounds", "opposite direction" → velocity, use signs |
| Distance: total path length | Displacement: straight line start to end, with direction | 3 m east then 4 m north: distance 7 m, displacement 5 m |
| Thermal (heat) capacity $C = mc$: J/K, whole object | Specific heat capacity $c$: J/(kg K), per kg | "specific" means per kg |
| Specific heat capacity: temperature changes | Specific latent heat: change of state, temperature constant | Is the temperature changing? |
| Current $I$: A, rate of flow | Charge $Q$: C, amount | $Q = It$ |
| Power: W, rate | Energy: J, amount | $E = Pt$ |
| Pressure: Pa, force per area | Force: N | $p = F/A$ |
| Frequency: Hz, waves per second | Period: s, time for one wave | $f = 1/T$ |
| Series: same current, resistances add | Parallel: same p.d., currents add, $R_T$ below the smallest | |
| Amplitude: rest to crest; loudness | Wavelength: crest to crest, m | amplitude is **not** crest to trough |
| e.m.f.: energy per coulomb given **in the source** | p.d.: energy per coulomb transferred **in a component** | |
| Moment: N m, $d$ perpendicular to the force | Work: J, $d$ along the force | both are force × distance |
| Momentum $mv$: kg m/s, always conserved in collisions | Kinetic energy $\tfrac12mv^2$: J, can be lost in collisions | |
| Resultant force: the net force | One force, or the sum ignoring directions | $F = ma$ needs the resultant |
