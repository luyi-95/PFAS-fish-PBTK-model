# Structural and restraint QC

These are separate preregistered quality gates; they do not alter the numerical matrices or issue a final route decision.

- Scan restraint centers: 1612 checks, 0 failures; maximum absolute drift 0.012906539 degrees against 0.020 degrees.
- Local proper-torsion domain: 280 variable/source checks, 0 failures; maximum minimax change 2.803452 degrees against 30.0 degrees. The selected map is fixed across each direction's six endpoints; 288 graph automorphisms were permitted generally and 96 with restrained CS O1 fixed.
- A/B pair geometry: 50592 values covering all 136 pairs at start, LBFGS final, and CG final for every state; maximum 0.69946831 nm against the 2.0 nm limit; [10.0, 10.0, 10.0] nm box checked.
- The T_CC_300 common energy-anchor row is included in both 118-row primary and 99-row low-tier vectors with its frozen CC weight; subtracting the same physical-energy record from itself gives exact zero value, derivative, and serialization bound.
