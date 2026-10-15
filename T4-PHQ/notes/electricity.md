# Electricity and magnetism

## Magnetism

Like poles repel, unlike poles attract. A magnet attracts magnetic materials (iron, steel, cobalt, nickel) whether or not they are already magnetised; it repels only another magnet.

Magnetic materials contain **magnetic domains** — small crystal regions each acting as a tiny magnet. In an unmagnetised sample the domains point in random directions and cancel. Magnetising aligns them. Non-magnetic materials have no domains.

**Field lines** run from N to S outside the magnet, are closest together where the field is strongest (at the poles), and **never cross** — magnetic forces arise from the interaction of field lines that cannot intersect.

*Plotting the field.* Sprinkle iron filings on paper over a bar magnet and tap gently: the filings line up along the field. Filings show the **pattern** but not the **direction** — for that, move a small plotting compass around the magnet and mark the needle's direction at each point.

Two N poles facing each other give a **neutral point** between them where the fields cancel.

| Magnetising | Demagnetising |
|---|---|
| Stroking repeatedly with one pole of a magnet | Hammering |
| Placing in a coil carrying **d.c.** | Heating strongly |
| Hammering while inside a magnetic field | Placing in a coil carrying **a.c.** |

**Soft** magnetic material (soft iron) loses its magnetism as soon as the external field is removed — ideal for electromagnet and transformer cores. **Hard** magnetic material (steel) keeps it — ideal for permanent magnets.

A **permanent magnet** is always on. An **electromagnet** can be switched off, and its strength varied by changing the current or the number of turns — which is what makes cranes, relays and loudspeakers possible.

## Charge and electric fields

Atoms contain positive protons and negative electrons with charges of equal magnitude. Charge is measured in **coulombs (C)**. Unlike charges attract, like charges repel.

**Charging by friction.** Rub a polythene rod with a cloth: electrons transfer from one material to the other. The rod gaining electrons becomes negative; the cloth losing them becomes positive. Only **electrons** move — protons stay in the nucleus.

**Detecting charge.** A gold-leaf electroscope has a metal cap on a stem with a thin gold leaf. Bringing a charged rod near the cap makes the leaf rise, because the leaf and stem acquire like charges and repel.

**Charging by induction.** Bring a charged rod near (not touching) an insulated metal sphere: electrons in the sphere shift, leaving the near face oppositely charged and the far face like-charged. Earth the far side briefly while the rod is still there, then remove the earth and then the rod. The sphere keeps a charge **opposite** to the rod's, without ever touching it.

**Conductors vs insulators.** Metals have **free (delocalised) electrons** that drift through the lattice, so charge flows. In insulators every electron is bound to its atom, so charge stays where it is put.

An **electric field** is a region in which a charge experiences a force. The field direction at a point is the direction of the force on a **positive** charge there.

| Arrangement | Field pattern |
|---|---|
| Point positive charge | straight lines radiating outwards |
| Point negative charge | straight lines pointing inwards |
| Charged conducting sphere | radial outside, as if from the centre; zero inside |
| Two parallel plates | uniform, evenly spaced parallel lines from + to − |

## Current, e.m.f., p.d. and resistance

**Current** is the rate of flow of charge:

$$I = \frac{Q}{t}$$

In a metal, current is a flow of **electrons**, from negative to positive. **Conventional current** is drawn from positive to negative — the opposite direction. Measure current with an **ammeter in series**.

**E.m.f.** (electromotive force, volts) is defined by the energy change *inside the supply* — chemical to electrical in a cell — that drives charge round a complete circuit.

**Potential difference** (volts) is the energy transferred *per unit charge* in a component. 1 V = 1 J/C. Measure p.d. with a **voltmeter in parallel** across the component.

**Resistance:**

$$R = \frac{V}{I}$$

Current is *not* used up passing through a resistor — charge is conserved. For a fixed p.d., more resistance means less current.

*Experiment.* Connect the unknown resistor in series with a cell, an ammeter and a variable resistor, with a voltmeter across it. Record several $V$ and $I$ pairs, plot $V$ against $I$: the gradient is $R$.

### Resistance of a wire

Resistance is **proportional to length** and **inversely proportional to cross-sectional area**:

$$R = \frac{\rho L}{A}$$

where $\rho$ is the resistivity, a constant for the material. Double the length, double the resistance; double the diameter (so quadruple the area), quarter the resistance.

