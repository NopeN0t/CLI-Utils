from Colors.ConsoleColors import ConsoleColors as CC
print(
    f"This is debug file, Write your own code here.\n\n"
    f"Color Samples form ConsoleColors.py\n"
    f"{CC.BLACK}BLACK {CC.RED}RED {CC.GREEN}GREEN {CC.YELLOW}Yellow {CC.BLUE}BLUE {CC.PURPLE}PURPLE {CC.CYAN}CYAN {CC.RESET}RESET\n"
    f"{CC.INFO}INFO {CC.HIGHLIGHT}HIGHLIGHT\n"
    f"{CC.WARNING}Warning {CC.ERROR}Error {CC.FATAL}Fatal error")


from Functions.Image_Locator import LocateImages
print(
    LocateImages(
        [r"C:\Users\USER\Pictures\T", r"C:\Users\USER\Pictures\T\B"], True
    )
# ProcessPaths(
#     ["D:/4-Projects/CLI Utils/Scripts", "D:/4-Projects/CLI Utils/Scripts/Projects", 
#      r"C:\Users\USER\Pictures\Camera Roll\WIN_20210115_15_47_59_Pro.jpg"],
#     True)
)