from functions import *

def main():
    check_for_database()
    
    if len(sys.argv) > 1:
        custom_dl(sys.argv[1])
            

if __name__ == '__main__':
    main()
