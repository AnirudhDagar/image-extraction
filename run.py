import os
import re
from PIL import Image
import IPython
import glob
from math import log
import argparse
import shutil

os.system("mkdir dataset")
os.system("mkdir out")


def get_histogram_dispersion(histogram):
    log2 = lambda x:log(x)/log(2)
    
    total = len(histogram)
    counts = {}
    for item in histogram:
        counts.setdefault(item,0)
        counts[item]+=1
        
    ent = 0
    for i in counts:
        p = float(counts[i])/total
        ent-=p*log2(p)
    return -ent*log2(1/ent)
        

def main(args):
    print("PDF Data Directory: ", args.data_dir)
    for g_f in glob.glob(args.data_dir + "/*.pdf"):
        # Rename PDFs removing all special characters and spaces
        old_name = os.path.basename(g_f)
        print(f"Old Name: {old_name})
        old_name = old_name.replace(".pdf", "").replace(" ", "_")
        new_name = re.sub(r'[^\w]|^_', '', old_name)
        new_name = new_name + ".pdf"        
        new_g_f = os.path.join(args.data_dir, new_name)
        os.rename(g_f, new_g_f)
        print(f"New Name: {new_name}")
        g = new_g_f.split("/")[-1]

        os.system("rm dataset/*")
        os.system("rm out/*")
        command = (
            "convert -background white  -alpha remove -alpha off -density 200 '"
            + new_g_f
            + "'[1-" + str(args.max_page) + "]  png24:dataset/"
            + g
            + "-%04d.png"
        )
        os.system(command)
        command2 = (
            "python infer_simple.py "
            + " --cfg e2e_faster_rcnn_X-101-64x4d-FPN_1x.yaml "
            + " --output-dir out "
            + " --image-ext png "
            + " --wts model_final.pkl dataset/ > tmp 2> tmp.err"
        )
        os.system(command2)
        if not os.path.exists("out/out.csv"):
            print("No pic found for " + new_g_f)
            
            # Create a directory to copy pdf where an image could not be extracted.
            not_extracted_dir = os.path.join(os.path.dirname(args.data_dir), os.path.basename(args.data_dir) + "_Not_Extracted")
            if not os.path.exists(not_extracted_dir):
                os.mkdir(not_extracted_dir)
            print(f"Copying the pdf to {not_extracted_dir}")
            shutil.copy2(new_g_f, not_extracted_dir)
            continue
        
        best = -1e9
        for i, l in enumerate(open("out/out.csv")):
            print(i)
            f, x0, y0, x1, y1, _ = l.strip().split(";")
            original = Image.open("dataset/" + f)
            cropped_example = original.crop(
                (int(x0) - 20, int(y0) - 20, int(x1) + 20, int(y1) + 20)
            )
        
            disp = get_histogram_dispersion(cropped_example.histogram())
            if disp > best:
                best = disp
                name = args.out_dir + "/" + g + ".png"
                print("Saving ", name)
                cropped_example.save(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("data_dir", help="Dataset path with pdfs")
    parser.add_argument("out_dir", help="Output path with pngs")
    parser.add_argument("--max_page", default=20, help="Max Page")
    args = parser.parse_args()
    main(args)