### I–V characteristics

- **Ohmic resistor (metal at constant temperature)** — a straight line through the origin. Resistance is constant.
- **Filament lamp** — an S-shaped curve that flattens. As the current rises the filament heats up, the lattice ions vibrate more, electrons collide more often, and the resistance **increases**.

## Series and parallel circuits

| | Series | Parallel |
|---|---|---|
| Current | the same at every point | source current = sum of branch currents |
| P.d. | p.d.s across components add to the supply p.d. | the same across each branch |
| Resistance | $R_T = R_1 + R_2$ | $R_T = \dfrac{R_1R_2}{R_1+R_2}$ |
| One lamp fails | all go out | the others stay on |

The combined parallel resistance is always **less** than either individual resistor, because there are more paths for charge to take. Cells in series add their e.m.f.s.

Household lamps are wired in **parallel** so each can be switched independently, each gets the full mains p.d., and one failing does not black out the house.

![Series circuit with a lamp, a resistor, an ammeter in series and a voltmeter across the resistor](circuit.svg)

**Worked example.** A 6.0 V supply across a 3.0 Ω resistor:

- $I = V/R = 6.0/3.0 = 2.0$ A
- $P = VI = 6.0 \times 2.0 = 12$ W
- In 10 s, $E = Pt = 120$ J
- Check independently: $Q = It = 20$ C and $E = VQ = 6.0\times20 = 120$ J ✓

**Worked example (combination).** A 4.0 Ω and a 12 Ω resistor in parallel, the pair in series with a 3.0 Ω resistor, across 12 V.

- Parallel pair: $\dfrac{4\times12}{4+12} = 3.0$ Ω
- Total: $3.0 + 3.0 = 6.0$ Ω
- Supply current: $12/6.0 = 2.0$ A
- P.d. across the parallel pair: $2.0 \times 3.0 = 6.0$ V, so the 4.0 Ω branch carries 1.5 A and the 12 Ω branch 0.5 A (summing to 2.0 A ✓)

## Electrical power and energy

$$P = IV \qquad E = IVt$$

A circuit transfers energy from the supply to the components, and the components transfer it onwards to the surroundings — as light, sound, motion or heating.

## Circuit components

Learn to draw and read: cell, battery, switch, fixed resistor, variable resistor, heater, thermistor, LDR, lamp, ammeter, voltmeter, galvanometer, magnetising coil, transformer, bell, fuse, relay, diode.

**Potential divider (potentiometer).** Two resistors in series across a supply tap off a fraction of the p.d. between them. A variable version lets you set any output p.d. from zero to the full supply — used as a volume control or a dimmer.

$$V_{out} = V_{in}\times\frac{R_2}{R_1+R_2}$$

**Thermistor** — resistance **falls** sharply as temperature rises. **LDR** — resistance **falls** as light intensity rises. Both are **input transducers**: put one in a potential divider and the output p.d. changes with temperature or light.

**Relay** — a small current through a coil makes an electromagnet that closes contacts in a separate circuit. It lets a small, safe sensing current switch a large current, and electrically isolates the two circuits.

**Diode** — conducts in one direction only. As a **rectifier**, it converts a.c. to d.c. by blocking the reverse half of the cycle.

**Light-sensitive switch.** LDR in a potential divider → output p.d. rises as it gets dark → that p.d. operates a relay → the relay switches on a lamp. Swap in a thermistor and the same circuit becomes a **temperature-operated alarm**.

## Dangers of electricity

| Hazard | Why it is dangerous |
|---|---|
| Damaged insulation | exposed live conductor — risk of electric shock |
| Overheating cables | too much current for the cable; melts insulation, fire risk |
| Damp conditions | water conducts, completing a path through the body |

Three-pin plug wiring: **live = brown**, **neutral = blue**, **earth = green/yellow stripes**.

A **fuse** is a thin wire that melts and breaks the circuit if the current exceeds its rating. It protects the **appliance and the wiring**, not the person — it does not blow fast enough to prevent a shock. A **circuit breaker** does the same job electromagnetically and can be reset.

Choose the fuse just above the appliance's normal current. A 230 V, 700 W appliance draws $I = P/V = 700/230 = 3.0$ A, so a 5 A fuse suits it; a 13 A fuse would let a dangerous fault current flow.

