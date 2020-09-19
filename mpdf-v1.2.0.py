import sys, getopt, os, glob, argparse, re, contextlib, ctypes
import PyPDF2

parser = argparse.ArgumentParser(description="-----Program for operations on PDF-Files-----")
group = parser.add_mutually_exclusive_group()
group.add_argument("-pall", type=str, help="(must be first parameter if used) select all .pdf files of specified directory (Use double quotationmarks and don't end on backslash (delete it or add a second backslash)\n", metavar="\"PATH\"")
group.add_argument("-pvar", type=str, help="(must be first parameter if used) select multiple .pdf files (needs absolute paths, seperated by space; Not working with files beginning with '-')", metavar="\"PATH\" \"..")
parser.add_argument("-m", help="merge files in directory [DEFAULT: Current]", action='store_true')
parser.add_argument("-r", type=int, help="rotate [90,180,270] degrees clockwise", choices=[90,180,270], metavar="INT")
parser.add_argument("-d", help="disable function to automatically delete the duplicate, unedited file(s) (Auto-Delete works only when cmd was launched as admin)", action='store_true')
args = vars(parser.parse_args())
if not any(args.values()):
    parser.error("No arguments provided.")
args = parser.parse_args()

SAVESTATE = path = glob.glob("*.pdf")                                                   #Default searchpath
counter = 0
delete_flag = 1

#   Method to decide which method should be executed, based on given arguments
def option_switch(arg,x):
    switch = {
        "-pall": pathing_all,
        "-pvar": pathing_variable,
        "-m": merge,
        "-r": rotate,
        "-d": delete
    }
   
    f = switch.get(arg, lambda:"Should not happen")
    if (arg == "-r"):
        f(sys.argv[x+1])
    elif (arg == "-pvar" or arg == "-pall"):
        f(x+1)
    elif (arg == "-d"):
        global delete_flag
        delete_flag = 0 
    else:
        f()
    
#   Mode to select every .pdf file in given path
def pathing_all(arg): 
    global path                                                                     
    path = glob.glob(glob.escape(sys.argv[arg]) + "*.pdf")                                  #Overwriting default path(s) with pointer(s) to given paths .pdf files
    if(path == []):                                                                         #Checking if .pdf files at given path are existent
        raise Exception("No .pdf files found in given directory")
        sys.exit(1)
      
#   Mode to select specific .pdf files with given absolute paths
def pathing_variable(arg):
    global path, counter
    path = []                                                                               #clearing default path
    for x in range(arg, len(sys.argv)):
        if (sys.argv[x][0] == '-') :                                                        #Checking if end reached (Might overhaul to allow input files to begin with "-")
            break;
        if re.search(r".pdf$", sys.argv[x]) is None:                                        #regex to check if input ends with .pdf to ckeck if path is valid
            raise Exception(sys.argv[x]+" doesn't point at a .pdf adress")
            sys.exit(1)
        counter += 1                                                                        #increase counter to skip iterations in main method for each given input 
        path += [sys.argv[x]]                                                               #adding .pdf pointers 
             
#  Creates a blank template on the desktop, where every scanned page gets copied into
def merge():
    n = scan_path("mergedFiles")
    c = y = 0 
    while(42):                                                                              #Checks if y (filename-number) is identical to the pointed number in array n; If yes, try again with y+1
        if (n == [] or c == len(n) or y != n[c]):                                           #Lazy evaluation <3
            break
        y += 1
        c += 1  
    with contextlib.ExitStack() as stack:
        output = PyPDF2.PdfFileMerger()
        file_objects = [stack.enter_context(open(path[x], 'r+b')) for x in range(len(path))]#Puts file_objects on the stack to avoid PyPDF2s bug (file-objects could only be closed, after content was written on the output-file)   
        for x in file_objects:
            output.append(x)
        with open("mergedFiles"+str(y)+".pdf", "w+b") as pdfOut:
            output.write(pdfOut)
    
#   Rotates every file in path
def rotate(d):
    d = int(d)   
    n = scan_path("rotatedFile")                                                            #Scanning if rotatedx files were already created and saves the unusable numbers in array n                 
    c = y = 0                                                                       
    with contextlib.ExitStack() as stack:
        file_objects = [stack.enter_context(open(path[x], 'r+b')) for x in range(len(path))]#Puts file_objects on the stack to avoid PyPDF2s bug (file-objects could only be closed, after content was written on the output-file)
        for x in range(len(path)):
            rfo = PyPDF2.PdfFileReader(file_objects[x])
            output = PyPDF2.PdfFileWriter()
            for pn in range(rfo.numPages):                                                  #Scans every page from given file, rotates it x degrees and saves it into output
                output.addPage(rfo.getPage(pn).rotateClockwise(d))
            while(42):                                                                      #Checks if y (the value for the filename-number) is identical to the pointed number in array n; if yes, try again with y+1
                if (n == [] or c == len(n) or y != n[c]):  
                    break
                y += 1
                c += 1
            with open("rotatedFile"+str(y)+".pdf", "w+b") as pdfOut:
                output.write(pdfOut)
            y += 1   
        
#   Deletes every file in path, if launched in admin-mode      
def delete():
    try:                                                                                    #Checking if program was launched as admin (Unix -> Windows)
        admin = (os.getuid() == 0)                                                          
    except AttributeError:
        admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if (admin):
        for x in range(len(path)):
            os.remove(path[x])
 
#   Subroutine to check if identical named files are already present and if yes, extracts and returns their infixed number
def scan_path(p):
    extN = []
    for x in range(len(SAVESTATE)):                                             
        if re.search(p, SAVESTATE[x]) is not None:
           s = re.sub(".pdf$",'', SAVESTATE[x][len(p):])                                    #Deleting prefix p (p = merge OR rotate) and suffix ".pdf"
           try:                                                                             #Catching rare cases like "rotated123.231.pdf"
                extN += [int(s)]             
           except ValueError:
                pass
    return(extN)
        
#   Main
for x in range(1,(len(sys.argv))):
    if (sys.argv[x-1]=="-r" or sys.argv[x-1]=="-pall"):
        continue
    if (counter != 0):
        counter -= 1
        continue
    option_switch(sys.argv[x],x)
if (delete_flag == 1):
    delete()


