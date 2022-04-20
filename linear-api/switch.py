from functools import partial

class Switch:
    """Switch in python"""
    def __init__(self) -> None:
        self.caller = {}
    
    def case(self, condition, function, *args, **kwargs):
        if condition in self.caller:
            raise Exception(f"SwitchError: Switch has already a case with provided value: {condition}")
        if args != () and kwargs != {}:
            print("Coucou")
            f = partial( function, *args, **kwargs )
        elif args != ():
            f = partial( function, *args )
        elif kwargs != {}:
            f = partial( function, *kwargs )
        else:
            f = partial( function )
        self.caller[condition] = f

    
    def run( self, value, **args ):
        if value not in self.caller:
            raise Exception(f"SwitchError: provided value not handle by case: {value}")
        try:
            return self.caller[value](**args)
        except TypeError as e:
            raise TypeError(f"SwitchError: Function not call with valid arguments: {e}")