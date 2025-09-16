# MyoBand

# New Apple Silicon chips do not support any Thalmic Labs products, including their device manager "Myo Connect." Intel and AMD chipsets (x86) do.

This is a collection of resources to utilize the Myo Band from Thalmic Labs.

Due to the nebulous nature of the Myo Band, I have compiled a list of the various packages and applications necessary for its usage.

A few key notes for any future researchers:

1. From my tests, the armband does not record at a constant cycle. In the script, there is a place to specify the Hz of the device (the number of readings it takes per second), which is not immediately imposed. Instead, the device undergoes a "warm-up" phase of approximately 2 seconds, during which it accelerates and eventually reaches its peak cycle speed. In patient data collection, this may require modifying the readings to remove the "warm-up" section of the CSV file.

2. The placement and orientation of the armband do matter. In my tests, I positioned the "top" of the armband (the section with the flashing icon) vertically, with a neutral hand posture, for consistency. The background application will guide this process, as it won't sync until the calibration point (where the device originally sat when calibration occurred) is replicated.

3. Calibration is essential. The app features a calibration function that enables users to replicate various hand motions in response to a signal. This calibration step is critical in producing accurate data readings.

4. Current versions of Python do not work with the myo-python library, which was built for Python 3.8 (when support for the package was dropped). Therefore, the latest version of Python used for any data collection should be 3.8. This is a simple fix, as all Python versions are available, and the only change necessary is to specify "Python 3.8" as the version to use in your IDE of choice (I used PyCharm for this project, which I can highly recommend).

5. The necessary DLL file must be specified as the "32-bit" option, NOT the "64-bit" (which is also present in the bin folder of the myo package). In my instance, I deleted the file titled "myo64.dll," present in the bin folder of the myo-sdk-win file, as dependency issues arose when the file was present. See the code for usage.

6. The particular IDE I used for this project, PyCharm, has a built-in feature for installing packages locally. I recommend using PyCharm for its ease of use. For reference, I installed the "myo-python" package in PyCharm, along with any others mentioned in the code of format: "import _____"

Good Luck!
