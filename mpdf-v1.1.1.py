import sys, getopt, os, glob, argparse, re
import PyPDF2

parser = argparse.ArgumentParser(description="-----Program for operations on PDF-Files-----")
group = parser.add_mutually_exclusive_group()

parser.add_argument("-m", help="merge files in directory [DEFAULT: Current]", action="store_true")
parser.add_argument("-r", type=int, help="rotate [90,180,270] degrees clockwise", choices=[90,180,270], metavar = "INT")
group.add_argument("-pall", type=str, help="(Must be first parameter) select all .pdf files of specified directory (Use double quotationmarks and don't end on backslash (delete it or add a second backslash)\n", metavar = "\"PATH\"")
group.add_argument("-pvar", type=str, help="(Must be first parameter) select multiple .pdf files (needs absolute paths, seperated by space; Not working with files beginning with '-')", metavar = "\"PATH\" \"..")
args = vars(parser.parse_args())
if not any(args.values()):
    parser.error("No arguments provided.")
args = parser.parse_args()

savestate = path = glob.glob("*.pdf")                                              #Default searchpath
counter = 0

#   Method to decide which method should be executed, based on given arguments
def optionSw(arg,x):
    switch = {
        "-pall": pathingAll,
        "-pvar": pathingVar,
        "-m": merge,
        "-r": rotate
    }
   
    f = switch.get(arg, lambda:"Should not happen")
    if (arg == "-r"):
        f(sys.argv[x+1])
    elif (arg == "-pvar" or arg == "-pall"):
        f(x+1)
    else:
        f()
    
#   Mode to select every .pdf file in given path
def pathingAll(arg): 
    global path                                                                     
    path = glob.glob(glob.escape(sys.argv[arg]) + "*.pdf")                         #Overwriting default path(s) with pointer(s) to given paths .pdf files
    if(path == []):                                                                 #Checking if .pdf files at given path are existent
        raise Exception("No .pdf files found in given directory")
        sys.exit(1)
      
#   Mode to select specific .pdf files with given absolute paths
def pathingVar(arg):
    global path, counter
    path = []                                                                       #clearing default path
    for x in range(arg, len(sys.argv)):
        if (sys.argv[x][0] == '-') :                                                #Checking if end reached (Might overhaul to allow input files to begin with "-")
            break;
        if re.search(r".pdf$", sys.argv[x]) is None:                                #regex to check if input ends with .pdf to ckeck if path is valid
            raise Exception(sys.argv[x]+" doesn't point at a .pdf adress")
            sys.exit(1)
        counter += 1                                                                #increase counter to skip iterations in main method for each given input 
        path += [sys.argv[x]]                                                       #adding .pdf pointers 
             
#  Creates a blank template on the desktop, where every scanned page gets copied into
def merge():
    n = scanPath("mergedFiles")
    output = PyPDF2.PdfFileWriter()
    for x in range(len(path)):
        mfo = PyPDF2.PdfFileReader(open(path[x],"r+b"))                             #[BUG] fo can't be closed -> would result in empty pages      (should get fixed, in case of crashes)                              
        for pn in range(mfo.numPages):                                              #Scans every page from given file and saves it into output
            output.addPage(mfo.getPage(pn)) 
    c = y = 0 
    while(42):                                                                      #Checks if y (filename-number) is identical to the pointed number in array n; if yes, try again with y+1
        if ((n == [] or c == len(n)) or y != n[c]):                                 #Lazy evaluation <3
            break
        y += 1
        c += 1   
    with open("mergedFiles"+str(y)+".pdf", "w+b") as pdfOut:
        output.write(pdfOut)
    y += 1
    
#   Rotates given files, as the name already suggests
def rotate(d):
    d = int(d)   
    n = scanPath("rotatedFile")                                                     #Scanning if rotatedx files were already created and saves the unusable numbers in array n                 
    c = y = 0                                                                       
    for x in range(len(path)):
        mfo = PyPDF2.PdfFileReader(open(path[x],"r+b"))                              #[BUG] fo can't be closed -> would result in empty pages      (should get fixed, in case of crashes) 
        output = PyPDF2.PdfFileWriter()
        for pn in range(mfo.numPages):                                              #Scans every page from given file, rotates it x degrees and saves it into output
            output.addPage(mfo.getPage(pn).rotateClockwise(d))
        while(42):                                                                  #Checks if y (the value for the filename-number) is identical to the pointed number in array n; if yes, try again with y+1
            if ((n == [] or c == len(n)) or y != n[c]):                             #Lazy evaluation <3
                break
            y += 1
            c += 1
        with open("rotatedFile"+str(y)+".pdf", "w+b") as pdfOut:
            output.write(pdfOut)
        y += 1   
 
#   subroutine to check if identical named files are already present and if yes, extracts and returns their infixed number
def scanPath(p):
    extN = []
    for x in range(len(savestate)):                                             
        if re.search(p, savestate[x]) is not None:
           s = re.sub(".pdf$",'', savestate[x][len(p):])                            #Deleting prefix p (p = merge OR rotate) and "suffix .pdf"
           try:                                                                     #Catching rare cases like "rotated123.231.pdf"
                extN += [int(s)]             
           except ValueError:
                pass
    return(extN)
        
#   Main method  
for x in range(1,(len(sys.argv))):
    if (sys.argv[x-1]=="-r" or sys.argv[x-1]=="-pall"):
        continue
    if (counter != 0):
        counter -= 1
        continue
    optionSw(sys.argv[x],x)


