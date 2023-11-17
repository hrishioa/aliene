import enum
from pydantic import BaseModel, Field

class Translation(BaseModel):
    """
    This represents a translation of a given sentence into english. 
    """
    translation:str = Field(...,description="This is an exact translation of the sentences into english from another language.")

class Command(str,enum.Enum):
    TRANSLATE = "translate"
    QUERY = "query"

class UserCommand(BaseModel):
    """
    This is a class which represents a command by a user. There are two types of commands we support, 

    1. Translate a sentence in some other language into english
    2. Tell me something about an object 
    """
    command: Command = Field(
        default=Command.QUERY,
        description="This is a specific user query which the user wants executed on their end"
    )

    
