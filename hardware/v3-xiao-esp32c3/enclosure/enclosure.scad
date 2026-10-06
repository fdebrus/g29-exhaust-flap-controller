// G29 exhaust flap controller - enclosure for board v3 (58 x 40 mm)
// Two-part box: base with three M2.5 screw bosses (board holes H1-H3) and a support ledge,
// lid with snap lip. The 433 MHz receiver is on the board (SYN480R), so one low variant only.
// Print: PETG or ASA (trunk gets warm), 0.2 mm layers, 3 perimeters, no supports.

// ---------- PCB ----------
pcb_x = 58;  pcb_y = 40;  pcb_t = 1.6;
clr   = 0.4;              // play around the PCB in the rails
// ---------- walls ----------
wall  = 2.0;  floor_t = 2.0;  lid_t = 2.0;
rail_h = 4.0;             // PCB underside above the floor (room for solder joints and the relay pins)
rail_d = 1.5;             // support ledge depth along the left wall
boss_od = 6.0; boss_id = 2.0;   // M2.5 self-tapping into PETG; use 2.2 for ASA/PLA
holes = [[55.5, 3.0], [15.75, 37.0], [55.5, 37.0]];   // H1 H2 H3, board coordinates
// ---------- heights above PCB top ----------
h_inner = 17;             // XIAO on sockets ~14 mm, relay 11.5 mm
// ---------- cutouts (board coordinates, origin = PCB top-left, x right, y down) ----------
usb_cx = 11.6;  usb_w = 12;  usb_z0 = 9.5;  usb_z1 = 17;     // XIAO USB-C, top wall (y = 0)
j1_x0 = 1.7;  j1_x1 = 9.8;                                   // J1 wire entry, bottom wall (y = pcb_y)
j3_x0 = 21.7; j3_x1 = 29.8;                                  // J3 wire entry
term_z0 = 1.0; term_z1 = 9.0;                                // terminal opening height above PCB top
ant_x = 26.0;  ant_hole = 3.2;  ant_z = 6;                   // antenna exit, top wall above the ANT pad (0 = none)
// ---------- fixing tabs ----------
tab_w = 12; tab_l = 8; tab_hole = 4.2;

$fn = 48;
ix = pcb_x + 2*clr;        // inner cavity x (between rails)
iy = pcb_y + 2*clr;        // inner cavity y
ox = ix + 2*wall;  oy = iy + 2*wall;
base_h = floor_t + rail_h + pcb_t + h_inner;   // outer height of the base (lid sits on top)
lip_h = 4;

module rbox(x, y, z, r = 1.5) {
  hull() for (sx = [r, x - r], sy = [r, y - r]) translate([sx, sy, 0]) cylinder(r = r, h = z);
}

// board coordinate -> base coordinate
function bx(x) = wall + clr + x;
function by(y) = wall + clr + y;
pcb_z = floor_t + rail_h;   // z of PCB underside

module base() {
  difference() {
    union() {
      rbox(ox, oy, base_h);
      // fixing tabs on the short sides
      for (sx = [-tab_l, ox]) translate([sx, oy/2 - tab_w/2, 0]) rbox(tab_l + 2, tab_w, floor_t + 1);
    }
    // cavity above the floor (full width between walls, rails are added back below)
    translate([wall, wall, floor_t]) rbox(ix, iy, base_h);
    // tab holes
    for (sx = [-tab_l/2 + 1, ox + tab_l/2 - 1]) translate([sx, oy/2, -1]) cylinder(d = tab_hole, h = floor_t + 3);
    // USB-C cutout, top wall (y = 0 side)
    translate([bx(usb_cx) - usb_w/2, -1, pcb_z + pcb_t + usb_z0]) cube([usb_w, wall + clr + 2, usb_z1 - usb_z0]);
    // terminal openings, bottom wall (y = pcb_y side)
    for (xr = [[j1_x0, j1_x1], [j3_x0, j3_x1]])
      translate([bx(xr[0]) - 0.5, oy - wall - 1, pcb_z + pcb_t + term_z0]) cube([xr[1] - xr[0] + 1, wall + 2, term_z1 - term_z0]);
    // antenna exit, top wall (y = 0), above the ANT pad
    if (ant_hole > 0) translate([bx(ant_x), -1, pcb_z + pcb_t + ant_z]) rotate([-90, 0, 0]) cylinder(d = ant_hole, h = wall + clr + 2);
    // lid snap grooves inside the long walls
    for (sy = [wall - 0.6, oy - wall - 0.6]) translate([ox/2 - 10, sy, base_h - lip_h + 1.2]) cube([20, 1.2, 1.2]);
  }
  // screw bosses under the board holes
  for (h = holes) translate([bx(h[0]), by(h[1]), floor_t - 0.01]) difference() {
    cylinder(d = boss_od, h = rail_h + 0.01);
    translate([0, 0, 0.8]) cylinder(d = boss_id, h = rail_h);
  }
  // support ledge along the left wall (no boss on that side)
  translate([wall, wall, floor_t]) cube([rail_d, iy, rail_h]);
  // stop ledge at the top wall
  translate([wall, wall, floor_t]) cube([ix, 1.0, rail_h]);
}

module lid() {
  difference() {
    union() {
      rbox(ox, oy, lid_t);
      translate([wall + 0.2, wall + 0.2, lid_t]) difference() {      // lip
        rbox(ix - 0.4, iy - 0.4, lip_h, 1.2);
        translate([1.6, 1.6, -1]) rbox(ix - 3.6, iy - 3.6, lip_h + 2, 0.8);
      }
    }
    // vent slots
    for (i = [0:4]) translate([ox/2 - 15 + i*7, oy/2 - 8, -1]) rbox(2, 16, lid_t + 2, 0.9);
  }
  // snap nubs on the lip (engage the wall grooves)
  for (sy = [wall + 0.2, oy - wall - 1.0]) translate([ox/2 - 10, sy, lid_t + lip_h - 1.6]) cube([20, 0.8, 1.0]);
}

// ---------- what to render ----------
part = "both";   // "base", "lid", "both" or "none"
if (part == "base" || part == "both") base();
if (part == "lid")  lid();
if (part == "both") translate([0, oy + 10, 0]) lid();
