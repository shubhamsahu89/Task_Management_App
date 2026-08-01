from src.tasks.dtos import TaskShema
from sqlalchemy.orm import Session
from src.tasks.models import TaskModel 
from fastapi import HTTPException
from src.users.models import UserModel

def create_task(body:TaskShema,db:Session,user:UserModel):
    data=body.model_dump()
    new_task=TaskModel(title=data["title"],
                       description=data["description"],
                       is_completed=data["is_completed"],
                       user_id=user.id
                       )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_task(db:Session,user:UserModel):
    tasks=db.query(TaskModel).filter(TaskModel.user_id==user.id).all()
    return tasks

def get_one_task(task_id:int,db:Session,user:UserModel):
    one_task=db.query(TaskModel).get(task_id)
    if not one_task:
        raise HTTPException(404,detail="Task id not incorrect")
    if one_task.user_id!=user.id:
        raise HTTPException(401,detail="you are not authorized")
    return one_task 

def update_task(body:TaskShema,task_id:int,db:Session,user:UserModel):
    one_task:TaskModel=db.query(TaskModel).get(task_id)

    if not one_task:
        raise HTTPException(404,detail="Task id incorrect")
    if one_task.user_id!=user.id:
        raise HTTPException(401,detail="you are not allowed to update this task")
    
    # one_task.title=body.title
    # one_task.description=body.description
    # one_task.is_completed=body.is_completed
    # this line is to make the update possible with just one or more key-value pair.
    body=body.model_dump()  #converted the body into dictionary
    for field,value in body.items():
        setattr(one_task,field,value)

    db.add(one_task)
    db.commit()
    db.refresh(one_task)

    return one_task

def delete_task(task_id:int,db:Session,user:UserModel):
    one_task=db.query(TaskModel).get(task_id)
    if not one_task:
        raise HTTPException(404,detail="incorrect task_id")
    if one_task.user_id!=user.id:
        raise HTTPException(401,detail="you are not allowed to delete this task")
    
    db.delete(one_task)
    db.commit()
    return None
