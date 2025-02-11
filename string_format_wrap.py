
def swrap(color: str, my_str: str) -> str:
    """
    Wraps the input string in the specified color or style formatting.

Args:
    color (str): The color or style to apply to the string.
        Supported options:
        - Colors: "green", "black", "red", "yellow", "blue", "magenta", "cyan", "white"
        - Background Colors: "black_bg", "red_bg", "green_bg", "yellow_bg", "blue_bg", 
          "magenta_bg", "cyan_bg", "white_bg"
        - Styles: "reset", "bold", "dim", "italic", "under"
    my_str (str): The string to format.

    my_str (str): The string to apply the color/style to.

    Returns:
    str: The input string wrapped in the appropriate ANSI escape codes to achieve the desired color/style.
    """
    match color:
        case "k" | "blk" | "black": 
            return "\033[30m" + my_str + "\033[0m"

        case "r" | "red": 
            return "\033[31m" + my_str + "\033[0m"

        case "g" | "green": 
            return "\033[32m" + my_str + "\033[0m"

        case "y" | "yellow": 
            return "\033[33m" + my_str + "\033[0m"

        case "b" | "blue": 
            return "\033[34m" + my_str + "\033[0m"

        case "m" | "magenta": 
            return "\033[35m" + my_str + "\033[0m"

        case "c" | "cyan": 
            return "\033[36m" + my_str + "\033[0m"

        case "w" | "white": 
            return "\033[37m" + my_str + "\033[0m"

        case "blkbg" | "black_bg":
            return "\033[40m" + my_str + "\033[0m"

        case "rbg" | "red_bg":
            return "\033[41m" + my_str + "\033[0m"

        case "gbg" | "green_bg":
            return "\033[42m" + my_str + "\033[0m"

        case "ybg" | "yellow_bg":
            return "\033[43m" + my_str + "\033[0m"

        case "blubg" | "blue_bg":
            return "\033[44m" + my_str + "\033[0m"

        case "mbg" | "magenta_bg":
            return "\033[45m" + my_str + "\033[0m"

        case "cbg" | "cyan_bg":
            return "\033[46m" + my_str + "\033[0m"

        case "wbg" | "white_bg":
            return "\033[47m" + my_str + "\033[0m"

        case "rst" | "reset": 
            return "\033[0m" + my_str + "\033[0m"
        
        case "bold" : 
            return "\033[1m" + my_str + "\033[0m"
        case "dim" : 
            return "\033[2m" + my_str + "\033[0m"
        case "italic" : 
            return "\033[3m" + my_str + "\033[0m"
        case "under" : 
            return "\033[4m" + my_str + "\033[0m"
        case _:
            raise ValueError(f"Invalid color or style: {color}. Please choose from the supported options.")

def pwrap(color: str, my_str: str) -> None: 
    print(swrap(color=color, my_str=my_str))
    

def swrap_test():
    
    print(swrap("k",      " [  k  ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))    
    print(swrap("r",      " [  r  ] \t [ERROR] The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))    
    print(swrap("g",      " [  g  ] \t [GOOD] The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("y",      " [  y  ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("b",      " [  b  ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("m",      " [  m  ] \t [SYSTEM MESSAGE] The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("c",      " [  c  ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("w",      " [  w  ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("blkbg",  " [blkbg] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("rbg",    " [ rbg ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("gbg",    " [ gbg ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("ybg",    " [ ybg ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("blubg",  " [blubg] \t [PROGRAM HEADERS] The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("mbg",    " [ mbg ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("cbg",    " [ cbg ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("wbg",    " [ wbg ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("rst",    " [ rst ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("bold",   " [bold ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("dim",    " [ dim ] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("italic", " [italic] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))
    print(swrap("under",  " [under] \t The Quick Brown Fox Jumps Over The Lazy Dog. !@#$%^&*()-=_+[]{}\\|;':"",./<>?"))

