
def iterable( object ):
  try:
    iter(object)
    return True
  except:
    return False
    
class Tensor:
  """Tensor represents a tensor object."""
  def __init__(self, encrypted_tensor) -> None:
    self.__encrypted_tensor = encrypted_tensor

  def __iter__(self):
    return iter(self.__encrypted_tensor)

  def data(self): return self.__encrypted_tensor
  
  def __add__(self, other_tensor ):
    """Returns the sum of self and argument provided tensors."""
    def nested_add( left, right ):
      if iterable(left) and iterable(right):
        return [
          nested_add( left_item, right_item )
          for left_item, right_item in zip(left, right)
        ]
      else:
        if type(left) == type(right):
          return left + right
        else:
          raise Exception(f"Incomptible type: {type(left)} and {type(right)}")
    return Tensor(nested_add( self, other_tensor ))

  def map(self, function ):
    def nested_map( object):
      if iterable(object) :
        return [
          nested_map(item)
          for item in object
        ]
      else:
        return function(object)
    return Tensor(nested_map( self ))

  def __str__(self) -> str:
      return str(self.__encrypted_tensor)
