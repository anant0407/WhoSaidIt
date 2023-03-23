import sys
def get_text(fpath)->str:
    pass

def convert(fpath, out_dir):
    pass

if __name__ == "main":
    if(len(sys.argv) < 3):
        print("Insufficient args")
        exit()
    convert(sys.argv[1], sys.argv[2])