**Earthing** connects a metal case to earth by a low-resistance path. If a fault makes the case live, a very large current flows straight to earth, blowing the fuse at once and disconnecting the supply — so the case can never stay live.

## Electromagnetic induction

Moving a conductor across a magnetic field, or changing the field linking a conductor, **induces an e.m.f.** in it. If the circuit is complete, an induced current flows.

*Experiment.* Connect a coil to a sensitive galvanometer and push a bar magnet in: the needle deflects. Hold the magnet still: no deflection. Pull it out: the needle deflects the other way. It is the **relative motion** — the change — that matters.

Induced e.m.f. increases with:
- a faster rate of change of the magnetic field
- more turns of wire on the coil
- a stronger magnet

**Lenz's law** — the induced e.m.f. opposes the change that caused it. Use **Fleming's right-hand rule** for the generator effect: thumb = motion, first finger = field, second finger = induced current.

## a.c. generator

**d.c.** flows in one direction only; **a.c.** reverses direction periodically.

A rotating-coil generator has a coil spinning between the poles of a magnet. Each end of the coil connects to a **slip ring**, pressed by a carbon brush, so the output keeps the coil's own reversals and the external current is **alternating**.

The voltage–time output is a sine curve:
- **Peak** output when the coil is **parallel to the field** (horizontal in the field), where it cuts field lines fastest.
- **Zero** output when the coil is **perpendicular to the field**, where it is momentarily cutting no lines.

## Transformers

A **soft-iron core** carries two coils. A.c. in the primary makes a continuously changing magnetic field in the core, which links the secondary and induces an a.c. e.m.f. in it. It only works with a.c., because a steady field induces nothing.

$$\frac{V_p}{V_s} = \frac{N_p}{N_s}$$

**Step-up** has more secondary turns ($V_s > V_p$); **step-down** has fewer.

For a 100% efficient transformer, power in = power out:

$$I_pV_p = I_sV_s$$

**Worked example.** A transformer steps 230 V to 11.5 V with 2000 primary turns. Secondary turns: $N_s = N_p V_s/V_p = 2000 \times 11.5/230 = 100$. If the secondary draws 2.0 A, the primary current is $I_p = I_sV_s/V_p = 2.0\times11.5/230 = 0.10$ A.

**High-voltage transmission.** Power is transmitted at very high voltage because, for a given power $P = IV$, raising $V$ lowers $I$. Cable losses are

$$P_{loss} = I^2R$$

so halving the current cuts the loss to a quarter. Advantages: much less energy wasted as heat in the cables, and thinner, cheaper cables can be used. Step-up transformers raise the voltage at the power station; step-down transformers lower it again for consumers.

## Magnetic effect of a current

A current produces a magnetic field around it.

- **Straight wire** — concentric circles around the wire, weakening with distance. Direction: right-hand grip rule — thumb along the conventional current, fingers curl the field direction.
- **Solenoid (coil)** — a field like a bar magnet's, uniform and strong inside, spreading outside. One end acts as N, the other as S; reverse the current and the poles swap.

The field strength increases with more current, more turns, or an iron core. The direction of a field line at a point is the direction of the force on a **north** pole placed there.

## Force on a current-carrying conductor

A current-carrying wire in a magnetic field experiences a force — the **motor effect**.

*Experiment.* Rest a stiff copper wire loosely across the poles of a horseshoe magnet and pass a current: the wire jumps. Reverse the **current** and it jumps the other way. Reverse the **field** (turn the magnet) and it also reverses. Reverse both and it jumps as before.

Use **Fleming's left-hand rule** for the motor effect: first finger = field (N to S), second finger = conventional current, thumb = force (motion). The force is greatest when the wire is perpendicular to the field and zero when parallel.

A beam of charged particles is deflected the same way — a cathode-ray beam bends in a magnetic field, with electrons (negative) deflecting opposite to the conventional-current direction.

## d.c. motor

A current-carrying coil in a magnetic field experiences a **turning effect**, because the forces on the two sides of the coil act in opposite directions. The turning effect increases with:

- more turns on the coil
- a larger current
- a stronger magnetic field

A **split-ring commutator** reverses the current direction in the coil every half turn, just as the coil passes the vertical. Without it, the coil would stop at the vertical position and rock; with it, the turning effect always acts the same way round and the coil rotates continuously.
