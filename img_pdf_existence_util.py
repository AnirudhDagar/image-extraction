import os
import re
import glob
import argparse
import time

def main(args):
    missing_images = []
    total_pdfs = 0
    total_images = 0
    for g_f in glob.glob(args.data_dir + "/*.pdf"):
        total_pdfs += 1
        name = os.path.basename(g_f)

        # Check if image has been extracted already
        img_file = name + ".png"
        img_file_path = os.path.join(args.out_dir, img_file)
        if os.path.exists(img_file_path):
            total_images += 1
            continue
        else:
            print(f"{img_file} doesn't exist!")
            missing_images.append(img_file_path)

    if not os.path.exists("missing_images"): 
        os.mkdir("missing_images")
    save_missing_file = "missing_images/" + os.path.basename(args.data_dir) + ".txt"
    with open(save_missing_file, "w") as f:
        f.write(f"Total PDFs: {total_pdfs}, Total Images: {total_images}, Total Missing Images: {len(missing_images)}\n")
        f.writelines(["%s\n" % item  for item in missing_images])

    print("\n*\n"*3)
    print(f"Total PDFs: {total_pdfs}")
    print(f"Total Images: {total_images}")
    print(f"Total Missing Images: {len(missing_images)}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("data_dir", help="Dataset path with pdfs")
    parser.add_argument("out_dir", help="Output path with pngs")
    args = parser.parse_args()
    start = time.time()
    main(args)
    print("Elapsed Time: ", time.time() - start)