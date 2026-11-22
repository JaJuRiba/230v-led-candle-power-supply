"""DC corner screen; run with python3 check.py. SI units except where printed."""
from itertools import product

# Separate contact for the monitor: open = low; <=1 ohm closed assumed.
e = (0.998, 1.002)

def span(high, thresholds):
    trips = []
    for a, b, c, rc, v, i in product(e, e, e, (0, 1), thresholds, (-50e-9, 50e-9)):
        rt = 71500*a
        g = 1/(10000*b) + (1/(18200*c+rc) if high else 0)
        rail = v*(1+rt*g) + rt*i
        assert abs((rail-v)/rt - v*g - i) < 1e-15  # node current balance
        trips.append(rail)
    return min(trips), max(trips)

for high, normal_max in ((False, 3.078), (True, 4.605)):  # outward guard on E1 rounding
    rise = span(high, (0.396, 0.404))
    fall = span(high, (0.387, 0.400))
    assert normal_max < fall[0] <= rise[0] and rise[1] < (6.05 if high else 4.378)
    print(f'{"high" if high else "low"}: rise {rise[0]:.6f}..{rise[1]:.6f} V; release {fall[0]:.6f}..{fall[1]:.6f} V; trip clearance {rise[0]-normal_max:.6f} V')
headroom = 6.05 - 0.020 - 4.605
extra = 6.15/(71500*.998) + 6.15/(10000*.99) + 20e-6  # generous; includes fault pull-up
assert headroom >= 1.4 and .376+extra < .400
print(f'headroom {headroom:.3f} V; additional source budget {1e3*extra:.3f} mA')
print('100 uF at 6.15 V:', 0.5*100e-6*6.15**2*1000, 'mJ; 100 mA adds 1 V in',100e-6/.1*1000,'ms')
