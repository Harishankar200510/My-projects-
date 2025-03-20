The file_handling3 program is used to remove empty lines from the given input file.And writes the content without any empty lines in a separate output.txt.To filter out all the empty line i used strip[] function which is used to remove whitespace and empty lines from the file.To check all the lines in a file i use for loop for iteration of the lines and used strip with if condition to check if there are any empty lines present in it and write the content in another file named as output.txt.Once the program is excuted successfully it prints "empty lines are removed from the file".




The program file_handling2 will read contents of two file and then merges into a single file.To accomplish this task i used function.
To read contents from the files the read function is used which opens the fiels in with open method in read mode then reads the contents.Also throws exceptions when the files didn't exsits.
To write the contents from the two file into a separate file write method is used a new file named merge.txt is created and the contents are written in it the file is also open using with open function which is used because there is no need to manually close the files onces opened.
Then the read functions are called the contents from the files are read till the end.
The write function writes the content in a single separate file.
Once the program is successfully executed it prints "content from both the files are updated in megered.text file" if there is any error in the program the program prints"error reading files".



