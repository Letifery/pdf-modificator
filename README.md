# pdf-modificator
A small python program to merge and rotate your .pdf files.

## Setup
To use this program, you need:
  * The python interpreter
  * PyPDF2 (use "pip install PyPDF2" on cmd if you have pip)
  
Don't forget the quotationmarks if you specify paths
  
## Argument list
m     Merge files in directory [DEFAULT: Current]
r     Rotate [90,180,270] degrees clockwise
pall  (Must be first parameter) select all .pdf files of specified directory
pvar  (Must be first parameter) select multiple .pdf files (needs absolute paths, seperated by space - Not working with files which are beginning with "-")
