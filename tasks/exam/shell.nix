with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "exam";
  buildInputs = [ glibc.static (ncurses.override { enableStatic = true; }) ];
}
