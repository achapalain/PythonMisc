
path = r"C:\android-ndk-r16b\toolchains\arm-linux-androideabi-4.9\prebuilt\windows-x86_64\arm-linux-androideabi\bin\output-3552.txt"
with open(path) as f:
    i = 0
    for line in f:
        i += 1
        if i == 100:
            break
        print(i, line.replace("\n", ""))