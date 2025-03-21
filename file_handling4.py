def add_numbers(input_file,output_file):
    try:
        with open(input_file,'r') as inputfile,open(output_file,'w')as outputfile:
            for number,line in enumerate(inputfile,start=1):
                outputfile.write(f"{number}){line}")
            print(f"line number are added")
    except FileNotFoundError:
        print(f"The file was not found.")
    except Exception as e:
        print(f"An error occurred")
input_file = 'text1.txt'  
output_file = 'output.txt' 
add_numbers(input_file, output_file)

        
                
