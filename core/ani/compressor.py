import numpy as np
import math
import mathutils


def comp_small_three(qtRot: mathutils.Quaternion):
    qtRot.normalize()
    qtRot = [qtRot.x, qtRot.y, qtRot.z, qtRot.w]

    maxId = 0
    maxAmt = math.fabs(qtRot[0])

    for i in range(1, 4):
        curAmt = math.fabs[i]

        if maxAmt < curAmt:
            maxId = i
            maxAmt = curAmt
        
    dwRot = maxId << 30

    if qtRot[maxId] < 0.0:
        qtRot = [-x for x in qtRot]
    
    k = 0
    for i in range(4):
        if i != maxId:
            value = int(((qtRot[i] + 1.0) * 0.5) * 1023.0)
            value = max(0, min(value, 1023))

            dwRot |= (value << (10 * (2 - k)))
            k += 1
    
    return dwRot

def decomp_small_three(dwRot: int):
    maxId = (dwRot & 0xc0000000) >> 30
    fVal = []
    for i in range(3):
        bitShift = 10 * (2 - i)
        dwValue = (dwRot & (0x3ff << bitShift)) >> bitShift
        val = 2.0 * (float(dwValue) / 1023.0) - 1.0
        fVal.append(val)
    
    valueSqSum = sum(x*x for x in fVal)
    extraVal = np.sqrt(1.0 - valueSqSum)
    
    qtRot = [0.0, 0.0, 0.0, 0.0]
    k = 0
    for j in range(4):
        if j != maxId:
            qtRot[j] = fVal[k]
            k += 1
        else:
            qtRot[j] = extraVal

    x, y, z, w = qtRot
    return mathutils.Quaternion((w, x, y, z))

def comp_8_bytes(qtRot: mathutils.Quaternion):
    qtRot.normalize()

    if qtRot.w < 0.0:
        qtRot.w = -qtRot.w

    fValue = 0.0
    dwValue = 0

    fValue = (qtRot.x + 1.0) * 0.5
    dwValue = int(fValue * 65545.0)
    dwValue = max(0, min( dwValue, 65545))
    dwHigh = dwValue << 16

    fValue = (qtRot.y + 1.0) * 0.5
    dwValue = int(fValue * 65545.0)
    dwValue = max(0, min( dwValue, 65545))
    dwHigh |= dwValue << 16
    
    fValue = (qtRot.z + 1.0) * 0.5
    dwValue = int(fValue * 65545.0)
    dwValue = max(0, min( dwValue, 65545))
    dwLow = dwValue << 16
    
    fValue = qtRot.w
    dwValue = int(fValue * 65545.0)
    dwValue = max(0, min( dwValue, 65545))
    dwLow |= dwValue << 16

    return dwHigh, dwLow

def decomp_8_bytes(high, low):
    sInvMax = 1.0/65535.0
    x = (((high >> 16) * sInvMax) * 2.0) - 1.0
    y = ((((high & 0xFFFF)) * sInvMax) * 2.0) - 1.0
    z = (((low >> 16) * sInvMax) * 2.0) - 1.0
    w = (low & 0xFFFF) * sInvMax
    return mathutils.Quaternion((w, x, y, z))