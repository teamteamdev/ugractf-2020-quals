{ config, pkgs, lib, ... }:

with lib;

in {
  networking.firewall = {
    allowedTCPPorts = [
      17493 # melodrama1, melodrama2
      17494 # ege
    ];
  };
}
