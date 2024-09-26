import os

class File_Reader_Class:

    ALLOWED_EXTENSIONS = {"csv"}

    def __init__(self):
        return
    
    def check_file_validity(file):
        # Returns True if the file is valid, otherwise False and an error message
        if not (file and File_Reader_Class.allowed_file(file.filename)):
            return False, "Invalid file type"
        data = file.read().decode("utf-8")
        # print(len(data)) # In bytes

        # Check that the file is not empty
        if len(data) == 0:
            return False, "Empty file"
        
        # Check that the headers and the values are a correct format
        try:
            line_number = 1
            lines = data.split("\n")
            for line in lines:
                values = line.strip().split(",")
                if line_number == 1:
                    headers = values
                else:
                    if values == [""]: # Skip empty lines
                        continue
                    if len(headers) != len(values):
                        return False, "Headers and values do not match at line "+str(line_number)
                line_number += 1
            
            # print("Headers: ", headers)

        except:
            return False, "Invalid file format"

        return True, None

    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in File_Reader_Class.ALLOWED_EXTENSIONS
    
    def get_file_metadata(file):
        # Return the read back to the start of the file
        file.seek(0)
        data = file.read().decode("utf-8")

        line_number = 1
        lines = data.split("\n")
        # Remove empty lines
        lines = [line for line in lines if line.strip() != ""]
        for line in lines:
            values = line.strip().split(",")
            if line_number == 1:
                headers = values
            line_number += 1

        

        file.seek(0)
        return {
            "lines": line_number - 2, # Subtract 2 to remove the header and the last empty line
            "headers": headers
        }
