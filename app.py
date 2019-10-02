import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path
from metpy.io import Level2File
from metpy.plots import add_timestamp
IN_PREFIX="RADAR/{}"
OUT_PREFIX="OUT/{}_sweep-{}.png"
CORE=sys.argv[1]
def save_as_image(d,nexrad):
    LAYER1=b"REF"
    LAYER2=b"VEL"
    f = Level2File(str(nexrad))
    
    # Pull data out of the file
    for sweep in range(0,21):
        try:
            print(f"rendering sweep {sweep}")
            # First item in ray is header, which has azimuth angle
            az = np.array([ray[0].az_angle for ray in f.sweeps[sweep]])

            # 5th item is a dict mapping a var name (byte string) to a tuple
            # of (header, data array)
            ref_hdr = f.sweeps[sweep][0][4][LAYER1][0]
            ref_range = np.arange(ref_hdr.num_gates) * ref_hdr.gate_width + ref_hdr.first_gate
            ref = np.array([ray[4][LAYER1][1] for ray in f.sweeps[sweep]])
            try:
                rho_hdr = f.sweeps[sweep][0][4][LAYER2][0]
                rho_range = (np.arange(rho_hdr.num_gates + 1) - 0.5) * rho_hdr.gate_width + rho_hdr.first_gate
                rho = np.array([ray[4][LAYER2][1] for ray in f.sweeps[sweep]])
            except:
                rho_hdr = f.sweeps[sweep][0][4][b"RHO"][0]
                rho_range = np.arange(rho_hdr.num_gates) * rho_hdr.gate_width + rho_hdr.first_gate
                rho = np.array([ray[4][b"RHO"][1] for ray in f.sweeps[sweep]])

            fig, axes = plt.subplots(1, 2, figsize=(15, 8))
            for var_data, var_range, ax in zip((ref, rho), (ref_range, rho_range), axes):
                # Turn into an array, then mask
                data = np.ma.array(var_data)
                data[np.isnan(data)] = np.ma.masked

                # Convert az,range to x,y
                xlocs = var_range * np.sin(np.deg2rad(az[:, np.newaxis]))
                ylocs = var_range * np.cos(np.deg2rad(az[:, np.newaxis]))

                # Plot the data
                ax.pcolormesh(xlocs, ylocs, data, cmap='viridis')
                ax.set_aspect('equal', 'datalim')
                ax.set_xlim(-275, 275)
                ax.set_ylim(-275, 275)
                add_timestamp(ax, f.dt, y=0.02, high_contrast=True)

            plt.savefig(str(d / OUT_PREFIX.format(f.dt.timestamp(),sweep)))
        except:
            print(f"sweep {sweep} failed, skipping")
def list_files(d):
   directory = d / IN_PREFIX.format("")
   for x in directory.iterdir():
       yield x

def confirm_dir(d):
    return (d / "RADAR").is_dir()

if __name__ == "__main__":
    d = Path(__file__).resolve().parent.parent / CORE
    if not confirm_dir(d):
        sys.exit(1)
    for first_file in list_files(d):
        print(f"working on {first_file}")
        save_as_image(d,first_file)
        print(f"finished working on {first_file}");
