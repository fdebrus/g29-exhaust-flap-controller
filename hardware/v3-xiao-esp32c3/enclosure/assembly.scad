// Assembly view: board v3 with its main components inside the enclosure.
// For visualisation only (component bodies are approximate boxes).
include <enclosure.scad>
part = "none";                 // suppress the enclosure's own output
show_lid = false;              // true: lid in place (translucent); false: lid off
exploded = 0;                  // mm to lift the lid

z0 = pcb_z;                    // PCB underside
module at(x, y, z = 0) translate([bx(x), by(y), z0 + pcb_t + z]) children();

module pcb() {
  translate([bx(0), by(0), z0]) color([0.12, 0.45, 0.2]) difference() {
    cube([pcb_x, pcb_y, pcb_t]);
    for (h = holes) translate([h[0], h[1], -1]) cylinder(d = 2.7, h = 5);
  }
}
module socket(x, y, n) at(x - 1.27, y - 1.27) color([0.15, 0.15, 0.15]) cube([2.54, 2.54 * n, 8.5]);
module xiao() {   // 21 x 17.5, sits on the two 1x7 sockets, USB at the top edge
  at(11.62 - 8.75, 11.62 - 10.5, 8.5 + 2.5) {
    color([0.1, 0.1, 0.1]) cube([17.5, 21, 1.2]);
    translate([17.5/2 - 4.5, -1.3, 1.2]) color([0.75, 0.75, 0.78]) cube([9, 7.5, 3.2]);     // USB-C
    translate([2, 6, 1.2]) color([0.75, 0.75, 0.78]) cube([13.5, 12, 2.4]);                  // shield can
  }
}
module receiver() {
  smd(25, 13.5, 5, 4, 1.6, [0.1, 0.1, 0.1]);                                                 // U3 SYN480R
  at(31.5 - 2.35, 18 - 5.75, 0) color([0.8, 0.8, 0.82]) cube([4.7, 11.5, 4.2]);              // Y1 HC-49S-SMD
  at(26, 2.5, 0) color([0.8, 0.2, 0.2]) { cylinder(d = 1, h = 8); translate([0, 0, 8]) rotate([-90, 0, 0]) cylinder(d = 1, h = 3); }   // antenna wire to the exit hole
}
module relay() at(36 - 1.3, 4 - 1.4, 0) color([0.95, 0.95, 0.92]) cube([10.2, 20.3, 11.5]);
module smd(x, y, l, w, h, c = [0.25, 0.25, 0.25], rot = 0) at(x, y) rotate([0, 0, rot]) translate([-l/2, -w/2, 0]) color(c) cube([l, w, h]);
module board_parts() {
  socket(4, 4, 7); socket(19.24, 4, 7);
  xiao(); receiver(); relay();
  at(53, 26) color([0.1, 0.1, 0.12]) cylinder(d = 6.3, h = 7.7);                             // C1
  smd(45, 36, 6.6, 6.1, 2.3, [0.2, 0.2, 0.2]);                                               // U2 body
  smd(50.3, 3.8, 4.5, 3.2, 1.2, [0.85, 0.85, 0.8], 90);                                      // F1
  smd(53, 10.3, 4.3, 2.6, 2.3, [0.15, 0.15, 0.15], 90); smd(53, 17.4, 4.3, 2.6, 2.3, [0.15, 0.15, 0.15], 90);
  smd(12, 28, 4.3, 2.6, 2.3, [0.15, 0.15, 0.15], 0);                                         // D1 D2 D6
  for (p = [[4, 24], [8.5, 24], [17.5, 24], [22, 24], [40, 26], [40, 30], [51.5, 31.9]]) smd(p[0], p[1], 2, 1.25, 0.6, [0.2, 0.2, 0.2], 0);
  smd(51.2, 37, 2, 1.25, 0.6, [0.2, 0.2, 0.2], 90);
  for (p = [[23.5, 5.5], [28.5, 5.5], [30, 9.5], [23.5, 17.8], [27.3, 20.2]]) smd(p[0], p[1], 1.6, 0.8, 0.8, [0.25, 0.25, 0.25], 0);
  smd(26, 8, 1.6, 0.8, 0.8, [0.25, 0.25, 0.25], 90);                                         // RF 0603s
  smd(13, 24, 2.9, 1.3, 1.1, [0.1, 0.1, 0.1]); smd(25.5, 27.5, 2.9, 1.3, 1.1, [0.1, 0.1, 0.1]);   // Q1 Q2
  smd(30.5, 26.5, 2.7, 1.6, 1.1, [0.15, 0.15, 0.15]);                                        // D5
  for (p = [[35.5, 26.5], [35.5, 30]]) smd(p[0], p[1], 3.2, 1.6, 0.6, [0.3, 0.3, 0.3]);     // R10 R11 (DNP)
  for (x = [4, 24]) at(x - 1.75, 35 - 3.6) color([0.2, 0.6, 0.35]) cube([7.5, 7.3, 8.3]);    // J1 J3
}

base();
pcb(); board_parts();
if (show_lid) translate([0, 0, base_h + exploded]) color([0.6, 0.65, 0.75, 0.35]) lid();
