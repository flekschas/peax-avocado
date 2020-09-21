# Peax-Avocado

This is a custom encoder model to use [Avocado](https://github.com/jmschrei/avocado) in [Peax](https://github.com/flekschas/peax)

## Get Started

1. Follow the instructions at https://github.com/flekschas/peax/blob/develop/README.md#installation to install Peax.

2. Outside of Peax, clone this repo.

  ```bash
  git clone https://github.com/flekschas/peax-avocado
  ```

3. Download an Avocado model. E.g.:

  ```bash
  cd peax-avocado
  python download-avocado.py chr1
  ```

  _Note: `download-avocado.py` requires that you activated the `px` environment from Peax!_

4. Symlink `peax-avocado` into Peax.

  ```bash
  cd ../peax
  ln -s ../peax-avocado avocado
  ```

5. Download the data that you want to explore and configure Peax. As an example do:

  ```bash
  cd avocado
  python download-example-data.py
  ```

  _Note: `download-example-data.py` requires that you activated the `px` environment from Peax!_

6. Start Peax.

  ```bash
  python start.py -b avocado -c avocado/configs/e116-dnase-h3k27ac.json
  ```

  _Note: the configuration file corresponds to the example data from step 5._