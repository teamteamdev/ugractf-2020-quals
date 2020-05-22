{ config, pkgs, lib, ... }:

with lib;

in {
  networking.firewall = {
    allowedTCPPorts = [
      17493
    ];
  };
}
