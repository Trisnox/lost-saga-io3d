import numpy as np
import mathutils


def decomp_small_three(dw_rot):
    dw_max_idx = (dw_rot & 0xc0000000) >> 30
    f_val = []
    for i in range(3):
        bit_shift = 10 * (2 - i)
        dw_value = (dw_rot & (0x3ff << bit_shift)) >> bit_shift
        val = 2.0 * (float(dw_value) / 1023.0) - 1.0
        f_val.append(val)
    
    value_sq_sum = sum(x*x for x in f_val)
    extra_val = np.sqrt(1.0 - value_sq_sum)
    
    qt_rot = [0.0, 0.0, 0.0, 0.0]
    k = 0
    for j in range(4):
        if j != dw_max_idx:
            qt_rot[j] = f_val[k]
            k += 1
        else:
            qt_rot[j] = extra_val

    x, y, z, w = qt_rot
    return mathutils.Quaternion((w, x, y, z))

def decomp_8_bytes(high, low):
    sInvMax = 1.0/65535.0
    x = (((high >> 16) * sInvMax) * 2.0) - 1.0
    y = ((((high & 0xFFFF)) * sInvMax) * 2.0) - 1.0
    z = (((low >> 16) * sInvMax) * 2.0) - 1.0
    w = (low & 0xFFFF) * sInvMax
    return mathutils.Quaternion((w, x, y, z))