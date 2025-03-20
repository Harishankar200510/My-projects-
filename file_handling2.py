def read(file):
    try:
        with open(file,'r') as file:
            return file.read()
    except filenotfounderror:
        print(f"the file does not exist")
        return None
def write(file,content):
    with open(file,'w') as file:
        file.write(content)
file1='text1.txt'
file2='text2.txt'
merged_file='merge.txt'
content1=read(file1)
content2=read(file2)
if content1 is not None and content2 is not None:
    merge=content1+content2
    write(merged_file,merge)
    print(f"content from both the files are updated in megered.text file")
else:
    print("error in reading files")
    
    
