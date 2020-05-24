{ pkgs ? import <nixpkgs> {} }:

let
  env = pkgs.buildFHSUserEnv {
    name = "netjs";
    targetPkgs = pkgs: with pkgs; [
      libmpc
      mpfr
      gmp
      zlib
      zstd
      gcc.cc
      gcc
      glibc
    ];
    extraOutputsToInstall = [ "dev" ];
    profile = ''
    '';
    runScript = pkgs.writeScript "env-shell" ''
      #!${pkgs.stdenv.shell}
      exec ${userShell}
    '';
  };

  userShell = builtins.getEnv "SHELL";

in pkgs.stdenv.mkDerivation {
  name = "netjs-fhs-dev";

  shellHook = ''
    exec ${env}/bin/netjs
  '';
  buildCommand = "exit 1";
}

