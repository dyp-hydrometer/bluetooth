"""
.. module:: tilts
    :platform: Linux
    :synopsis: Uses calibration data to formulate a best fit line for the data. Might want to change to a linear line since no longer using both X and Y angles for the calculation

.. moduleauthor:: Evan Campbell
"""

import csv, math
import numpy as np
import matplotlib.pyplot as plt 

def run():
    logs = [f"log_1.0{x}.csv" for x in range(0, 9)]
    sgs = [1000 + x*10 for x in range(0,9)]
    tilts = []

    for i,log in enumerate(logs):
        data = np.genfromtxt(log, delimiter=',')
        #print(data)
        
        x_avg = sum(data[:,0])/data.shape[0]
        y_avg = sum(data[:,1])/data.shape[0]

        print(f"{log} - x average = {x_avg}, y average = {y_avg}")

        tilt = math.sqrt(math.pow(x_avg,2) + math.pow(y_avg,2))

        #print (tilt)
        print(f"{log} - tilt = sqrt(x_avg**2 + y_avg**2) = {tilt}")
        tilts.append(tilt)

    a = np.array(tilts)
    b = np.array(sgs)

    plt.figure()
    plt.plot(tilts, sgs)

    print("Final eq:")

    #ffit = np.polyfit(tilts, sgs, 2)
    #print(ffit)
    x_new = np.linspace(tilts[0], tilts[-1], num=len(tilts)*10)
    coefs = np.polynomial.polynomial.polyfit(tilts, sgs, 2)
    ffit = np.polynomial.polynomial.polyval(x_new, coefs)
    plt.plot(x_new, ffit)
    plt.show()

    print(f"{coefs[2]}*tilt^2 + ({coefs[1]})*tilt + ({coefs[0]})")

    for tilt in tilts:
        print((coefs[2]*math.pow(tilt,2)) + (coefs[1]*tilt) + (coefs[0]))
            
if __name__ == "__main__":
    run()