def read_line(input_file,output_file):
    try:
        with open(input_file, 'r') as file:
            lines=file.readlines()
        not_empty=[line for line in lines if line.strip()]
        with open (output_file, 'w') as outfile:
            outfile.writelines(not_empty)
        print(f"empty lines are removed from the file")
    except filenotfounderror:
        print(f"the file dose not exist")
input_file='text1.txt'
output_file='output.txt'
read_line(input_file,output_file)
