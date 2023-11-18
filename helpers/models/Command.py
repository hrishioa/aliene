import enum
from typing import Optional, Union,List
from pydantic import BaseModel, Field

class Translation(BaseModel):
    """
    This represents a translation of a given sentence into english. 
    """
    translation:str = Field(description="This is an exact translation of the sentences into english from another language.")


class Query(BaseModel):
    """
    This represents a command chosen when the user is making a query. This can be related to general knowledge, industry insights or even trends.
    
    In this case, make sure to generate some unique keywords and sub queries that we can use to answer the query.

    Sample queries could be

    eg. What's the biggest problem facing our industry now
    eg. What's in my cupboard at the moment? I need to plan what to eat
    eg. Can you tell me the main things that've transpired over the past few days
    eg. Is the sky blue or red?
    """
    keywords: List[str] = Field(description="This represents a list of potential keywords that are relevant to the user's specific query")
    sub_queries: List[str] = Field(description="This represents a list of sub questions that need to be answered before asking this query")

class UserCommand(BaseModel):
    """
    This class represents a categorization of the question in the context into one of the possible commands avaliable. 
    
    You must make sure to respond only with the command that best matches the question and nothing else. Make sure to adhere to the requested json schema.
    """
    command: Union[
        Translation,
        Query
    ] = Field(
        description="This is the chosen command which best matches the question that the user has provided."
    )

class MaybeUserCommand(BaseModel):
    """
    This represents the result of trying to interpret the user's command. 
    """
    result: Optional[UserCommand] = Field(default=None)
    error: bool = Field(default=False)
    message: Optional[str] = Field(default=None)



