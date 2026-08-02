# `white_line.figures.plates` — plate builders

One module per plate family. Each module owns the SVG composition for its plates;
the `FigurePlate` registry in `__init__.py` binds each plate to its builder.

## Modules

- `__init__.py` — `FigurePlate` dataclass and `FIGURE_PLATES` registry
- `overview.py` — cover art, absence layers, registry taxonomy
- `contract.py` — state machine, review atlas, review protocol
- `distributions.py` — distribution panels, decay timeline, conflict lattice
- `evidence.py` — reason trail, invariant battery, facets lattice
- `inspection.py` — expiry queue, horizon dispersion, intake reachability
