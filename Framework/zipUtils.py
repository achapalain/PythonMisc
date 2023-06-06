import os, gzip, zipfile

# Copied from common.py, @cleanup needed
def zipData(pathIn, pathOut, compression=zipfile.ZIP_DEFLATED):
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    zipf = zipfile.ZipFile(pathOut, "w", compression)
    zipdir(pathIn, zipf)
    zipf.close()


def unzipBigFile(path_in, path_out=None, displayProgress=True):
    if not path_out:
        path_out = os.path.splitext(path_in)[0]
        if path_out == path_in:
            path_out = path_in + ".uncompressed"

    total_size = os.path.getsize(path_in)
    block_size = 1 << 18  # 64kB
    with gzip.open(path_in, 'rb') as f_in:
        with open(path_out, 'wb') as f_out:
            readSize = 0
            while True:
                block = f_in.read(block_size)
                if block == b'' or block == None:
                    if displayProgress:
                        print("\r", end="")
                    break
                readSize += block_size
                if displayProgress:
                    print("\rExtracted {:.2f}%".format(readSize / total_size * 100), end="")
                f_out.write(block)
    return path_out

def zipBigFile(path_in, path_out=None, displayProgress=True):
    if not path_out:
        path_out = path_in + ".compressed"

    total_size = os.path.getsize(path_in)
    block_size = 1 << 18  # 64kB
    with open(path_in, 'rb') as f_in:
        with gzip.open(path_out, 'wb') as f_out:
            readSize = 0
            while True:
                block = f_in.read(block_size)
                if block == b'' or block == None:
                    if displayProgress:
                        print("\r", end="")
                    break
                readSize += block_size
                if displayProgress:
                    print("\rCompressed {:.2f}%".format(readSize / total_size * 100), end="")
                f_out.write(block)
    return path_out
