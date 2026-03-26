import time
from typing import Annotated, Optional

from fastapi import FastAPI, Header, Request, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.params import Query, Path, Depends
from fastapi.security import OAuth2PasswordBearer

from employee import Employee
from middleware.Middleware import middleware
from model.Customer import Customer, CustomerOut
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware




customerRouter = APIRouter(prefix='/customer')



@customerRouter.get("/")
def home():
    return {"message": "Hello, FastAPI with Middleware!"}

@customerRouter.get("/sunil")
async def sayHi(q: Annotated[str, Query(max_length=5)]):
    return {"message": "Ban gaya Sunil"}


@customerRouter.post("/users")
async def createCustomer(customer: Customer):
    print("got customer call")
    return customer


@customerRouter.get("/customers/{customerId}")
async def sayHi(customerId: Annotated[str, Path(title='path', max_length=4)]):
    return {"message": "Ban gaya Sunil"}


@customerRouter.get("/cust", response_model=CustomerOut)
async def sayHi(request: Request, customer: Annotated[Customer, Query()],
                user_agent: Annotated[Optional[str], Header()] = None):
    print(jsonable_encoder(customer))
    print(customer)
    print(user_agent)
    print(request.headers)
    return customer


async def commonparams(userId: str="", user_name: str ="s"):
    return {'user id': userId, 'user name': user_name}


@customerRouter.get("/commonparams")
async def commonparams(commons: Annotated[dict, Depends(commonparams)]):
    return commons



@customerRouter.get("/employees")
async def emp(emp: Annotated[Employee, Depends()]):
    emp.name ="sunil ss"
    return emp


oautt2_bearer = OAuth2PasswordBearer(tokenUrl="token")

@customerRouter.get("/items/")
async def read_items(token: Annotated[str, Depends(oautt2_bearer)]):
    return {"token": token}






