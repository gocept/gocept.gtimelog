{ pkgs ? import <nixpkgs> {} }:


let
  python = import ./requirements.nix { inherit pkgs; };
in
{
  gtimelog = python.mkDerivation {
    name = "gocept.gtimelog-1.1.0";
    src = ./.;
    propagatedBuildInputs  = builtins.attrValues python.packages;
  };
}
