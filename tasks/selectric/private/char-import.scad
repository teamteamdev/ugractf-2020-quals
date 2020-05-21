$fa = 1.25;
$fs = 2;

pos = 0;
char = "u0448.stl";

rotate(360 - (1 + floor(pos / 5)) * 9, [0, 0, 1]) {
    rotate((5 - pos % 5) * 12 - 10, [1, 0, 0]) import(char);
}
