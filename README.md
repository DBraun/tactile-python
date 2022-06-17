# Tactile-Python

Tactile-Python is a pure Python port of [tactile-js](https://github.com/isohedral/tactile-js), a library for representing, manipulating, and drawing isohedral tilings on the 2D plane. [Craig S. Kaplan](https://github.com/isohedral) created `tactile-js` based on his [PhD thesis](https://cs.uwaterloo.ca/~csk/other/phd/).

See [`tactile`'s original README file](https://github.com/isohedral/tactile/blob/master/README.md) for more information on how to use this library.

## Install

`pip install tactile`

## Demo

See `examples/random_tiles_p5.py` which requires [`p5`](https://p5.readthedocs.io/en/latest/). It will display random tilings in a window.

![Animating random tiles](docs/random-tiles.gif?raw=true "Animating random tiles")

## License

BSD 3-Clause License, inherited from [tactile-js](https://github.com/isohedral/tactile-js).

## Related Libraries and Projects

* [turning-function](https://github.com/DBraun/turning-function): A shape distance metric, hopefully the same as used in ["Escherization"](https://dl.acm.org/doi/10.1145/344779.345022) (Kaplan & Salesin, 2000)