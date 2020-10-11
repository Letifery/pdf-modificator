import sys, getopt, os, glob, argparse, re, contextlib, ctypes
from pikepdf import Pdf, Encryption, Permissions, PasswordError

parser = argparse.ArgumentParser(description="-----Program for operations on PDF-Files-----")
group = parser.add_mutually_exclusive_group()
group.add_argument("-pall", type=str, help="(must be first parameter if used) select all .pdf files of specified directory (Use double quotationmarks and don't end on backslash (delete it or add a second backslash)\n", metavar="\"PATH\"")
group.add_argument("-pvar", type=str, help="(must be first parameter if used) select multiple .pdf files (needs absolute paths, seperated by space; Not working with files beginning with '-')", metavar="\"PATH\" \"..")
parser.add_argument("-m", help="merge .pdf files (every .pdf file in current directory, if not specified)", action='store_true')
parser.add_argument("-r", type=int, help="rotate [90,180,270] degrees clockwise (every .pdf file in current directory, if not specified)", choices=[90,180,270], metavar="INT")
parser.add_argument("-enc", help="encrypt files with password (every .pdf file in current directory, if not specified)", metavar="PASSWORD")
parser.add_argument("-dec", help="decrypt files with password (every .pdf file in current directory, if not specified)", metavar="PASSWORD")
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
        "-enc": decrypt_encrypt,
        "-dec": decrypt_encrypt,
        "-d": delete
    }
   
    f = switch.get(arg, lambda:"Should not happen")
    if (arg == "-r"):
        f(sys.argv[x+1])
    elif (arg == "-enc" or arg == "-dec"):
        f(arg, sys.argv[x+1])
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
        y,c = y+1,c+1
    resulting_pdf = Pdf.new()
    version = resulting_pdf.pdf_version
    for x in path:
        src = Pdf.open(x)
        version = max(version, src.pdf_version)
        resulting_pdf.pages.extend(src.pages)
    resulting_pdf.remove_unreferenced_resources()
    resulting_pdf.save("mergedFiles"+str(y)+".pdf", min_version=version)
    
#   Rotates every file in path
def rotate(d):
    d = int(d)   
    n = scan_path("rotatedFile")                                                            #Scanning if rotatedFilex files were already created and saves the unusable numbers in array n                 
    c = y = 0                                                                       
    for x in path:
        resulting_pdf = Pdf.open(x)
        for page in resulting_pdf.pages:
            page.Rotate = d
        while(42):                                                                          #Checks if y (the value for the filename-number) is identical to the pointed number in array n; if yes, try again with y+1
            if (n == [] or c == len(n) or y != n[c]):  
                break
            y,c = y+1,c+1
        resulting_pdf.save("rotatedFile"+str(y)+".pdf", min_version=resulting_pdf.pdf_version)
        y += 1   

#   Encrypts or decrypts selected files with given password (Yes, you could merge this function with rotate but it would be pretty inefficient and uglier)
def decrypt_encrypt(arg, pw):
    n = scan_path("encryptedFile") if arg == "-enc" else scan_path("decryptedFile")         #Scanning if encryptedFilex files were already created and saves the unusable numbers in array n                 
    c = y = 0
    d = []
    for x in range((len(path)-1),-1,-1):                                                    #Reverse order or it would mess the exception handler up
        try:
            resulting_pdf = Pdf.open(path[x], password=pw)
        except PasswordError:                                                               #deleting entries from path if wrong password or they would get deleted by the delete() subroutine
            print("Invalid Password -> "+ path[x])
            del path[x]
            continue
        while(42):                                                                          #Checks if y (the value for the filename-number) is identical to the pointed number in array n; if yes, try again with y+1
            if (n == [] or c == len(n) or y != n[c]):  
                break
            y,c = y+1,c+1
        if (arg == "-enc"):
            resulting_pdf.save("encryptedFile"+str(y)+".pdf", encryption = Encryption(user=pw, owner=pw, R=4))
        else:
            resulting_pdf.save("decryptedFile"+str(y)+".pdf")
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
def scan_path(p) -> [int]:
    extN = []
    for x in range(len(SAVESTATE)):                                                         #Checking against SAVESTATE, since path could have gotten altered with -pvar/-pall
        if re.search(p, SAVESTATE[x]) is not None:
           s = re.sub(".pdf$",'', SAVESTATE[x][len(p):])                                    #Deleting prefix p (e.g. p = mergedFiles, ...) and suffix ".pdf"
           try:                                                                             #Catching rare cases like "rotatedFile123.231.pdf"
                extN += [int(s)]             
           except ValueError:                                                               #Program will never create names like above, thus this file-index can be ignored
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
