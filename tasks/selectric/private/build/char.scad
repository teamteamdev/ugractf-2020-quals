$fa = 1.25;
$fs = 2;

char = "F";

rotate(-10, [1, 0, 0]) rotate(-90, [1, 0, 0]) {
    rotate(180) translate([0, -5, 98]) linear_extrude(height=5) {
        mirror([1, 0, 0]) text(char,
                               font="JetBrains Mono", size=10, 
                               valign="baseline", halign="center", $fs=2.5);
    }
}
