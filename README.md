The file handling program performs two basic file operation in it create and delete a file.
As per the given condition the program need to get base_path as input from user and need to perform the file operations.
To store the logging of the file operation we are saving it in the file_operations.log .
we need to configure the logging first.
To save the logging we need to create a function def log() in which the logging are stored in file_operations.log.
Then two function are implemented for file operations.
def create() for file creation and def delete() for file deletion.
In def create function the file is opened in the write mode and writes this is a new file.Then the log() function is called to store the logging details.The print statement print the output.Also we use give a exception in which when there is error in creating the exception block executes.
In def delete function the created file is removed form the location and the print statement prints the output once the file is deleted.
The main() function gets the base path as input from the user.If the path dose not exists the print statement prints the path(base path) dose not exist.
At last theh two functions are called and the program is executed.


 
