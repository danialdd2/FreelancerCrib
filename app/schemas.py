from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8, max_length=15)
    user_role: str


class ChangeInfo(BaseModel):
    username: str
    email: str
    full_name: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateProjectRequest(BaseModel):
    title: str
    description: str
    budget: int = Field(gt=0)


class CreateBidRequest(BaseModel):
    price: float = Field(gt=0)
    message: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    user_role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class userresponse(BaseModel):
    id: int
    username: str
    full_name: str
    user_role: str
    created_at: datetime


class bidsresponse(BaseModel):
    id: int
    price: int
    message: str
    project_id: int


class notificationresponse(BaseModel):
    id: int
    title: str
    created_at: datetime


class ProjectsResponse(BaseModel):
    id: int
    title: str
    description: str
    budget: int
    status: str
    winner_id: int | None
    model_config = ConfigDict(from_attributes=True)


class ClientDashboardResponse(BaseModel):
    projects_created: int
    projects_completed: int
    client_open_projects: int
    active_projects: int
    total_bids: int
    rating: float


class FreelancerDashboardResponse(BaseModel):
    bids_sent: int
    pending_bids: int
    projects_won: int
    projects_completed: int
    active_projects: int
    rating: float


class CreateRatingRequest(BaseModel):
    score: int = Field(ge=1, le=10)
    comment: str
