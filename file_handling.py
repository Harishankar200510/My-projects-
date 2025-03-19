import os
import logging
logging.basicConfig(filename='file_operations.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')
def log(operation, path):
    logging.info(f"{operation} - {path}")
def create(base_path, filename):
        file_path = os.path.join(base_path, filename)
    try:
        with open(file_path, 'w') as f:
            f.write("This is a new file.")
        log("CREATED", file_path)
        print(f"File created: {file_path}")
    except Exception as e:
        print(f"Error creating file: {e}")
def delete(base_path, filename):
    """Delete a file in the specified base path."""
    file_path = os.path.join(base_path, filename)
    try:
        os.remove(file_path)
        log("DELETED", file_path)
        print(f"File deleted: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")
def main():
        base_path = input("Enter the base path: ")
    if not os.path.exists(base_path):
        print(f"The path {base_path} does not exist.")
        return
    filename = "example.txt"
    create(base_path, filename)  
    delete(base_path, filename)  
if __name__ == "__main__":
    main()
