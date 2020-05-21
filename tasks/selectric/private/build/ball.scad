$fa = 1.25;
$fs = 2;

faces = 40;

difference() {
    union() {
        sphere(100);
        rotate((360/faces) * 9.5 - 0.25) intersection() {
            sphere(101);
            translate([0, 0, -100]) difference() {
                cube(200);
                rotate(0.5) translate([0, 0, -50]) cube(300);
            }
            translate([0, 0, -35]) cube(200);
        };
    }
    sphere(80);
    translate([-100, -100, 78]) cube(200);
    translate([-100, -100, -250]) cube(200);
    for (j = [0:faces-1]) {
        rotate((360/faces) * (j + 0.5)) {
            translate([60, 0, -50]) rotate(45, [1, 0, 0]) translate([-10, -10, -10]) scale([3, 1, 1]) cube(20);
        }
    }
}
