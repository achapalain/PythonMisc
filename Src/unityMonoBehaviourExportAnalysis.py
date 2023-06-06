import obbinstall
from Python import common
import os

def process_dir(path, out_path):
    res = []
    searched = "m_PathID = "
    for f in common.getFiles(path, ".txt"):
        f_name = os.path.basename(f)
        with open(f, encoding="utf-8") as f_in:
            for line in f_in.readlines():
                if searched in line:
                    text = line[line.index(searched) + len(searched):].replace("\r", "").replace("\n", "")
                    id = int(text)
                    res.append((id, f_name))

    res.sort(key=lambda x: x[0])

    with open(out_path, "w", encoding="utf-8") as f_out:
        for x in res:
            f_out.write("{} - {}\n".format(x[0], x[1]))

process_dir(r"D:\Downloads\FPS-3472-1.5.2-Prod-arm-master-export\MonoBehaviour", r"d:\Documents\_Arnaud\text1.txt")
process_dir(r"D:\Downloads\FPS-3469-1.5.2-Prod-arm-master-export\MonoBehaviour", r"d:\Documents\_Arnaud\text2.txt")