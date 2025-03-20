def encrypt(text,move):
    encrypted_text=""
    for char in text:
        if char.isalpha():
            move_amount=move%26
            if char.islower():
                encrypted_text+=chr(((ord(char)-ord('a')+move_amount)%26)+ord('a'))
            else:
                encrypted_text+=chr(((ord(char)-ord('A')+move_amount)%26)+ord('a'))
        else:
            encrypted_text+=char
    return encrypted_text
def encrypt_file(input_file,output_file,move):
    try:
        with open(input_file,'r')as file:
            text=file.read()
        encrypted_text=encrypt(text,move)
        with open(output_file,'w')as file:
            file.write(encrypted_text)
        print(f"File encrypted ")
    except FileNotFoundError:
        print(f"the file does not exist.")
input_file='text1.txt'
output_file='encrypted.txt'
move=3
encrypt_file(input_file,output_file,move)

def decrypt(text,move):
    decrypted_text=""
    for char in text:
        if char.isalpha():
            move_amount=move%26
            if char.islower():
                decrypted_text+=chr(((ord(char)-ord('a')-move_amount)%26)+ord('a'))
            else:
                decrypted_text+=chr(((ord(char)-ord('A')-move_amount)%26)+ord('A'))
        else:
            decrypted_text+=char
    return decrypted_text
def decrypt_file(input_file, output_file,move):
    try:
        with open(input_file, 'r') as file:
            text = file.read()
        decrypted_text = decrypt(text,move)        
        with open(output_file, 'w') as file:
            file.write(decrypted_text)        
        print(f"File decrypted")    
    except FileNotFoundError:
        print(f"The file does not exist.")
input_file='encrypted.txt'
output_file='decrypted.txt'
move=3
decrypt_file(input_file, output_file,move)




        
                
