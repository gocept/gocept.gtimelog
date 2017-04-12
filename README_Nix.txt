To use the Nix expressions to install the package, you need nix installed (currently available for macOS and Linux)

# install nix
$ curl https://nixos.org/nix/install | sh

# install gocept.gtimelog
$ nix-env -f ./default.nix -iA gtimelog