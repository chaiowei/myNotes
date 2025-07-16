#!/usr/bin/env python3
"""
Interactive tool for basic screw conveyor design calculations
and Sumitomo Cyclo 6000 gearmotor selection.

This script is a simplified engineering aid. It estimates the
required screw speed, torque and power based on user inputs and
recommends a Cyclo 6000 gearmotor model from a built-in table.
All calculations use rough empirical coefficients and must not
replace professional engineering design.
"""

import math
from dataclasses import dataclass


def get_float(prompt, optional=False):
    while True:
        val = input(prompt)
        if optional and val.strip() == "":
            return None
        try:
            return float(val)
        except ValueError:
            print("Please enter a number.")


def get_choice(prompt, choices):
    choices_str = "/".join(choices)
    while True:
        val = input(f"{prompt} ({choices_str}): ").strip().lower()
        if val in [c.lower() for c in choices]:
            return val
        print("Invalid choice. Choose from:", choices_str)


@dataclass
class InputParams:
    material_name: str
    bulk_density: float  # kg/m3
    repose_angle: float  # degrees
    abrasiveness: str
    flowability: str
    length: float  # m
    screw_diameter: float  # mm
    trough_type: str
    incline: float  # degrees
    capacity: float  # m3/hr
    screw_speed: float  # rpm, may be None
    hours_per_day: float
    ambient_temp: float


def collect_input():
    print("--- Material Properties ---")
    material_name = input("Material name: ")
    bulk_density = get_float("Bulk density [kg/m3]: ")
    repose_angle = get_float("Angle of repose [deg]: ")
    abrasiveness = get_choice("Abrasiveness", ["low", "medium", "high"])
    flowability = get_choice("Flowability", ["good", "fair", "poor"])

    print("\n--- Conveyor Geometry ---")
    length = get_float("Conveyor length L [m]: ")
    screw_diameter = get_float("Screw diameter D [mm]: ")
    trough_type = get_choice("Trough type", ["U", "tube"])
    incline = get_float("Incline angle theta [deg]: ")

    print("\n--- Conveying Requirements ---")
    capacity = get_float("Capacity Q [m3/hr]: ")
    screw_speed = get_float("Desired screw speed N [rpm] (leave blank for auto): ", optional=True)

    print("\n--- Operating Conditions ---")
    hours_per_day = get_float("Hours of operation per day: ")
    ambient_temp = get_float("Ambient temperature [C]: ")

    return InputParams(
        material_name,
        bulk_density,
        repose_angle,
        abrasiveness,
        flowability,
        length,
        screw_diameter,
        trough_type,
        incline,
        capacity,
        screw_speed,
        hours_per_day,
        ambient_temp,
    )


def filling_efficiency(flowability, trough_type, incline):
    base = {
        "good": 0.425,
        "fair": 0.325,
        "poor": 0.20,
    }[flowability]
    if trough_type == "tube":
        base -= 0.05
    if incline > 10:
        base *= 1 - 0.012 * (incline - 10)
        base = max(base, 0.05)
    return base


def calc_single_flight_volume(D_mm, C):
    D = D_mm / 1000  # to m
    pitch = D  # assume pitch = D
    shaft_d = 0.3 * D
    area = math.pi / 4 * (D ** 2 - shaft_d ** 2)
    V = area * pitch * C  # m3 per revolution
    return V


def calc_torque(D_mm, L_m, Q, gamma, theta_deg):
    Ke = 0.002
    K1 = 0.003
    K2 = 0.001
    T_empty = Ke * D_mm * L_m
    T_horiz = K1 * L_m * Q * gamma
    theta_rad = math.radians(theta_deg)
    T_lift = 0.0
    if theta_deg > 0:
        T_lift = K2 * Q * gamma * L_m * math.sin(theta_rad)
    return T_empty + T_horiz + T_lift


def service_factor(abrasiveness, hours, flowability):
    if abrasiveness == "low":
        sf = 1.1
    elif abrasiveness == "medium":
        sf = 1.3
    else:
        sf = 1.7
    if hours > 16:
        sf += 0.3
    elif hours > 8:
        sf += 0.1
    if flowability == "poor":
        sf += 0.1
    return sf


GEAR_DATA = [
    {"model": "C6000-XXS", "power": (0.75, 2.2), "speed": (5, 150)},
    {"model": "C6000-XS", "power": (2.2, 7.5), "speed": (3, 100)},
    {"model": "C6000-S", "power": (7.5, 22), "speed": (2, 80)},
    {"model": "C6000-M", "power": (22, 75), "speed": (1, 50)},
    {"model": "C6000-L", "power": (75, 200), "speed": (0.5, 30)},
    {"model": "C6000-XL", "power": (200, 500), "speed": (0.2, 20)},
]


def select_gearmotor(design_power, speed):
    candidates = []
    for g in GEAR_DATA:
        p_min, p_max = g["power"]
        s_min, s_max = g["speed"]
        if design_power <= p_max and s_min <= speed <= s_max:
            margin = p_max - design_power
            candidates.append((margin, g))
    candidates.sort(key=lambda x: (x[0], x[1]["power"][0]))
    return [c[1] for c in candidates[:3]]


def main():
    params = collect_input()
    C = filling_efficiency(params.flowability, params.trough_type, params.incline)
    V_pitch = calc_single_flight_volume(params.screw_diameter, C)

    N = params.screw_speed
    if N is None or V_pitch * N < params.capacity:
        N_min = params.capacity / V_pitch
        print(f"Suggested minimum screw speed: {N_min:.1f} rpm")
        N = N_min

    torque = calc_torque(
        params.screw_diameter, params.length, params.capacity, params.bulk_density, params.incline
    )
    power_req = 2 * math.pi * N * torque / (60 * 1000)
    motor_power = power_req / 0.9
    sf = service_factor(params.abrasiveness, params.hours_per_day, params.flowability)
    design_power = motor_power * sf

    gears = select_gearmotor(design_power, N)

    print("\n===== INPUT SUMMARY =====")
    print(params)

    print("\n===== CALCULATION RESULTS =====")
    print(f"Filling efficiency C: {C:.3f}")
    print(f"Single flight volume V_pitch: {V_pitch:.5f} m3/rev")
    print(f"Screw speed used N: {N:.1f} rpm")
    print(f"Total required torque: {torque:.2f} N.m")
    print(f"Motor input power (no SF): {motor_power:.2f} kW")
    print(f"Service factor chosen: {sf:.2f}")
    print(f"Design power: {design_power:.2f} kW")

    print("\n===== GEAR MOTOR SELECTION =====")
    if not gears:
        print("No matching Cyclo 6000 model found with current data.")
    else:
        primary = gears[0]
        print(f"Recommended model: {primary['model']}")
        print(
            f" Rated power range: {primary['power'][0]}-{primary['power'][1]} kW, "
            f"speed range: {primary['speed'][0]}-{primary['speed'][1]} rpm"
        )
        if len(gears) > 1:
            print("Other possible options:")
            for g in gears[1:]:
                print(
                    f" {g['model']} (power {g['power'][0]}-{g['power'][1]} kW, "
                    f"speed {g['speed'][0]}-{g['speed'][1]} rpm)"
                )

    print("\nIMPORTANT: This tool provides preliminary estimates only.\n"
          "Final design and gearmotor selection must consult official"
          " Sumitomo documentation and experienced engineers.")


if __name__ == "__main__":
    main()

